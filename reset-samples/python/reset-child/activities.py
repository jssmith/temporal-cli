"""
Supporting activities for financial research workflow.

These activities simulate external API calls for fetching market data and news.
In a real implementation, these would call services like Yahoo Finance, Alpha Vantage,
News API, etc.
"""

import asyncio
import random
import math
from typing import List
from temporalio import activity

from data_types import HistoricalData, NewsData, NewsArticle


@activity.defn
async def fetch_historical_data(company_symbol: str) -> HistoricalData:
    """
    Fetch historical market data for a company.
    
    In a real implementation, this would call external APIs like:
    - Yahoo Finance, Alpha Vantage, IEX Cloud, etc.
    - Cost: ~$0.10 per request (simulated)
    
    Args:
        company_symbol: Stock ticker symbol (e.g., "AAPL")
        
    Returns:
        HistoricalData with prices, volumes, and market cap
    """
    activity.logger.info(f"[Activity] Fetching historical data for {company_symbol}...")
    activity.logger.info("[Activity] 💰 Simulated API Cost: $0.10")
    
    # Simulate API call delay
    await asyncio.sleep(0.2)
    
    # Generate simulated historical data
    base_price = _get_base_price_for_symbol(company_symbol)
    num_months = 24  # 2 years of monthly data
    
    prices: List[float] = []
    volumes: List[float] = []
    
    for i in range(num_months):
        # Add some realistic price movement with trend
        trend = 1 + (i / num_months) * 0.3  # 30% growth over period
        volatility = (random.random() - 0.5) * 0.1  # ±5% random movement
        price = base_price * trend * (1 + volatility)
        prices.append(price)
        
        # Volume with some randomness
        base_volume = 1000000 + random.random() * 500000
        volumes.append(base_volume)
    
    # Simulated market cap
    market_cap = base_price * 10000000  # Price * shares outstanding
    
    return HistoricalData(
        symbol=company_symbol,
        prices=prices,
        volumes=volumes,
        market_cap=market_cap,
    )


@activity.defn
async def fetch_news_data(company_symbol: str) -> NewsData:
    """
    Fetch news and sentiment data for a company.
    
    In a real implementation, this would call external APIs like:
    - News API, Finnhub, Benzinga, etc.
    - Cost: ~$0.20 per request (simulated)
    
    Args:
        company_symbol: Stock ticker symbol (e.g., "AAPL")
        
    Returns:
        NewsData with articles and sentiment scores
    """
    activity.logger.info(f"[Activity] Fetching news data for {company_symbol}...")
    activity.logger.info("[Activity] 💰 Simulated API Cost: $0.20")
    
    # Simulate API call delay
    await asyncio.sleep(0.15)
    
    # Generate simulated news articles
    num_articles = 10 + int(random.random() * 10)
    articles: List[NewsArticle] = []
    
    headlines = [
        "Reports Strong Quarterly Earnings",
        "Announces New Product Launch",
        "Faces Regulatory Scrutiny",
        "Expands Into New Markets",
        "CEO Discusses Future Strategy",
        "Analyst Upgrades Rating",
        "Market Share Gains Reported",
        "Partnership Announced",
        "Challenges in Supply Chain",
        "Innovation Drives Growth",
    ]
    
    sources = [
        "Bloomberg",
        "Reuters",
        "CNBC",
        "Wall Street Journal",
        "Financial Times",
    ]
    
    for _ in range(num_articles):
        headline = random.choice(headlines)
        source = random.choice(sources)
        
        # Generate sentiment based on headline keywords
        if any(word in headline for word in ['Strong', 'Growth', 'Gains']):
            sentiment = 0.5 + random.random() * 0.4  # Positive: 0.5 to 0.9
        elif any(word in headline for word in ['Challenges', 'Scrutiny']):
            sentiment = -0.5 - random.random() * 0.4  # Negative: -0.5 to -0.9
        else:
            sentiment = (random.random() - 0.5) * 0.6  # Neutral: -0.3 to 0.3
        
        articles.append(NewsArticle(
            headline=f"{company_symbol} {headline}",
            sentiment=sentiment,
            source=source,
        ))
    
    return NewsData(
        symbol=company_symbol,
        articles=articles,
    )


@activity.defn
async def validate_company_symbol(symbol: str) -> bool:
    """
    Validate company symbol.
    
    In a real implementation, this would check against a list of valid symbols.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    activity.logger.info(f"[Activity] Validating company symbol: {symbol}")
    
    # Basic validation
    if not symbol or len(symbol) < 1 or len(symbol) > 5:
        return False
    
    # Check if all uppercase letters
    if not symbol.isupper() or not symbol.isalpha():
        return False
    
    return True


# ============================================================================
# Helper Functions
# ============================================================================

def _get_base_price_for_symbol(symbol: str) -> float:
    """
    Get base price for a symbol (deterministic but varied).
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Base price between $50 and $500
    """
    # Use symbol hash to generate deterministic but varied base price
    hash_value = sum(ord(char) for char in symbol)
    
    # Generate price between $50 and $500
    return 50 + (hash_value % 450)

