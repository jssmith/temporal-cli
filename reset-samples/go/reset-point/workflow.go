package main

import (
	"context"
	"time"

	"go.temporal.io/sdk/activity"
	"go.temporal.io/sdk/workflow"
)

// OrderWorkflow demonstrates using reset points for workflow checkpointing
func OrderWorkflow(ctx workflow.Context, orderID string) (string, error) {
	logger := workflow.GetLogger(ctx)
	logger.Info("Order workflow started", "orderID", orderID)

	// Set activity options
	activityOptions := workflow.ActivityOptions{
		StartToCloseTimeout: 10 * time.Second,
	}
	ctx = workflow.WithActivityOptions(ctx, activityOptions)

	// Step 1: Validate order
	var validationResult string
	err := workflow.ExecuteActivity(ctx, ValidateOrder, orderID).Get(ctx, &validationResult)
	if err != nil {
		return "", err
	}
	logger.Info("Order validated", "result", validationResult)

	// RESET POINT: Can reset to here if payment fails
	err = ResetPoint(ctx, "after-validation")
	if err != nil {
		logger.Error("Failed to record reset point", "error", err)
		return "", err
	}
	logger.Info("Recorded reset point: after-validation")

	// Step 2: Process payment
	var paymentResult string
	err = workflow.ExecuteActivity(ctx, ProcessPayment, orderID).Get(ctx, &paymentResult)
	if err != nil {
		return "", err
	}
	logger.Info("Payment processed", "result", paymentResult)

	// RESET POINT: Can reset to here if shipping fails
	err = ResetPoint(ctx, "after-payment")
	if err != nil {
		logger.Error("Failed to record reset point", "error", err)
		return "", err
	}
	logger.Info("Recorded reset point: after-payment")

	// Step 3: Ship order
	var shippingResult string
	err = workflow.ExecuteActivity(ctx, ShipOrder, orderID).Get(ctx, &shippingResult)
	if err != nil {
		return "", err
	}
	logger.Info("Order shipped", "result", shippingResult)

	return "Order completed: " + orderID, nil
}

// ValidateOrder activity
func ValidateOrder(ctx context.Context, orderID string) (string, error) {
	activity.GetLogger(ctx).Info("Validating order", "orderID", orderID)
	// Simulate validation work
	time.Sleep(100 * time.Millisecond)
	return "Validated-" + orderID, nil
}

// ProcessPayment activity
func ProcessPayment(ctx context.Context, orderID string) (string, error) {
	activity.GetLogger(ctx).Info("Processing payment", "orderID", orderID)
	// Simulate payment processing
	time.Sleep(100 * time.Millisecond)
	return "Paid-" + orderID, nil
}

// ShipOrder activity
func ShipOrder(ctx context.Context, orderID string) (string, error) {
	activity.GetLogger(ctx).Info("Shipping order", "orderID", orderID)
	// Simulate shipping
	time.Sleep(100 * time.Millisecond)
	return "Shipped-" + orderID, nil
}
