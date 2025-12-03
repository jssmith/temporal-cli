"""Order workflow demonstrating reset points."""
import asyncio
from datetime import timedelta
from temporalio import workflow

# Import our activities and reset point helper
with workflow.unsafe.imports_passed_through():
    from activities import validate_order, process_payment, ship_order
    from reset_point_helper import record_reset_point


@workflow.defn
class OrderWorkflow:
    """
    Demonstrates using reset points for workflow checkpointing.
    
    Reset points allow you to reset a workflow to a specific named point
    in its execution history.
    """

    @workflow.run
    async def run(self, order_id: str) -> str:
        workflow.logger.info(f"Order workflow started for {order_id}")

        # Step 1: Validate order
        validation_result = await workflow.execute_activity(
            validate_order,
            order_id,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Order validated: {validation_result}")

        # RESET POINT
        await record_reset_point("after-validation")

        # Step 2: Process payment
        payment_result = await workflow.execute_activity(
            process_payment,
            order_id,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Payment processed: {payment_result}")

        # RESET POINT
        await record_reset_point("after-payment")

        # Step 3: Ship order
        shipping_result = await workflow.execute_activity(
            ship_order,
            order_id,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Order shipped: {shipping_result}")

        return f"Order completed: {order_id}"

