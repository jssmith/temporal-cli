"""Activities for the order workflow."""
import asyncio
from temporalio import activity


@activity.defn
async def validate_order(order_id: str) -> str:
    """Validate an order."""
    activity.logger.info(f"Validating order {order_id}")
    # Simulate validation work
    await asyncio.sleep(0.1)
    return f"Validated-{order_id}"


@activity.defn
async def process_payment(order_id: str) -> str:
    """Process payment for an order."""
    activity.logger.info(f"Processing payment for {order_id}")
    # Simulate payment processing
    await asyncio.sleep(0.1)
    return f"Paid-{order_id}"


@activity.defn
async def ship_order(order_id: str) -> str:
    """Ship an order."""
    activity.logger.info(f"Shipping order {order_id}")
    # Simulate shipping
    await asyncio.sleep(0.1)
    return f"Shipped-{order_id}"

