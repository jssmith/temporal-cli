package main

import (
	"errors"

	"go.temporal.io/sdk/workflow"
)

// ResetPoint records a named reset point marker in the workflow history.
// This marker can later be used to reset the workflow to this specific point.
//
// Note: This uses SideEffect internally to record a marker in the workflow history.
// The marker will appear in the history and can be referenced when resetting the workflow.
//
// Example usage:
//
//	err := ResetPoint(ctx, "after-validation")
//	if err != nil {
//	    return err
//	}
func ResetPoint(ctx workflow.Context, name string) error {
	if name == "" {
		return errors.New("reset point name cannot be empty")
	}

	logger := workflow.GetLogger(ctx)
	
	// Use SideEffect to record a marker with the reset point name
	// SideEffect internally creates a marker in the workflow history
	var markerData struct {
		Type string
		Name string
	}
	
	workflow.SideEffect(ctx, func(ctx workflow.Context) interface{} {
		return struct {
			Type string
			Name string
		}{
			Type: "temporal-reset-point",
			Name: name,
		}
	}).Get(&markerData)
	
	logger.Info("Reset point recorded", "name", name)
	return nil
}

