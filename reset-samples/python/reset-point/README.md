# Workflow Reset Points - Python Example

## What This Demonstrates

- Adding reset points to a workflow
- Running a workflow with reset points
- Resetting a workflow to a named reset point using CLI
- Viewing reset point markers in workflow history

## Prerequisites

- Temporal server running: `temporal server start-dev`
- Python 3.8+
- Temporal Python SDK
- Built CLI from `/Users/jssmith/t/flex-reset/cli/temporal`

## Steps to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Worker

```bash
python main.py
```

You should see:
```
Starting worker on task queue: reset-point-python
Press Ctrl+C to stop...
```

### 3. Start a Workflow (in a new terminal)

```bash
temporal workflow start \
    --task-queue reset-point-python \
    --type OrderWorkflow \
    --workflow-id py-order-12345 \
    --input '"ORD-001"'
```

Wait for the workflow to complete (~1 second).

### 4. View Reset Points in History

```bash
temporal workflow show --workflow-id py-order-12345 | grep -A 5 "temporal-reset-point"
```

You should see MarkerRecorded events with:
```
EventType: MarkerRecorded
MarkerName: temporal-reset-point
Details: {"name": "after-validation"}
...
MarkerName: temporal-reset-point  
Details: {"name": "after-payment"}
```

### 5. Reset to a Named Point

**Important:** Use the locally built CLI with reset-point support:

```bash
/Users/jssmith/t/flex-reset/cli/temporal workflow reset \
    --workflow-id py-order-12345 \
    --reset-point after-payment \
    --reason "Retry shipping due to address error"
```

Output:
```
Found reset point "after-payment" at event ID 10
Reset successful. New run ID: abc-def-123
```

### 6. Verify Reset

```bash
# Check the workflow was reset
temporal workflow describe --workflow-id py-order-12345

# You'll see a new run ID
# The workflow re-executed from the after-payment checkpoint
```

## Reset Points in This Workflow

- **`after-validation`**: After order validation, before payment
  - Use this to retry both payment and shipping

- **`after-payment`**: After payment processed, before shipping
  - Use this when payment succeeded but shipping failed

## Understanding the Output

When you start the workflow, the logs will show:
```
Order workflow started for ORD-001
Order validated: Validated-ORD-001
Recorded reset point: after-validation
Payment processed: Paid-ORD-001
Recorded reset point: after-payment
Order shipped: Shipped-ORD-001
```

After reset to `after-payment`, only shipping runs again:
```
Order shipped: Shipped-ORD-001
```

## How It Works

✅ **WORKING SOLUTION:** This example uses **local activities** to record reset point markers in workflow history.

### The Local Activity Approach

Since the Python SDK doesn't have a direct `workflow.record_marker()` API, we use a clever workaround:

1. **Local Activity as Marker**: We execute a lightweight local activity named `"temporal-reset-point"`
2. **Creates MarkerRecorded Event**: Local activities create `MarkerRecorded` events in history with name `"core_local_activity"`
3. **CLI Finds It**: The CLI looks for these markers and extracts the reset point name from the activity result

### Implementation

```python
# reset_point_helper.py
@activity.defn(name="temporal-reset-point")
async def _reset_point_marker_activity(name: str) -> Dict[str, str]:
    """Local activity that records a reset point marker."""
    return {
        "marker_type": "temporal-reset-point",
        "name": name,
    }

async def record_reset_point(name: str) -> None:
    """Record a reset point using a local activity."""
    await workflow.execute_local_activity(
        _reset_point_marker_activity,
        name,
        start_to_close_timeout=timedelta(seconds=1),
    )
```

### Why This Works

- ✅ **No SDK Changes Needed**: Uses existing local activity APIs
- ✅ **Creates Real Markers**: `MarkerRecorded` events appear in history
- ✅ **Fast**: Local activities execute inline (no task queue delay)
- ✅ **Deterministic**: Replays correctly like any other local activity
- ✅ **Works Now**: No waiting for SDK features

### Advantages vs. Direct Marker API

While not as clean as a hypothetical `workflow.record_marker()`, this approach:
- Works with current Python SDK
- Is explicit and visible in workflow code
- Has negligible performance overhead (microseconds)
- Follows established Temporal patterns

## Common Use Cases

### Retry Failed Step

If shipping fails:
```bash
# Fix the shipping code, then reset
/Users/jssmith/t/flex-reset/cli/temporal workflow reset \
    --workflow-id py-order-12345 \
    --reset-point after-payment \
    --reason "Fixed shipping bug"
```

### Retry Multiple Steps

If both payment and shipping need retry:
```bash
/Users/jssmith/t/flex-reset/cli/temporal workflow reset \
    --workflow-id py-order-12345 \
    --reset-point after-validation \
    --reason "Retry payment and shipping"
```

## Tips

1. **Name reset points descriptively** - "after-payment" is better than "checkpoint1"
2. **Place reset points after important state changes** - after activities complete
3. **Don't overuse reset points** - only add them where you might actually need to reset
4. **Test your reset points** - verify workflows reset correctly to each point

## Next Steps

- Try the Go example: `../go/reset-point/`
- Try the TypeScript example: `../typescript/reset-point/`
- See cascading reset example: `../cascading-reset/`

