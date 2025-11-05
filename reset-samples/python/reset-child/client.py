"""
Client script to start a financial research workflow.

Usage:
    python client.py [SYMBOL] [DEPTH]

Examples:
    python client.py
    python client.py AAPL
    python client.py TSLA deep
"""

import asyncio
import sys
from datetime import datetime
from temporalio.client import Client

from workflows import FinancialResearchWorkflow
from data_types import ResearchInput


async def main():
    """Start a financial research workflow."""
    # Parse command line arguments
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    depth = sys.argv[2] if len(sys.argv) > 2 else "deep"
    
    if depth not in ['basic', 'deep']:
        print(f"Invalid depth: {depth}. Must be 'basic' or 'deep'")
        sys.exit(1)
    
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Generate workflow ID
    timestamp = int(datetime.now().timestamp() * 1000)
    workflow_id = f"research-{symbol}-{timestamp}"
    
    print("")
    print("========================================")
    print("Starting Financial Research Workflow")
    print("========================================")
    print(f"Company Symbol: {symbol}")
    print(f"Research Depth: {depth}")
    print(f"Workflow ID:    {workflow_id}")
    print("========================================")
    print("")
    
    # Create input
    input_data: ResearchInput = {
        'company_symbol': symbol,
        'research_depth': depth,
    }
    
    # Start workflow
    handle = await client.start_workflow(
        FinancialResearchWorkflow.run,
        input_data,
        id=workflow_id,
        task_queue="reset-child-python",
    )
    
    print(f"✓ Workflow started successfully")
    print(f"  Run ID: {handle.first_execution_run_id}")
    print("")
    print("Waiting for workflow to complete...")
    print("")
    
    # Wait for result
    result = await handle.result()
    
    # Display final report
    print("")
    print("========================================")
    print("FINAL RESEARCH REPORT")
    print("========================================")
    print(f"Company:        {result['company_symbol']}")
    print(f"Timestamp:      {result['timestamp']}")
    print(f"Overall Score:  {result['weighted_overall_score']:.2f}/100")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Confidence:     {result['confidence']:.2f}%")
    print("========================================")
    print("")
    
    print("Detailed Scores:")
    print(f"  Market Analysis:  {result['results']['market']['overall_score']:.2f}/100")
    print(f"    - Market Share:      {result['results']['market']['market_share']:.2f}%")
    print(f"    - Competitive Index: {result['results']['market']['competitive_index']:.2f}/100")
    print(f"    - Growth Trend:      {result['results']['market']['growth_trend']}")
    print("")
    print(f"  Financial Metrics: {result['results']['financial']['health_score']:.2f}/100")
    print(f"    - P/E Ratio:         {result['results']['financial']['pe_ratio']:.2f}")
    print(f"    - Debt/Equity:       {result['results']['financial']['debt_to_equity']:.2f}")
    print(f"    - Revenue Growth:    {result['results']['financial']['revenue_growth_rate']:.2f}%")
    print(f"    - Profit Margin:     {result['results']['financial']['profit_margin']:.2f}%")
    print("")
    print(f"  Sentiment Analysis: {result['results']['sentiment']['confidence_score']:.2f}/100")
    print(f"    - News Sentiment:    {result['results']['sentiment']['news_sentiment']:.2f}")
    print(f"    - Social Sentiment:  {result['results']['sentiment']['social_sentiment']:.2f}")
    print(f"    - Analyst Rating:    {result['results']['sentiment']['analyst_rating']:.2f}/5")
    print(f"    - Trend:             {result['results']['sentiment']['trend_direction']}")
    print("")
    print(f"  Risk Assessment: {result['results']['risk']['overall_risk']:.2f}/100 (lower is better)")
    print(f"    - Volatility Index:  {result['results']['risk']['volatility_index']:.4f}")
    print(f"    - Sector Risk:       {result['results']['risk']['sector_risk']}")
    print(f"    - Regulatory Risk:   {result['results']['risk']['regulatory_risk']:.2f}/100")
    print("")
    
    print("")
    print("========================================")
    print("RESET POINT USAGE")
    print("========================================")
    print("You can now reset this workflow to specific points:")
    print("")
    print("1. Cascading reset (resets parent + Market + Financial children):")
    print("   temporal workflow reset \\")
    print(f"     --workflow-id {workflow_id} \\")
    print("     --reset-point after-historical-data-fetch \\")
    print("     --cascade \\")
    print('     --reason "Fixed P/E ratio calculation bug"')
    print("")
    print("   💰 Saves: ~$0.20 in API costs (skips re-fetching historical data)")
    print("   🌊 Cascades to: Market Analysis + Financial Metrics children")
    print("   ⏭️  Skips: Sentiment Analysis + Risk Assessment (no reset point)")
    print("")
    print("2. Reset after research (re-run aggregation only):")
    print("   temporal workflow reset \\")
    print(f"     --workflow-id {workflow_id} \\")
    print("     --reset-point after-research-complete \\")
    print('     --reason "Changed aggregation formula"')
    print("")
    print("   💰 Saves: ~$0.50 in API costs (child workflows not re-executed)")
    print("")
    print("3. Reset after aggregation (re-run recommendations only):")
    print("   temporal workflow reset \\")
    print(f"     --workflow-id {workflow_id} \\")
    print("     --reset-point after-aggregation \\")
    print('     --reason "Updated recommendation thresholds"')
    print("")
    print("========================================")
    print("")


if __name__ == "__main__":
    asyncio.run(main())

