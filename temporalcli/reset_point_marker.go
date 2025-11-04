package temporalcli

import (
	"context"
	"fmt"
	"sort"

	"go.temporal.io/api/enums/v1"
	"go.temporal.io/api/history/v1"
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/converter"
)

const resetPointMarkerName = "temporal-reset-point"
const resetPointNameKey = "name"
const sideEffectMarkerName = "SideEffect"
const sideEffectDataKey = "data"
const localActivityMarkerName = "core_local_activity"
const localActivityResultKey = "result"
const localActivityDataKey = "data"

// findResetPointMarker finds a reset point marker in history and returns the event ID to reset to.
// It looks for either:
// 1. Native reset point markers (marker name: "temporal-reset-point")
// 2. SideEffect markers containing reset point data (marker name: "SideEffect" with Type: "temporal-reset-point")
// 3. Local activity markers (marker name: "LocalActivity" for activity "temporal-reset-point")
func findResetPointMarker(history []*history.HistoryEvent, resetPointName string) (int64, error) {
	dc := converter.GetDefaultDataConverter()

	for _, event := range history {
		if event.GetEventType() == enums.EVENT_TYPE_MARKER_RECORDED {
			attr := event.GetMarkerRecordedEventAttributes()
			markerName := attr.GetMarkerName()

			// Check for native reset point marker
			if markerName == resetPointMarkerName {
				if namePayload, ok := attr.Details[resetPointNameKey]; ok {
					var name string
					dc.FromPayloads(namePayload, &name)

					if name == resetPointName {
						return attr.GetWorkflowTaskCompletedEventId(), nil
					}
				}
			}

			// Check for SideEffect marker with reset point data
			if markerName == sideEffectMarkerName {
				if dataPayload, ok := attr.Details[sideEffectDataKey]; ok {
					var data struct {
						Type string
						Name string
					}
					err := dc.FromPayloads(dataPayload, &data)
					if err == nil && data.Type == resetPointMarkerName && data.Name == resetPointName {
						return attr.GetWorkflowTaskCompletedEventId(), nil
					}
				}
			}

			// Check for Local Activity marker used as reset point
			if markerName == localActivityMarkerName {
				// Check if this is a reset point local activity
				// Local activities store their result in the "result" key
				if resultPayload, ok := attr.Details[localActivityResultKey]; ok {
					var result struct {
						MarkerType string `json:"marker_type"`
						Name       string `json:"name"`
					}
					err := dc.FromPayloads(resultPayload, &result)
					if err == nil && result.MarkerType == resetPointMarkerName && result.Name == resetPointName {
						return attr.GetWorkflowTaskCompletedEventId(), nil
					}
				}
			}
		}
	}

	return 0, fmt.Errorf("reset point %q not found in workflow history", resetPointName)
}

// fetchAllHistory fetches complete workflow history with pagination
func fetchAllHistory(ctx context.Context, cl client.Client, workflowID, runID string) ([]*history.HistoryEvent, error) {
	iter := cl.GetWorkflowHistory(ctx, workflowID, runID, false, enums.HISTORY_EVENT_FILTER_TYPE_ALL_EVENT)

	var events []*history.HistoryEvent
	for iter.HasNext() {
		event, err := iter.Next()
		if err != nil {
			return nil, err
		}
		events = append(events, event)
	}

	return events, nil
}

// extractChildrenBeforeEvent finds child workflows started before the given event ID
func extractChildrenBeforeEvent(history []*history.HistoryEvent, beforeEventID int64) []childRef {
	childMap := make(map[int64]*childRef)

	for _, event := range history {
		if event.EventId >= beforeEventID {
			break
		}

		switch event.EventType {
		case enums.EVENT_TYPE_START_CHILD_WORKFLOW_EXECUTION_INITIATED:
			attr := event.GetStartChildWorkflowExecutionInitiatedEventAttributes()
			childMap[event.EventId] = &childRef{
				workflowID: attr.GetWorkflowId(),
			}

		case enums.EVENT_TYPE_CHILD_WORKFLOW_EXECUTION_STARTED:
			attr := event.GetChildWorkflowExecutionStartedEventAttributes()
			if child, exists := childMap[attr.GetInitiatedEventId()]; exists {
				child.runID = attr.GetWorkflowExecution().GetRunId()
			}
		}
	}

	// Return only started children
	result := []childRef{}
	for _, child := range childMap {
		if child.runID != "" {
			result = append(result, *child)
		}
	}
	return result
}

type childRef struct {
	workflowID string
	runID      string
}

type cascadeResetPlan struct {
	resets  []resetInfo
	skipped []string
}

type resetInfo struct {
	workflowID string
	runID      string
	eventID    int64
	depth      int
}

// buildCascadingPlan recursively builds a cascading reset plan
func buildCascadingPlan(
	ctx context.Context,
	cl client.Client,
	workflowID, runID, resetPointName string,
	depth int,
) (*cascadeResetPlan, error) {
	plan := &cascadeResetPlan{}
	discoverCascade(ctx, cl, workflowID, runID, resetPointName, depth, plan)

	// Sort by depth (deepest first)
	sort.Slice(plan.resets, func(i, j int) bool {
		return plan.resets[i].depth > plan.resets[j].depth
	})

	return plan, nil
}

func discoverCascade(
	ctx context.Context,
	cl client.Client,
	workflowID, runID, resetPointName string,
	depth int,
	plan *cascadeResetPlan,
) {
	// Fetch history
	history, err := fetchAllHistory(ctx, cl, workflowID, runID)
	if err != nil {
		plan.skipped = append(plan.skipped, workflowID)
		return
	}

	// Find marker
	eventID, err := findResetPointMarker(history, resetPointName)
	if err != nil {
		plan.skipped = append(plan.skipped, workflowID)
		return
	}

	// Add to plan
	plan.resets = append(plan.resets, resetInfo{
		workflowID: workflowID,
		runID:      runID,
		eventID:    eventID,
		depth:      depth,
	})

	// Find and recurse into children
	children := extractChildrenBeforeEvent(history, eventID)
	for _, child := range children {
		discoverCascade(ctx, cl, child.workflowID, child.runID, resetPointName, depth+1, plan)
	}
}

