"""
Financial Research Workflow - Parent workflow demonstrating child workflows with reset points.

This workflow coordinates multiple child workflows in parallel to perform comprehensive
financial research on a company.
"""

import asyncio
from typing import List
from temporalio import workflow

# Import child workflows and types
with workflow.unsafe.imports_passed_through():
    from child_workflows import (
        MarketAnalysisChildWorkflow,
        FinancialMetricsChildWorkflow,
        SentimentAnalysisChildWorkflow,
        RiskAssessmentChildWorkflow,
    )
    from reset_point_helper import record_reset_point
    from data_types import (
        ResearchInput,
        ResearchReport,
        AggregatedResearchResults,
        InvestmentRecommendation,
        MarketAnalysisResult,
        FinancialMetricsResult,
        SentimentAnalysisResult,
        RiskAssessmentResult,
    )


@workflow.defn
class FinancialResearchWorkflow:
    """
    Parent workflow that coordinates financial research using parallel child workflows.
    
    This workflow demonstrates:
    - Parallel execution of multiple child workflows (fan-out pattern)
    - Reset points at key checkpoints to allow targeted re-execution
    - Cascading resets to selectively reset child workflows
    - Aggregation of results from multiple sources
    - Weighted scoring and recommendation generation
    
    Reset Points:
    - after-historical-data-fetch: Reset here with --cascade to reset parent + Market + Financial children
                                   (skips Sentiment + Risk, saves $0.20 in API costs)
    - after-research-complete: Reset here to re-run aggregation without re-running expensive child workflows
    - after-aggregation: Reset here to regenerate recommendations with different thresholds
    """
    
    @workflow.run
    async def run(self, input: ResearchInput) -> ResearchReport:
        company_symbol = input['company_symbol']
        research_depth = input['research_depth']
        
        workflow.logger.info("")
        workflow.logger.info("========================================")
        workflow.logger.info(f"Starting Financial Research for {company_symbol}")
        workflow.logger.info(f"Research Depth: {research_depth}")
        workflow.logger.info("========================================")
        workflow.logger.info("")
        
        start_time = workflow.now()
        
        # ============================================================================
        # Phase 1: Parallel Child Workflow Execution (Fan-Out)
        # ============================================================================
        
        workflow.logger.info("[Phase 1a] Launching historical data research workflows...")
        workflow.logger.info("  - Market Analysis")
        workflow.logger.info("  - Financial Metrics")
        workflow.logger.info("")
        
        # Execute all 4 child workflows - start all at once for true parallelism
        current_time_ms = int(workflow.now().timestamp() * 1000)
        
        market_task = workflow.execute_child_workflow(
            MarketAnalysisChildWorkflow.run,
            company_symbol,
            id=f"market-{company_symbol}-{current_time_ms}",
            task_queue="reset-child-python",
        )
        
        financial_task = workflow.execute_child_workflow(
            FinancialMetricsChildWorkflow.run,
            company_symbol,
            id=f"financial-{company_symbol}-{current_time_ms}",
            task_queue="reset-child-python",
        )
        
        sentiment_task = workflow.execute_child_workflow(
            SentimentAnalysisChildWorkflow.run,
            company_symbol,
            id=f"sentiment-{company_symbol}-{current_time_ms}",
            task_queue="reset-child-python",
        )
        
        risk_task = workflow.execute_child_workflow(
            RiskAssessmentChildWorkflow.run,
            company_symbol,
            id=f"risk-{company_symbol}-{current_time_ms}",
            task_queue="reset-child-python",
        )
        
        # Wait for historical data workflows first (Market + Financial)
        historical_results = await asyncio.gather(
            market_task,
            financial_task,
        )
        
        market_result: MarketAnalysisResult = historical_results[0]
        financial_result: FinancialMetricsResult = historical_results[1]
        
        workflow.logger.info("")
        workflow.logger.info("✓ Historical data workflows completed (Market + Financial)")
        workflow.logger.info("")
        
        # RESET POINT: After historical data workflows (Market + Financial)
        # Cascading reset here will reset parent + Market child + Financial child
        # But will NOT reset Sentiment or Risk (they don't have this reset point)
        # Saves $0.20 in API costs (avoids re-fetching historical data twice)
        await record_reset_point('after-historical-data-fetch')
        
        workflow.logger.info("[Phase 1b] Waiting for remaining research workflows...")
        workflow.logger.info("  - Sentiment Analysis")
        workflow.logger.info("  - Risk Assessment")
        workflow.logger.info("")
        
        # Wait for remaining workflows (Sentiment + Risk)
        remaining_results = await asyncio.gather(
            sentiment_task,
            risk_task,
        )
        
        sentiment_result: SentimentAnalysisResult = remaining_results[0]
        risk_result: RiskAssessmentResult = remaining_results[1]
        
        workflow.logger.info("")
        workflow.logger.info("✓ All research workflows completed")
        workflow.logger.info("")
        
        # RESET POINT: After all expensive child workflows complete
        # Reset here to re-run only aggregation and recommendations (saves API costs!)
        await record_reset_point('after-research-complete')
        
        # ============================================================================
        # Phase 2: Aggregate Results
        # ============================================================================
        
        workflow.logger.info("[Phase 2] Aggregating research results...")
        workflow.logger.info("")
        
        aggregated_results: AggregatedResearchResults = {
            'market': market_result,
            'financial': financial_result,
            'sentiment': sentiment_result,
            'risk': risk_result,
        }
        
        # Display individual scores
        workflow.logger.info("Individual Component Scores:")
        workflow.logger.info(f"  Market Score:     {market_result['overall_score']:.2f}/100")
        workflow.logger.info(f"  Financial Score:  {financial_result['health_score']:.2f}/100")
        workflow.logger.info(f"  Sentiment Score:  {sentiment_result['confidence_score']:.2f}/100")
        workflow.logger.info(f"  Risk Score:       {risk_result['overall_risk']:.2f}/100 (lower is better)")
        workflow.logger.info("")
        
        # Calculate weighted overall score
        # Weights: Market 25%, Financial 30%, Sentiment 20%, Risk 25%
        weighted_overall_score = (
            market_result['overall_score'] * 0.25 +
            financial_result['health_score'] * 0.30 +
            sentiment_result['confidence_score'] * 0.20 +
            risk_result['risk_adjusted_score'] * 0.25  # Using risk-adjusted (inverse) score
        )
        
        workflow.logger.info(f"Weighted Overall Score: {weighted_overall_score:.2f}/100")
        workflow.logger.info("")
        
        # RESET POINT: After aggregation, before recommendations
        # Reset here to regenerate recommendations with different thresholds
        await record_reset_point('after-aggregation')
        
        # ============================================================================
        # Phase 3: Generate Investment Recommendation
        # ============================================================================
        
        workflow.logger.info("[Phase 3] Generating investment recommendation...")
        workflow.logger.info("")
        
        recommendation = _generate_recommendation(
            weighted_overall_score,
            risk_result['overall_risk'],
            sentiment_result['trend_direction']
        )
        
        confidence = _calculate_confidence(
            aggregated_results,
            weighted_overall_score
        )
        
        workflow.logger.info("========================================")
        workflow.logger.info(f"RECOMMENDATION: {recommendation}")
        workflow.logger.info(f"Confidence: {confidence:.2f}%")
        workflow.logger.info("========================================")
        workflow.logger.info("")
        
        elapsed_time = (workflow.now() - start_time).total_seconds()
        workflow.logger.info(f"Research completed in {elapsed_time:.2f}s")
        workflow.logger.info("")
        
        # ============================================================================
        # Return Final Report
        # ============================================================================
        
        return ResearchReport(
            company_symbol=company_symbol,
            timestamp=workflow.now().isoformat(),
            results=aggregated_results,
            weighted_overall_score=weighted_overall_score,
            recommendation=recommendation,
            confidence=confidence,
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _generate_recommendation(
    overall_score: float,
    risk_score: float,
    sentiment_trend: str
) -> InvestmentRecommendation:
    """Generate investment recommendation based on scores and risk."""
    # Adjust score based on risk
    risk_adjusted_score = overall_score - (risk_score * 0.2)
    
    # Adjust for sentiment trend
    final_score = risk_adjusted_score
    if sentiment_trend == 'improving':
        final_score += 5
    elif sentiment_trend == 'declining':
        final_score -= 5
    
    # Generate recommendation based on final score
    if final_score >= 80:
        return 'STRONG_BUY'
    elif final_score >= 65:
        return 'BUY'
    elif final_score >= 45:
        return 'HOLD'
    elif final_score >= 30:
        return 'SELL'
    else:
        return 'STRONG_SELL'


def _calculate_confidence(
    results: AggregatedResearchResults,
    overall_score: float
) -> float:
    """Calculate confidence in the recommendation."""
    # Confidence based on:
    # 1. Consistency across metrics (lower variance = higher confidence)
    # 2. Sentiment confidence score
    # 3. Risk assessment confidence
    
    scores = [
        results['market']['overall_score'],
        results['financial']['health_score'],
        results['sentiment']['confidence_score'],
        results['risk']['risk_adjusted_score'],
    ]
    
    # Calculate variance
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    consistency_score = max(0, 100 - variance)
    
    # Weighted confidence calculation
    confidence = (
        consistency_score * 0.4 +
        results['sentiment']['confidence_score'] * 0.3 +
        (100 - results['risk']['overall_risk']) * 0.3
    )
    
    return min(100, max(0, confidence))

