# Workflow Reset Points - Go Example

## What This Demonstrates

- Adding reset points to a workflow
- Running a workflow with reset points
- Resetting a workflow to a named reset point using CLI
- Viewing reset point markers in workflow history

## Prerequisites

- Temporal server running: `temporal server start-dev`
- Temporal CLI installed
- Go 1.21 or higher

## Steps to Run

### 1. Install Dependencies

```bash
go mod download
```

### 2. Start the Worker

```bash
go run .
```

You should see:
```
Starting worker on task queue: reset-point-example
```

### 3. Start a Workflow (in a new terminal)

```bash
temporal workflow start \
    --task-queue reset-point-example \
    --type OrderWorkflow \
    --workflow-id order-12345 \
    --input '"ORD-001"'
```

Wait for the workflow to complete (~1 second).

### 4. View Reset Points in History

```bash
temporal workflow show --workflow-id order-12345 | grep -A 5 "temporal-reset-point"
```

You should see MarkerRecorded events like:
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
    --workflow-id order-12345 \
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
temporal workflow describe --workflow-id order-12345

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
Order workflow started orderID=ORD-001
Validating order orderID=ORD-001
Order validated result=Validated-ORD-001
Processing payment orderID=ORD-001  
Payment processed result=Paid-ORD-001
Shipping order orderID=ORD-001
Order shipped result=Shipped-ORD-001
```

After reset to `after-payment`, only shipping runs again:
```
Shipping order orderID=ORD-001
Order shipped result=Shipped-ORD-001
```

The payment doesn't run again because we reset to AFTER payment was processed.

## Common Use Cases

### Retry Failed Step

If shipping fails:
```bash
# Fix the shipping code, then reset
temporal workflow reset \
    --workflow-id order-12345 \
    --reset-point after-payment \
    --reason "Fixed shipping bug"
```

### Retry Multiple Steps

If both payment and shipping need retry:
```bash
temporal workflow reset \
    --workflow-id order-12345 \
    --reset-point after-validation \
    --reason "Retry payment and shipping"
```

## Tips

1. **Name reset points descriptively** - "after-payment" is better than "checkpoint1"
2. **Place reset points after important state changes** - after activities complete
3. **Don't overuse reset points** - only add them where you might actually need to reset
4. **Test your reset points** - verify workflows reset correctly to each point

## Next Steps

- Try the Python example: `../python/reset-point/`
- Try the TypeScript example: `../typescript/reset-point/`  
- See cascading reset example: `../cascading-reset/`

