package main

import (
	"context"
	"log"
	"time"

	"go.temporal.io/api/enums/v1"
	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"
	"go.temporal.io/sdk/workflow"
)

// TestMarkerWorkflow is a minimal workflow to test marker recording
func TestMarkerWorkflow(ctx workflow.Context) (string, error) {
	logger := workflow.GetLogger(ctx)
	logger.Info("TestMarkerWorkflow started")

	// Test 1: Use SideEffect which internally uses markers
	var sideEffectResult string
	workflow.SideEffect(ctx, func(ctx workflow.Context) interface{} {
		return "side-effect-value"
	}).Get(&sideEffectResult)
	logger.Info("SideEffect recorded", "value", sideEffectResult)

	// Test 2: Try ResetPoint
	err := ResetPoint(ctx, "test-checkpoint")
	if err != nil {
		logger.Error("ResetPoint failed", "error", err)
		return "", err
	}
	logger.Info("ResetPoint called successfully")

	return "test-completed", nil
}

func RunMarkerTest() {
	ctx := context.Background()

	// Create Temporal client
	c, err := client.Dial(client.Options{
		HostPort: "localhost:7233",
	})
	if err != nil {
		log.Fatalln("Unable to create client", err)
	}
	defer c.Close()

	taskQueue := "test-marker-queue"

	// Create worker
	w := worker.New(c, taskQueue, worker.Options{})
	w.RegisterWorkflow(TestMarkerWorkflow)

	// Start worker in a goroutine
	log.Println("Starting test worker...")
	go func() {
		err := w.Run(worker.InterruptCh())
		if err != nil {
			log.Fatalln("Unable to start worker", err)
		}
	}()

	// Give the worker a moment to start
	time.Sleep(2 * time.Second)

	// Start a workflow execution
	workflowOptions := client.StartWorkflowOptions{
		ID:        "test-marker-workflow-003",
		TaskQueue: taskQueue,
	}

	log.Println("Starting test workflow...")
	we, err := c.ExecuteWorkflow(ctx, workflowOptions, TestMarkerWorkflow)
	if err != nil {
		log.Fatalln("Unable to execute workflow", err)
	}

	log.Println("Started workflow", "WorkflowID", we.GetID(), "RunID", we.GetRunID())

	// Wait for workflow completion
	var result string
	err = we.Get(ctx, &result)
	if err != nil {
		log.Fatalln("Unable get workflow result", err)
	}

	log.Println("Workflow result:", result)
	log.Println("\n=== Checking workflow history for markers ===")

	// Get workflow history
	iter := c.GetWorkflowHistory(ctx, we.GetID(), we.GetRunID(), false, 0)
	
	markerCount := 0
	for iter.HasNext() {
		event, err := iter.Next()
		if err != nil {
			log.Fatalln("Error reading history", err)
		}
		
		eventType := event.GetEventType()
		log.Printf("Event %d: %s", event.GetEventId(), eventType.String())
		
		if eventType == enums.EVENT_TYPE_MARKER_RECORDED {
			markerAttrs := event.GetMarkerRecordedEventAttributes()
			markerName := markerAttrs.GetMarkerName()
			log.Printf("  ✓ Found MARKER: %s", markerName)
			markerCount++
		}
	}

	log.Printf("\n=== Total markers found: %d ===\n", markerCount)
	
	if markerCount == 0 {
		log.Println("⚠️  WARNING: No markers were recorded in workflow history!")
	} else {
		log.Println("✓ SUCCESS: Markers are being recorded!")
	}
}

