# Reset Point Helper - Usage Guide

This sample demonstrates how to use reset points in Temporal workflows using a simple helper function that works across all Temporal SDKs (Go, Python, TypeScript).

## How It Works

The `ResetPoint()` helper function uses `SideEffect` to record markers in the workflow history. These markers can later be used to reset the workflow to that specific point using the Temporal CLI.

## Using Reset Points in Your Workflow

```go
import (
	"go.temporal.io/sdk/workflow"
)

func MyWorkflow(ctx workflow.Context) error {
	// Do some work
	err := workflow.ExecuteActivity(ctx, Step1).Get(ctx, nil)
	if err != nil {
		return err
	}

	// Mark a reset point
	err = ResetPoint(ctx, "after-step1")
	if err != nil {
		return err
	}

	// Continue with more work
	err = workflow.ExecuteActivity(ctx, Step2).Get(ctx, nil)
	if err != nil {
		return err
	}

	return nil
}
```

## Running the Sample

```bash
# Run the order workflow example
go run .

# Run the marker test (verifies markers are recorded)
go run . test-markers
```

## Resetting a Workflow

After a workflow completes, you can reset it to any named reset point:

```bash
# Build the temporal CLI with reset point support
cd ../../../cli
go build -o temporal ./cmd/temporal

# Reset to a specific point
./temporal workflow reset \
  --workflow-id <workflow-id> \
  --reset-point <reset-point-name> \
  --reason "Reason for reset"

# Example:
./temporal workflow reset \
  --workflow-id reset-point-example-order-005 \
  --reset-point after-validation \
  --reason "Need to reprocess payment"
```

## How the Helper Works

The `ResetPoint()` helper function:
1. Uses `SideEffect` to record a marker in the workflow history
2. The marker contains metadata: `Type: "temporal-reset-point"` and `Name: "<your-name>"`
3. The CLI recognizes these markers and can reset the workflow to that point

## Porting to Other SDKs

### Python

```python
from datetime import timedelta
from typing import Dict
import temporalio.workflow as workflow
import temporalio.activity as activity

@activity.defn(name="temporal-reset-point")
async def _reset_point_marker_activity(name: str) -> Dict[str, str]:
    """Local activity that records a reset point marker."""
    return {
        "marker_type": "temporal-reset-point",
        "name": name,
    }

async def record_reset_point(name: str) -> None:
    """Record a reset point using a local activity."""
    if not name:
        raise ValueError("Reset point name cannot be empty")
    
    await workflow.execute_local_activity(
        _reset_point_marker_activity,
        name,
        start_to_close_timeout=timedelta(seconds=1),
        local_retry_threshold=timedelta(seconds=0),
    )
    
    workflow.logger.info(f"Recorded reset point: {name}")
```

### TypeScript

```typescript
import { proxyLocalActivities } from '@temporalio/workflow';

export interface ResetPointMarkerActivity {
  resetPointMarker(name: string): Promise<{ markerType: string; name: string }>;
}

export async function resetPointMarkerActivity(
  name: string
): Promise<{ markerType: string; name: string }> {
  return {
    markerType: 'temporal-reset-point',
    name,
  };
}

const { resetPointMarker } = proxyLocalActivities<ResetPointMarkerActivity>({
  startToCloseTimeout: '1s',
  localRetryThreshold: '0s',
});

export async function recordResetPoint(name: string): Promise<void> {
  if (!name) {
    throw new Error('Reset point name cannot be empty');
  }
  await resetPointMarker(name);
  console.log(`Recorded reset point: ${name}`);
}
```

Note: All SDKs use local activities to record markers since there's no public marker recording API. Local activities create MarkerRecorded events in history that the CLI can find.

## Benefits

- **No SDK modifications required** - Uses existing SDK APIs
- **Cross-SDK compatible** - Same pattern works in Go, Python, TypeScript
- **Simple to use** - Just call `ResetPoint(ctx, "name")` at key checkpoints
- **CLI integrated** - The Temporal CLI recognizes these markers automatically

## When to Use Reset Points

Use reset points when you want to:
- Rerun part of a long-running workflow without starting from the beginning
- Fix data issues by replaying from a known good state
- Test different execution paths from a checkpoint
- Recover from transient failures at specific workflow stages

