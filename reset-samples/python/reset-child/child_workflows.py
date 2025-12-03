"""
Child workflows for financial research.

Each child workflow performs specific analysis with realistic computations.
These workflows can be executed in parallel by the parent workflow.
"""

from datetime import timedelta
from temporalio import workflow

# Import activities and types
with workflow.unsafe.imports_passed_through():
    from activities import (
        fetch_historical_data,
        fetch_news_data,
        analyze_market_metrics,
        calculate_financial_ratios,
        analyze_sentiment,
        assess_risk,
    )
    from reset_point_helper import record_reset_point
    from data_types import (
        MarketAnalysisResult,
        FinancialMetricsResult,
        SentimentAnalysisResult,
        RiskAssessmentResult,
        HistoricalData,
        NewsData,
    )


@workflow.defn
class MarketAnalysisChildWorkflow:
    """
    Market Analysis Child Workflow.
    
    Analyzes market position, competitive landscape, and growth trends.
    """
    
    @workflow.run
    async def run(self, company_symbol: str) -> MarketAnalysisResult:
        workflow.logger.info(f"[Market Analysis] Starting analysis for {company_symbol}")
        
        # Fetch historical market data
        historical_data: HistoricalData = await workflow.execute_activity(
            fetch_historical_data,
            company_symbol,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # RESET POINT: After expensive data fetch, before computations
        # Allows cascading reset with FinancialMetrics (both use historical data)
        await record_reset_point('after-historical-data-fetch')
        
        # Analyze market metrics using activity
        metrics = await workflow.execute_activity(
            analyze_market_metrics,
            historical_data,
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info(f"[Market Analysis] Market Score: {metrics['overall_score']:.2f}/100")
        
        return MarketAnalysisResult(
            market_share=metrics['market_share'],
            competitive_index=metrics['competitive_index'],
            growth_trend=metrics['growth_trend'],
            overall_score=metrics['overall_score'],
        )


@workflow.defn
class FinancialMetricsChildWorkflow:
    """
    Financial Metrics Child Workflow.
    
    Calculates financial health indicators and ratios.
    """
    
    @workflow.run
    async def run(self, company_symbol: str) -> FinancialMetricsResult:
        workflow.logger.info(f"[Financial Metrics] Starting analysis for {company_symbol}")
        
        historical_data: HistoricalData = await workflow.execute_activity(
            fetch_historical_data,
            company_symbol,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # RESET POINT: After expensive data fetch, before computations
        # Allows cascading reset with MarketAnalysis (both use historical data)
        await record_reset_point('after-historical-data-fetch')
        
        # Calculate financial ratios using activity
        ratios = await workflow.execute_activity(
            calculate_financial_ratios,
            historical_data,
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info(f"[Financial Metrics] Health Score: {ratios['health_score']:.2f}/100")
        
        return FinancialMetricsResult(
            pe_ratio=ratios['pe_ratio'],
            debt_to_equity=ratios['debt_to_equity'],
            revenue_growth_rate=ratios['revenue_growth_rate'],
            profit_margin=ratios['profit_margin'],
            health_score=ratios['health_score'],
        )


@workflow.defn
class SentimentAnalysisChildWorkflow:
    """
    Sentiment Analysis Child Workflow.
    
    Analyzes news, social media, and analyst sentiment.
    """
    
    @workflow.run
    async def run(self, company_symbol: str) -> SentimentAnalysisResult:
        workflow.logger.info(f"[Sentiment Analysis] Starting analysis for {company_symbol}")
        
        news_data: NewsData = await workflow.execute_activity(
            fetch_news_data,
            company_symbol,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Analyze sentiment using activity
        sentiment = await workflow.execute_activity(
            analyze_sentiment,
            args=[news_data, company_symbol],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info(f"[Sentiment Analysis] Confidence Score: {sentiment['confidence_score']:.2f}/100")
        
        return SentimentAnalysisResult(
            news_sentiment=sentiment['news_sentiment'],
            social_sentiment=sentiment['social_sentiment'],
            analyst_rating=sentiment['analyst_rating'],
            trend_direction=sentiment['trend_direction'],
            confidence_score=sentiment['confidence_score'],
        )


@workflow.defn
class RiskAssessmentChildWorkflow:
    """
    Risk Assessment Child Workflow.
    
    Evaluates volatility, sector risks, and overall risk profile.
    """
    
    @workflow.run
    async def run(self, company_symbol: str) -> RiskAssessmentResult:
        workflow.logger.info(f"[Risk Assessment] Starting analysis for {company_symbol}")
        
        historical_data: HistoricalData = await workflow.execute_activity(
            fetch_historical_data,
            company_symbol,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Assess risk using activity
        risk = await workflow.execute_activity(
            assess_risk,
            args=[historical_data, company_symbol],
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        workflow.logger.info(f"[Risk Assessment] Overall Risk: {risk['overall_risk']:.2f}/100 (lower is better)")
        
        return RiskAssessmentResult(
            volatility_index=risk['volatility_index'],
            sector_risk=risk['sector_risk'],
            regulatory_risk=risk['regulatory_risk'],
            overall_risk=risk['overall_risk'],
            risk_adjusted_score=risk['risk_adjusted_score'],
        )

