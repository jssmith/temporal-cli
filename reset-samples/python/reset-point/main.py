"""Main worker script."""
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflow import OrderWorkflow
from activities import validate_order, process_payment, ship_order
from reset_point_helper import _reset_point_marker_activity


async def main():
    """Run the worker."""
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Create and run worker
    worker = Worker(
        client,
        task_queue="reset-point-python",
        workflows=[OrderWorkflow],
        activities=[
            validate_order,
            process_payment,
            ship_order,
            _reset_point_marker_activity,  # Register the reset point marker activity
        ],
    )

    print("Starting worker on task queue: reset-point-python")
    print("Press Ctrl+C to stop...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

