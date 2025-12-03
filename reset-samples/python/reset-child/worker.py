"""
Worker script that processes workflows and activities.

This worker handles:
- Parent workflow: FinancialResearchWorkflow
- Child workflows: MarketAnalysisChildWorkflow, FinancialMetricsChildWorkflow,
                   SentimentAnalysisChildWorkflow, RiskAssessmentChildWorkflow
- Data fetch activities: fetch_historical_data, fetch_news_data, validate_company_symbol
- Computational activities: analyze_market_metrics, calculate_financial_ratios,
                           analyze_sentiment, assess_risk
- Reset point marker activity
"""

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import all workflows, activities, and helpers
from workflows import FinancialResearchWorkflow
from child_workflows import (
    MarketAnalysisChildWorkflow,
    FinancialMetricsChildWorkflow,
    SentimentAnalysisChildWorkflow,
    RiskAssessmentChildWorkflow,
)
import activities
from reset_point_helper import _reset_point_marker_activity


async def main():
    """Run the worker."""
    # Create client to connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create and run worker
    worker = Worker(
        client,
        task_queue="reset-child-python",
        workflows=[
            FinancialResearchWorkflow,
            MarketAnalysisChildWorkflow,
            FinancialMetricsChildWorkflow,
            SentimentAnalysisChildWorkflow,
            RiskAssessmentChildWorkflow,
        ],
        activities=[
            activities.fetch_historical_data,
            activities.fetch_news_data,
            activities.validate_company_symbol,
            activities.analyze_market_metrics,
            activities.calculate_financial_ratios,
            activities.analyze_sentiment,
            activities.assess_risk,
            _reset_point_marker_activity,
        ],
    )
    
    print("========================================")
    print("Financial Research Worker Started")
    print("========================================")
    print("Task Queue: reset-child-python")
    print("Registered Workflows:")
    print("  - FinancialResearchWorkflow (parent)")
    print("  - MarketAnalysisChildWorkflow")
    print("  - FinancialMetricsChildWorkflow")
    print("  - SentimentAnalysisChildWorkflow")
    print("  - RiskAssessmentChildWorkflow")
    print("")
    print("Press Ctrl+C to stop...")
    print("========================================")
    print("")
    
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())




