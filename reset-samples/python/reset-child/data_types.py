"""
Type definitions for financial research workflow.

This module contains TypedDict definitions for all data structures used
in the financial research workflow and child workflows.
"""

from typing import Literal, TypedDict, List


class ResearchInput(TypedDict):
    """Input for the financial research workflow."""
    company_symbol: str
    research_depth: Literal['basic', 'deep']


class MarketAnalysisResult(TypedDict):
    """Result from market analysis child workflow."""
    market_share: float
    competitive_index: float
    growth_trend: Literal['accelerating', 'stable', 'declining']
    overall_score: float  # Weighted composite 0-100


class FinancialMetricsResult(TypedDict):
    """Result from financial metrics child workflow."""
    pe_ratio: float
    debt_to_equity: float
    revenue_growth_rate: float
    profit_margin: float
    health_score: float  # 0-100


class SentimentAnalysisResult(TypedDict):
    """Result from sentiment analysis child workflow."""
    news_sentiment: float  # -1 to 1
    social_sentiment: float  # -1 to 1
    analyst_rating: float  # 1-5 scale
    trend_direction: Literal['improving', 'stable', 'declining']
    confidence_score: float  # 0-100


class RiskAssessmentResult(TypedDict):
    """Result from risk assessment child workflow."""
    volatility_index: float
    sector_risk: Literal['low', 'medium', 'high']
    regulatory_risk: float  # 0-100
    overall_risk: float  # 0-100 (lower is better)
    risk_adjusted_score: float  # 0-100


class AggregatedResearchResults(TypedDict):
    """Aggregated research results from all child workflows."""
    market: MarketAnalysisResult
    financial: FinancialMetricsResult
    sentiment: SentimentAnalysisResult
    risk: RiskAssessmentResult


# Investment recommendation type
InvestmentRecommendation = Literal['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL']


class ResearchReport(TypedDict, total=False):
    """Final research report."""
    company_symbol: str
    timestamp: str
    results: AggregatedResearchResults
    weighted_overall_score: float  # 0-100
    recommendation: InvestmentRecommendation
    confidence: float  # 0-100
    cost_savings: str  # Optional: For tracking API cost savings on reset


class HistoricalData(TypedDict):
    """Historical market data for analysis."""
    symbol: str
    prices: List[float]
    volumes: List[float]
    market_cap: float


class NewsArticle(TypedDict):
    """Individual news article data."""
    headline: str
    sentiment: float  # -1 to 1
    source: str


class NewsData(TypedDict):
    """News data for sentiment analysis."""
    symbol: str
    articles: List[NewsArticle]

