/**
 * Supporting activities for financial research workflow
 */

import type { HistoricalData, NewsData } from './types';

/**
 * Fetch historical market data for a company
 * 
 * In a real implementation, this would call external APIs like:
 * - Yahoo Finance, Alpha Vantage, IEX Cloud, etc.
 * - Cost: ~$0.10 per request (simulated)
 */
export async function fetchHistoricalData(companySymbol: string): Promise<HistoricalData> {
  console.log(`[Activity] Fetching historical data for ${companySymbol}...`);
  console.log(`[Activity] 💰 Simulated API Cost: $0.10`);
  
  // Simulate API call delay
  await new Promise((resolve) => setTimeout(resolve, 200));

  // Generate simulated historical data
  const basePrice = getBasePriceForSymbol(companySymbol);
  const numMonths = 24; // 2 years of monthly data

  const prices: number[] = [];
  const volumes: number[] = [];

  for (let i = 0; i < numMonths; i++) {
    // Add some realistic price movement with trend
    const trend = 1 + (i / numMonths) * 0.3; // 30% growth over period
    const volatility = (Math.random() - 0.5) * 0.1; // ±5% random movement
    const price = basePrice * trend * (1 + volatility);
    prices.push(price);

    // Volume with some randomness
    const baseVolume = 1000000 + Math.random() * 500000;
    volumes.push(baseVolume);
  }

  // Simulated market cap
  const marketCap = basePrice * 10000000; // Price * shares outstanding

  return {
    symbol: companySymbol,
    prices,
    volumes,
    marketCap,
  };
}

/**
 * Fetch news and sentiment data for a company
 * 
 * In a real implementation, this would call external APIs like:
 * - News API, Finnhub, Benzinga, etc.
 * - Cost: ~$0.20 per request (simulated)
 */
export async function fetchNewsData(companySymbol: string): Promise<NewsData> {
  console.log(`[Activity] Fetching news data for ${companySymbol}...`);
  console.log(`[Activity] 💰 Simulated API Cost: $0.20`);
  
  // Simulate API call delay
  await new Promise((resolve) => setTimeout(resolve, 150));

  // Generate simulated news articles
  const numArticles = 10 + Math.floor(Math.random() * 10);
  const articles = [];

  const headlines = [
    'Reports Strong Quarterly Earnings',
    'Announces New Product Launch',
    'Faces Regulatory Scrutiny',
    'Expands Into New Markets',
    'CEO Discusses Future Strategy',
    'Analyst Upgrades Rating',
    'Market Share Gains Reported',
    'Partnership Announced',
    'Challenges in Supply Chain',
    'Innovation Drives Growth',
  ];

  const sources = [
    'Bloomberg',
    'Reuters',
    'CNBC',
    'Wall Street Journal',
    'Financial Times',
  ];

  for (let i = 0; i < numArticles; i++) {
    const headline = headlines[Math.floor(Math.random() * headlines.length)];
    const source = sources[Math.floor(Math.random() * sources.length)];
    
    // Generate sentiment based on headline keywords
    let sentiment = 0;
    if (headline.includes('Strong') || headline.includes('Growth') || headline.includes('Gains')) {
      sentiment = 0.5 + Math.random() * 0.4; // Positive: 0.5 to 0.9
    } else if (headline.includes('Challenges') || headline.includes('Scrutiny')) {
      sentiment = -0.5 - Math.random() * 0.4; // Negative: -0.5 to -0.9
    } else {
      sentiment = (Math.random() - 0.5) * 0.6; // Neutral: -0.3 to 0.3
    }

    articles.push({
      headline: `${companySymbol} ${headline}`,
      sentiment,
      source,
    });
  }

  return {
    symbol: companySymbol,
    articles,
  };
}

/**
 * Validate company symbol
 * 
 * In a real implementation, this would check against a list of valid symbols
 */
export async function validateCompanySymbol(symbol: string): Promise<boolean> {
  console.log(`[Activity] Validating company symbol: ${symbol}`);
  
  // Basic validation
  if (!symbol || symbol.length < 1 || symbol.length > 5) {
    return false;
  }

  // Check if all uppercase letters
  if (!/^[A-Z]+$/.test(symbol)) {
    return false;
  }

  return true;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get base price for a symbol (deterministic but varied)
 */
function getBasePriceForSymbol(symbol: string): number {
  // Use symbol hash to generate deterministic but varied base price
  const hash = symbol.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  
  // Generate price between $50 and $500
  return 50 + (hash % 450);
}

