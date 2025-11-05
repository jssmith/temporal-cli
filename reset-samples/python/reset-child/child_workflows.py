"""
Child workflows for financial research.

Each child workflow performs specific analysis with realistic computations.
These workflows can be executed in parallel by the parent workflow.
"""

import math
from datetime import timedelta
from typing import List
from temporalio import workflow

# Import activities and types
with workflow.unsafe.imports_passed_through():
    from activities import fetch_historical_data, fetch_news_data
    from reset_point_helper import record_reset_point
    from data_types import (
        MarketAnalysisResult,
        FinancialMetricsResult,
        SentimentAnalysisResult,
        RiskAssessmentResult,
        HistoricalData,
        NewsArticle,
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
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # RESET POINT: After expensive data fetch, before computations
        # Allows cascading reset with FinancialMetrics (both use historical data)
        await record_reset_point('after-historical-data-fetch')
        
        # Calculate market share (simulated)
        market_share = _calculate_market_share(historical_data['market_cap'])
        
        # Calculate competitive positioning index
        competitive_index = _calculate_competitive_index(
            historical_data['prices'],
            historical_data['volumes']
        )
        
        # Analyze growth trend
        growth_trend = _analyze_growth_trend(historical_data['prices'])
        
        # Calculate overall market score (weighted composite)
        growth_score = 90 if growth_trend == 'accelerating' else (60 if growth_trend == 'stable' else 30)
        overall_score = (
            market_share * 0.3 +
            competitive_index * 0.4 +
            growth_score * 0.3
        )
        
        workflow.logger.info(f"[Market Analysis] Market Score: {overall_score:.2f}/100")
        
        return MarketAnalysisResult(
            market_share=market_share,
            competitive_index=competitive_index,
            growth_trend=growth_trend,
            overall_score=overall_score,
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
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # RESET POINT: After expensive data fetch, before computations
        # Allows cascading reset with MarketAnalysis (both use historical data)
        await record_reset_point('after-historical-data-fetch')
        
        # Calculate P/E ratio (Price-to-Earnings)
        pe_ratio = _calculate_pe_ratio(historical_data['prices'][-1])
        
        # Calculate debt-to-equity ratio
        debt_to_equity = _calculate_debt_to_equity(historical_data['market_cap'])
        
        # Calculate revenue growth rate (CAGR - Compound Annual Growth Rate)
        revenue_growth_rate = _calculate_cagr(historical_data['prices'])
        
        # Calculate profit margin
        profit_margin = _calculate_profit_margin(historical_data['market_cap'])
        
        # Calculate financial health score (weighted formula)
        pe_score = max(0, 100 - pe_ratio * 2)  # Lower P/E is better (capped)
        debt_score = max(0, 100 - debt_to_equity * 50)  # Lower debt is better
        growth_score = min(100, revenue_growth_rate * 5)  # Higher growth is better
        margin_score = min(100, profit_margin * 5)  # Higher margin is better
        
        health_score = (
            pe_score * 0.2 +
            debt_score * 0.3 +
            growth_score * 0.3 +
            margin_score * 0.2
        )
        
        workflow.logger.info(f"[Financial Metrics] Health Score: {health_score:.2f}/100")
        
        return FinancialMetricsResult(
            pe_ratio=pe_ratio,
            debt_to_equity=debt_to_equity,
            revenue_growth_rate=revenue_growth_rate,
            profit_margin=profit_margin,
            health_score=health_score,
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
        
        news_data = await workflow.execute_activity(
            fetch_news_data,
            company_symbol,
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # Calculate news sentiment (average of article sentiments)
        news_sentiment = _calculate_news_sentiment(news_data['articles'])
        
        # Calculate social media sentiment (simulated)
        social_sentiment = _calculate_social_sentiment(company_symbol)
        
        # Calculate analyst rating (simulated 1-5 scale)
        analyst_rating = _calculate_analyst_rating(news_data['articles'])
        
        # Analyze sentiment trend
        trend_direction = _analyze_sentiment_trend(news_data['articles'])
        
        # Calculate confidence score based on data volume and consistency
        confidence_score = _calculate_sentiment_confidence(news_data['articles'])
        
        workflow.logger.info(f"[Sentiment Analysis] Confidence Score: {confidence_score:.2f}/100")
        
        return SentimentAnalysisResult(
            news_sentiment=news_sentiment,
            social_sentiment=social_sentiment,
            analyst_rating=analyst_rating,
            trend_direction=trend_direction,
            confidence_score=confidence_score,
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
            start_to_close_timeout=timedelta(seconds=10),
        )
        
        # Calculate volatility index (standard deviation of returns)
        volatility_index = _calculate_volatility(historical_data['prices'])
        
        # Assess sector risk
        sector_risk = _assess_sector_risk(company_symbol)
        
        # Calculate regulatory risk
        regulatory_risk = _calculate_regulatory_risk(company_symbol, sector_risk)
        
        # Calculate overall risk (weighted composite, lower is better)
        volatility_risk = min(100, volatility_index * 100)
        sector_risk_score = 80 if sector_risk == 'high' else (50 if sector_risk == 'medium' else 20)
        
        overall_risk = (
            volatility_risk * 0.4 +
            sector_risk_score * 0.3 +
            regulatory_risk * 0.3
        )
        
        # Calculate risk-adjusted score (inverse of risk for consistency)
        risk_adjusted_score = 100 - overall_risk
        
        workflow.logger.info(f"[Risk Assessment] Overall Risk: {overall_risk:.2f}/100 (lower is better)")
        
        return RiskAssessmentResult(
            volatility_index=volatility_index,
            sector_risk=sector_risk,
            regulatory_risk=regulatory_risk,
            overall_risk=overall_risk,
            risk_adjusted_score=risk_adjusted_score,
        )


# ============================================================================
# Helper Functions for Computations
# ============================================================================

def _calculate_market_share(market_cap: float) -> float:
    """Simulated market share calculation based on market cap."""
    # Assuming total market is 10x this company's market cap
    return min(100, (market_cap / (market_cap * 10)) * 100 * 10)


def _calculate_competitive_index(prices: List[float], volumes: List[float]) -> float:
    """Competitive index based on price stability and volume."""
    price_stability = 100 - _calculate_volatility(prices) * 100
    volume_score = min(100, math.log10(sum(volumes)) * 10)
    return price_stability * 0.6 + volume_score * 0.4


def _analyze_growth_trend(prices: List[float]):
    """Analyze if growth is accelerating, stable, or declining."""
    if len(prices) < 3:
        return 'stable'
    
    # Calculate growth rates between consecutive periods
    growth_rates = [
        (prices[i] - prices[i-1]) / prices[i-1]
        for i in range(1, len(prices))
    ]
    
    # Check if growth is accelerating (increasing growth rates)
    mid = len(growth_rates) // 2
    avg_first_half = sum(growth_rates[:mid]) / mid
    avg_second_half = sum(growth_rates[mid:]) / (len(growth_rates) - mid)
    
    if avg_second_half > avg_first_half + 0.02:
        return 'accelerating'
    elif avg_second_half < avg_first_half - 0.02:
        return 'declining'
    return 'stable'


def _calculate_pe_ratio(current_price: float) -> float:
    """Simulated P/E ratio (Price / Earnings)."""
    # Typical P/E ratios range from 10-30 for most stocks
    simulated_earnings = current_price / (15 + workflow.random().random() * 20)
    return current_price / simulated_earnings


def _calculate_debt_to_equity(market_cap: float) -> float:
    """Simulated debt-to-equity ratio."""
    # Good companies typically have D/E < 1.0
    return 0.3 + workflow.random().random() * 0.8


def _calculate_cagr(prices: List[float]) -> float:
    """Compound Annual Growth Rate."""
    if len(prices) < 2:
        return 0
    
    beginning_value = prices[0]
    ending_value = prices[-1]
    years = len(prices) / 12  # Assuming monthly data
    
    return (math.pow(ending_value / beginning_value, 1 / years) - 1) * 100


def _calculate_profit_margin(market_cap: float) -> float:
    """Simulated profit margin (10-30% is typical for good companies)."""
    return 10 + workflow.random().random() * 20


def _calculate_news_sentiment(articles: List[NewsArticle]) -> float:
    """Average sentiment from news articles."""
    if not articles:
        return 0
    return sum(article['sentiment'] for article in articles) / len(articles)


def _calculate_social_sentiment(symbol: str) -> float:
    """Simulated social media sentiment (-1 to 1)."""
    # Using symbol hash for deterministic but varied results
    hash_value = sum(ord(char) for char in symbol)
    return math.sin(hash_value) * 0.6  # Range: -0.6 to 0.6


def _calculate_analyst_rating(articles: List[NewsArticle]) -> float:
    """Convert sentiment to 1-5 rating scale."""
    avg_sentiment = _calculate_news_sentiment(articles)
    # Map -1..1 to 1..5
    return 3 + avg_sentiment * 2


def _analyze_sentiment_trend(articles: List[NewsArticle]):
    """Analyze if sentiment is improving, stable, or declining."""
    if len(articles) < 4:
        return 'stable'
    
    mid = len(articles) // 2
    first_half = articles[:mid]
    second_half = articles[mid:]
    
    first_avg = sum(a['sentiment'] for a in first_half) / len(first_half)
    second_avg = sum(a['sentiment'] for a in second_half) / len(second_half)
    
    if second_avg > first_avg + 0.15:
        return 'improving'
    elif second_avg < first_avg - 0.15:
        return 'declining'
    return 'stable'


def _calculate_sentiment_confidence(articles: List[NewsArticle]) -> float:
    """Confidence based on volume and consistency."""
    # More articles = higher confidence
    volume_score = min(100, len(articles) * 10)
    
    # Calculate variance (lower variance = higher confidence)
    avg = _calculate_news_sentiment(articles)
    variance = sum((a['sentiment'] - avg) ** 2 for a in articles) / len(articles)
    consistency_score = max(0, 100 - variance * 100)
    
    return volume_score * 0.4 + consistency_score * 0.6


def _calculate_volatility(prices: List[float]) -> float:
    """Calculate volatility (standard deviation of returns)."""
    if len(prices) < 2:
        return 0
    
    # Calculate returns
    returns = [
        (prices[i] - prices[i-1]) / prices[i-1]
        for i in range(1, len(prices))
    ]
    
    # Calculate standard deviation of returns
    mean = sum(returns) / len(returns)
    squared_diffs = [(r - mean) ** 2 for r in returns]
    variance = sum(squared_diffs) / len(returns)
    
    return math.sqrt(variance)


def _assess_sector_risk(symbol: str):
    """Simulated sector risk based on symbol."""
    hash_value = sum(ord(char) for char in symbol)
    risk = hash_value % 3
    return 'low' if risk == 0 else ('medium' if risk == 1 else 'high')


def _calculate_regulatory_risk(symbol: str, sector_risk) -> float:
    """Regulatory risk score (0-100)."""
    base_risk = 60 if sector_risk == 'high' else (40 if sector_risk == 'medium' else 20)
    hash_value = sum(ord(char) for char in symbol)
    variation = (hash_value % 30) - 15  # -15 to +15
    return max(0, min(100, base_risk + variation))

