# Workflow Reset Points - Multi-Language Examples

Reset workflows to named checkpoints instead of event IDs using markers in workflow history.

## What Are Reset Points?

Reset points are named markers in your workflow code that you can reset to:

```go
// In your workflow - records a marker in history
workflow.ResetPoint(ctx, "after-payment")

// Later, reset to it via CLI - no workflow code needed!
temporal workflow reset --workflow-id wf-123 --reset-point after-payment
```

## Quick Start

### 1. Start Temporal Server

```bash
temporal server start-dev
```

### 2. Try the Go Example

```bash
cd go/reset-point
go run .
```

In another terminal:
```bash
# Start a workflow
temporal workflow start \
    --task-queue reset-point-example \
    --type OrderWorkflow \
    --workflow-id order-12345 \
    --input '"ORD-001"'

# View reset points in history
temporal workflow show --workflow-id order-12345

# Reset to a named point
temporal workflow reset \
    --workflow-id order-12345 \
    --reset-point after-payment \
    --reason "Retry shipping"
```

## Examples

- **Go** (`go/reset-point/`) - ✅ Fully working example using SideEffect
- **Python** (`python/reset-point/`) - ✅ Fully working example using local activities
- **TypeScript** (`typescript/reset-point/`) - ✅ Fully working example using local activities

## How It Works

### Recording (SDK)

```go
workflow.ResetPoint(ctx, "checkpoint-name")
```

This records a **marker event** in workflow history:
```
EventType: MarkerRecorded
MarkerName: "temporal-reset-point"
Details: {"name": "checkpoint-name"}
WorkflowTaskCompletedEventId: 42
```

### Resetting (CLI)

```bash
temporal workflow reset --reset-point checkpoint-name --workflow-id wf-123
```

CLI:
1. Fetches workflow history
2. Finds marker with `name="checkpoint-name"`
3. Extracts `WorkflowTaskCompletedEventId` (e.g., 42)
4. Calls reset API with event ID 42

**No workflow code needed on CLI!**

## Cascading Reset

Reset entire workflow trees:

```bash
temporal workflow reset \
    --workflow-id parent-workflow \
    --reset-point checkpoint1 \
    --cascade
```

This will:
- Reset parent to `checkpoint1`
- Find all child workflows initiated before the reset point
- Reset children that also have `checkpoint1` marker
- Skip children without the marker
- Use best-effort (warns about failures, continues)

Example output:
```
Skipping 1 workflows (no reset point marker found)
Resetting 4 workflows (depth-first)...
Reset child grandchild-1 (depth 2) → run ID: xyz-1
Reset child child-1 (depth 1) → run ID: xyz-2  
Reset child child-2 (depth 1) → run ID: xyz-3
Reset parent parent-workflow → run ID: xyz-4
Successfully reset 4 out of 4 workflows
```

## Benefits

✅ **Semantic** - Names instead of event IDs  
✅ **CLI-Friendly** - No workflow code needed to reset  
✅ **Multi-Language** - Same CLI for Go/Python/TypeScript  
✅ **Visible** - Markers show in `temporal workflow show`  
✅ **Cascading** - Reset entire workflow trees  
✅ **Server-Compatible** - Works with existing Temporal servers  

## Implementation Status

### Go SDK
- ✅ `ResetPoint(ctx, name)` helper - Records markers using SideEffect
- ✅ CLI `--reset-point` flag - Finds markers and resets
- ✅ CLI `--cascade` flag - Cascading tree reset
- ✅ Complete working example

### Python SDK
- ✅ `record_reset_point(name)` helper - Records markers using local activities
- ✅ CLI `--reset-point` flag - Finds markers and resets
- ✅ CLI `--cascade` flag - Cascading tree reset
- ✅ Complete working example

### TypeScript SDK  
- ✅ `recordResetPoint(name)` helper - Records markers using local activities
- ✅ CLI `--reset-point` flag - Finds markers and resets
- ✅ CLI `--cascade` flag - Cascading tree reset
- ✅ Complete working example

## When to Use

### Good Use Cases
- After expensive operations (payment processing)
- Before error-prone operations (external API calls)
- At logical checkpoints (after validation)
- When you might need to retry from a specific point

### When NOT to Use
- Don't add reset points everywhere (only where needed)
- Not for fine-grained debugging (use normal debugging tools)
- Not as a replacement for proper error handling

## Tips

1. **Name Descriptively**: `after-payment` not `checkpoint1`
2. **Place After State Changes**: After activities complete, not before
3. **Document Your Reset Points**: Comment what each does
4. **Test Your Resets**: Verify workflows reset correctly

## Advanced

### Reset Points in Loops

```go
for i := 0; i < 10; i++ {
    doWork(i)
    if i == 5 {
        workflow.ResetPoint(ctx, "iteration-5")
    }
}
```

Only records marker on iteration 5.

### Conditional Reset Points

```go
if criticalPath {
    workflow.ResetPoint(ctx, "before-critical")
    doCriticalWork()
}
```

Marker only recorded if condition is true.

## Troubleshooting

**"Reset point not found"**
- Check spelling of reset point name
- Verify workflow actually executed to that point
- Use `temporal workflow show` to see all markers

**"Must specify workflow id"**
- Add `--workflow-id` flag

**"cannot be combined with --event-id"**
- Use either `--reset-point` OR `--event-id`, not both

## Next Steps

1. Try the Go example
2. Check markers in history: `temporal workflow show`
3. Test simple reset
4. Test cascading reset with parent/child workflows
5. Add reset points to your own workflows!

