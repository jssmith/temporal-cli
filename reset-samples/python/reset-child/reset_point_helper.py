"""
Helper to record reset point markers in workflow history using local activities.

This approach uses a local activity to create a marker in the workflow history.
Local activities execute inline and their completion creates a MarkerRecorded event,
which the CLI can find and use for reset operations.
"""

from datetime import timedelta
from typing import Dict
import temporalio.workflow as workflow
import temporalio.activity as activity


@activity.defn(name="temporal-reset-point")
async def _reset_point_marker_activity(name: str) -> Dict[str, str]:
    """
    Local activity that records a reset point marker.
    
    This activity does minimal work - it just returns the marker data.
    The important part is that its execution creates a LocalActivityMarkerRecorded
    event in the workflow history that the CLI can find.
    
    Args:
        name: The name of the reset point
        
    Returns:
        Dictionary with marker metadata
    """
    return {
        "marker_type": "temporal-reset-point",
        "name": name,
    }


async def record_reset_point(name: str) -> None:
    """
    Record a reset point marker in the workflow history using a local activity.
    
    This executes a local activity that creates a MarkerRecorded event in the
    workflow history. The CLI can find these markers by looking for local activity
    completions with the activity name "temporal-reset-point".
    
    Args:
        name: The name of the reset point marker
        
    Example:
        await record_reset_point("after-payment")
    """
    if not name:
        raise ValueError("Reset point name cannot be empty")
    
    # Execute a local activity to create the marker
    # Local activities run inline with the workflow task and create markers in history
    result = await workflow.execute_local_activity(
        _reset_point_marker_activity,
        name,
        start_to_close_timeout=timedelta(seconds=1),
        local_retry_threshold=timedelta(seconds=0),  # Don't retry
    )
    
    workflow.logger.info(f"Recorded reset point: {name}")


