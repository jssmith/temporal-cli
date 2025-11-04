package main

import (
	"context"
	"log"
	"os"
	"time"

	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"
)

func main() {
	// Check if we should run the marker test
	if len(os.Args) > 1 && os.Args[1] == "test-markers" {
		RunMarkerTest()
		return
	}

	runOrderWorkflow()
}

func runOrderWorkflow() {
	// Create Temporal client
	c, err := client.Dial(client.Options{
		HostPort: "localhost:7233",
	})
	if err != nil {
		log.Fatalln("Unable to create client", err)
	}
	defer c.Close()

	// Create worker
	w := worker.New(c, "reset-point-example", worker.Options{})

	// Register workflow and activities
	w.RegisterWorkflow(OrderWorkflow)
	w.RegisterActivity(ValidateOrder)
	w.RegisterActivity(ProcessPayment)
	w.RegisterActivity(ShipOrder)

	// Start worker in a goroutine
	log.Println("Starting worker on task queue: reset-point-example")
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
		ID:        "reset-point-example-order-005",
		TaskQueue: "reset-point-example",
	}

	log.Println("Starting workflow execution...")
	we, err := c.ExecuteWorkflow(context.Background(), workflowOptions, OrderWorkflow, "ORDER-123")
	if err != nil {
		log.Fatalln("Unable to execute workflow", err)
	}

	log.Println("Started workflow", "WorkflowID", we.GetID(), "RunID", we.GetRunID())

	// Wait for workflow completion
	var result string
	err = we.Get(context.Background(), &result)
	if err != nil {
		log.Fatalln("Unable get workflow result", err)
	}

	log.Println("Workflow result:", result)
	log.Println("\nWorkflow completed successfully!")
	log.Println("You can now reset this workflow to a specific point using:")
	log.Println("  temporal workflow reset --workflow-id", we.GetID(), "--reset-point-name after-validation")
	log.Println("  temporal workflow reset --workflow-id", we.GetID(), "--reset-point-name after-payment")
}
