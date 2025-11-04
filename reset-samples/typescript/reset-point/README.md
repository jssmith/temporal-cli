# Workflow Reset Points - TypeScript Example

## What This Demonstrates

- Adding reset points to a workflow
- Running a workflow with reset points
- Resetting a workflow to a named reset point using CLI
- Viewing reset point markers in workflow history

## Prerequisites

- Temporal server running: `temporal server start-dev`
- Temporal CLI installed
- Node.js 16+
- npm or yarn

## Steps to Run

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Worker

```bash
npm run worker
```

You should see:
```
Starting worker on task queue: reset-point-ts
Press Ctrl+C to stop...
```

### 3. Start a Workflow (in a new terminal)

```bash
temporal workflow start \
    --task-queue reset-point-ts \
    --type orderWorkflow \
    --workflow-id ts-order-12345 \
    --input '"ORD-001"'
```

Wait for the workflow to complete (~1 second).

Alternatively, use the included client script:
```bash
npm run workflow
```

### 4. View Reset Points in History

```bash
temporal workflow show --workflow-id ts-order-12345 | grep -A 5 "temporal-reset-point"
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

```bash
temporal workflow reset \
    --workflow-id ts-order-12345 \
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
temporal workflow describe --workflow-id ts-order-12345

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

The payment doesn't run again because we reset to AFTER payment was processed.

## How It Works

✅ **WORKING SOLUTION:** This example uses **local activities** to record reset point markers in workflow history.

### The Local Activity Approach

Since the TypeScript SDK doesn't have a direct `workflow.recordMarker()` API exposed, we use a clever workaround:

1. **Local Activity as Marker**: We execute a lightweight local activity named `"resetPointMarker"`
2. **Creates MarkerRecorded Event**: Local activities create `MarkerRecorded` events in history
3. **CLI Finds It**: The CLI looks for these markers and extracts the reset point name from the activity result

### Implementation

```typescript
// reset-point-helper.ts
export async function resetPointMarkerActivity(
  name: string
): Promise<{ marker_type: string; name: string }> {
  return {
    marker_type: 'temporal-reset-point',
    name,
  };
}

const { resetPointMarker } = proxyLocalActivities<ResetPointMarkerActivity>({
  startToCloseTimeout: '1s',
  localRetryThreshold: '0s',
});

export async function recordResetPoint(name: string): Promise<void> {
  await resetPointMarker(name);
  console.log(`Recorded reset point: ${name}`);
}
```

### Why This Works

- ✅ **No SDK Changes Needed**: Uses existing local activity APIs
- ✅ **Creates Real Markers**: `MarkerRecorded` events appear in history
- ✅ **Fast**: Local activities execute inline (no task queue delay)
- ✅ **Deterministic**: Replays correctly like any other local activity
- ✅ **Works Now**: No waiting for SDK features

### Important: Field Naming Convention

**⚠️ Use snake_case for field names!** The CLI expects `marker_type` (with underscore), not `markerType` (camelCase):

```typescript
return {
  marker_type: 'temporal-reset-point',  // ✅ Correct: snake_case
  name,
};

// ❌ Wrong: markerType (camelCase) - CLI won't find it!
```

This is because the Go CLI uses JSON deserialization with snake_case field names.

### Advantages vs. Direct Marker API

While not as clean as a hypothetical `workflow.recordMarker()`, this approach:
- Works with current TypeScript SDK
- Is explicit and visible in workflow code
- Has negligible performance overhead (microseconds)
- Follows established Temporal patterns

## Common Use Cases

### Retry Failed Step

If shipping fails:
```bash
# Fix the shipping code, then reset
temporal workflow reset \
    --workflow-id ts-order-12345 \
    --reset-point after-payment \
    --reason "Fixed shipping bug"
```

### Retry Multiple Steps

If both payment and shipping need retry:
```bash
temporal workflow reset \
    --workflow-id ts-order-12345 \
    --reset-point after-validation \
    --reason "Retry payment and shipping"
```

## Tips

1. **Name reset points descriptively** - "after-payment" is better than "checkpoint1"
2. **Place reset points after important state changes** - after activities complete
3. **Don't overuse reset points** - only add them where you might actually need to reset
4. **Test your reset points** - verify workflows reset correctly to each point

## Development

### Build the Project

```bash
npm run build
```

### Watch Mode (for development)

```bash
npm run start.watch
```

## Next Steps

- Try the Go example: `../go/reset-point/`
- Try the Python example: `../python/reset-point/`
- See cascading reset example: `../cascading-reset/`

## Same Markers, Same CLI, Different Language!

All three SDK examples (Go, Python, TypeScript) use the same approach:
- Record markers in workflow history
- Use the same CLI commands to reset
- Same workflow patterns across languages
