/**
 * Child workflows for financial research
 * Each child workflow performs specific analysis with realistic computations
 */

import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';
import type {
  MarketAnalysisResult,
  FinancialMetricsResult,
  SentimentAnalysisResult,
  RiskAssessmentResult,
} from './types';

const { fetchHistoricalData, fetchNewsData } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10s',
});

/**
 * Market Analysis Child Workflow
 * Analyzes market position, competitive landscape, and growth trends
 */
export async function marketAnalysisChildWorkflow(
  companySymbol: string
): Promise<MarketAnalysisResult> {
  console.log(`[Market Analysis] Starting analysis for ${companySymbol}`);

  // Fetch historical market data
  const historicalData = await fetchHistoricalData(companySymbol);

  // Calculate market share (simulated)
  const marketShare = calculateMarketShare(historicalData.marketCap);

  // Calculate competitive positioning index
  const competitiveIndex = calculateCompetitiveIndex(
    historicalData.prices,
    historicalData.volumes
  );

  // Analyze growth trend
  const growthTrend = analyzeGrowthTrend(historicalData.prices);

  // Calculate overall market score (weighted composite)
  const overallScore =
    marketShare * 0.3 + competitiveIndex * 0.4 + (growthTrend === 'accelerating' ? 90 : growthTrend === 'stable' ? 60 : 30) * 0.3;

  console.log(`[Market Analysis] Market Score: ${overallScore.toFixed(2)}/100`);

  return {
    marketShare,
    competitiveIndex,
    growthTrend,
    overallScore,
  };
}

/**
 * Financial Metrics Child Workflow
 * Calculates financial health indicators and ratios
 */
export async function financialMetricsChildWorkflow(
  companySymbol: string
): Promise<FinancialMetricsResult> {
  console.log(`[Financial Metrics] Starting analysis for ${companySymbol}`);

  const historicalData = await fetchHistoricalData(companySymbol);

  // Calculate P/E ratio (Price-to-Earnings)
  const peRatio = calculatePERatio(historicalData.prices[historicalData.prices.length - 1]);

  // Calculate debt-to-equity ratio
  const debtToEquity = calculateDebtToEquity(historicalData.marketCap);

  // Calculate revenue growth rate (CAGR - Compound Annual Growth Rate)
  const revenueGrowthRate = calculateCAGR(historicalData.prices);

  // Calculate profit margin
  const profitMargin = calculateProfitMargin(historicalData.marketCap);

  // Calculate financial health score (weighted formula)
  const peScore = Math.max(0, 100 - peRatio * 2); // Lower P/E is better (capped)
  const debtScore = Math.max(0, 100 - debtToEquity * 50); // Lower debt is better
  const growthScore = Math.min(100, revenueGrowthRate * 5); // Higher growth is better
  const marginScore = Math.min(100, profitMargin * 5); // Higher margin is better

  const healthScore = peScore * 0.2 + debtScore * 0.3 + growthScore * 0.3 + marginScore * 0.2;

  console.log(`[Financial Metrics] Health Score: ${healthScore.toFixed(2)}/100`);

  return {
    peRatio,
    debtToEquity,
    revenueGrowthRate,
    profitMargin,
    healthScore,
  };
}

/**
 * Sentiment Analysis Child Workflow
 * Analyzes news, social media, and analyst sentiment
 */
export async function sentimentAnalysisChildWorkflow(
  companySymbol: string
): Promise<SentimentAnalysisResult> {
  console.log(`[Sentiment Analysis] Starting analysis for ${companySymbol}`);

  const newsData = await fetchNewsData(companySymbol);

  // Calculate news sentiment (average of article sentiments)
  const newsSentiment = calculateNewsSentiment(newsData.articles);

  // Calculate social media sentiment (simulated)
  const socialSentiment = calculateSocialSentiment(companySymbol);

  // Calculate analyst rating (simulated 1-5 scale)
  const analystRating = calculateAnalystRating(newsData.articles);

  // Analyze sentiment trend
  const trendDirection = analyzeSentimentTrend(newsData.articles);

  // Calculate confidence score based on data volume and consistency
  const confidenceScore = calculateSentimentConfidence(newsData.articles);

  console.log(`[Sentiment Analysis] Confidence Score: ${confidenceScore.toFixed(2)}/100`);

  return {
    newsSentiment,
    socialSentiment,
    analystRating,
    trendDirection,
    confidenceScore,
  };
}

/**
 * Risk Assessment Child Workflow
 * Evaluates volatility, sector risks, and overall risk profile
 */
export async function riskAssessmentChildWorkflow(
  companySymbol: string
): Promise<RiskAssessmentResult> {
  console.log(`[Risk Assessment] Starting analysis for ${companySymbol}`);

  const historicalData = await fetchHistoricalData(companySymbol);

  // Calculate volatility index (standard deviation of returns)
  const volatilityIndex = calculateVolatility(historicalData.prices);

  // Assess sector risk
  const sectorRisk = assessSectorRisk(companySymbol);

  // Calculate regulatory risk
  const regulatoryRisk = calculateRegulatoryRisk(companySymbol, sectorRisk);

  // Calculate overall risk (weighted composite, lower is better)
  const volatilityRisk = Math.min(100, volatilityIndex * 100);
  const sectorRiskScore = sectorRisk === 'high' ? 80 : sectorRisk === 'medium' ? 50 : 20;

  const overallRisk = volatilityRisk * 0.4 + sectorRiskScore * 0.3 + regulatoryRisk * 0.3;

  // Calculate risk-adjusted score (inverse of risk for consistency)
  const riskAdjustedScore = 100 - overallRisk;

  console.log(`[Risk Assessment] Overall Risk: ${overallRisk.toFixed(2)}/100 (lower is better)`);

  return {
    volatilityIndex,
    sectorRisk,
    regulatoryRisk,
    overallRisk,
    riskAdjustedScore,
  };
}

// ============================================================================
// Helper Functions for Computations
// ============================================================================

function calculateMarketShare(marketCap: number): number {
  // Simulated market share calculation based on market cap
  // Assuming total market is 10x this company's market cap
  return Math.min(100, (marketCap / (marketCap * 10)) * 100 * 10);
}

function calculateCompetitiveIndex(prices: number[], volumes: number[]): number {
  // Competitive index based on price stability and volume
  const priceStability = 100 - calculateVolatility(prices) * 100;
  const volumeScore = Math.min(100, Math.log10(volumes.reduce((a, b) => a + b, 0)) * 10);
  return (priceStability * 0.6 + volumeScore * 0.4);
}

function analyzeGrowthTrend(prices: number[]): 'accelerating' | 'stable' | 'declining' {
  if (prices.length < 3) return 'stable';

  // Calculate growth rates between consecutive periods
  const growthRates: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    growthRates.push((prices[i] - prices[i - 1]) / prices[i - 1]);
  }

  // Check if growth is accelerating (increasing growth rates)
  const avgFirstHalf = growthRates.slice(0, Math.floor(growthRates.length / 2)).reduce((a, b) => a + b, 0) / Math.floor(growthRates.length / 2);
  const avgSecondHalf = growthRates.slice(Math.floor(growthRates.length / 2)).reduce((a, b) => a + b, 0) / (growthRates.length - Math.floor(growthRates.length / 2));

  if (avgSecondHalf > avgFirstHalf + 0.02) return 'accelerating';
  if (avgSecondHalf < avgFirstHalf - 0.02) return 'declining';
  return 'stable';
}

function calculatePERatio(currentPrice: number): number {
  // Simulated P/E ratio (Price / Earnings)
  // Typical P/E ratios range from 10-30 for most stocks
  const simulatedEarnings = currentPrice / (15 + Math.random() * 20);
  return currentPrice / simulatedEarnings;
}

function calculateDebtToEquity(marketCap: number): number {
  // Simulated debt-to-equity ratio
  // Good companies typically have D/E < 1.0
  return 0.3 + Math.random() * 0.8;
}

function calculateCAGR(prices: number[]): number {
  // Compound Annual Growth Rate
  if (prices.length < 2) return 0;

  const beginningValue = prices[0];
  const endingValue = prices[prices.length - 1];
  const years = prices.length / 12; // Assuming monthly data

  return (Math.pow(endingValue / beginningValue, 1 / years) - 1) * 100;
}

function calculateProfitMargin(marketCap: number): number {
  // Simulated profit margin (10-30% is typical for good companies)
  return 10 + Math.random() * 20;
}

function calculateNewsSentiment(articles: Array<{ sentiment: number }>): number {
  if (articles.length === 0) return 0;
  return articles.reduce((sum, article) => sum + article.sentiment, 0) / articles.length;
}

function calculateSocialSentiment(symbol: string): number {
  // Simulated social media sentiment (-1 to 1)
  // Using symbol hash for deterministic but varied results
  const hash = symbol.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return (Math.sin(hash) * 0.6); // Range: -0.6 to 0.6
}

function calculateAnalystRating(articles: Array<{ sentiment: number }>): number {
  // Convert sentiment to 1-5 rating scale
  const avgSentiment = calculateNewsSentiment(articles);
  // Map -1..1 to 1..5
  return 3 + avgSentiment * 2;
}

function analyzeSentimentTrend(articles: Array<{ sentiment: number }>): 'improving' | 'stable' | 'declining' {
  if (articles.length < 4) return 'stable';

  const firstHalf = articles.slice(0, Math.floor(articles.length / 2));
  const secondHalf = articles.slice(Math.floor(articles.length / 2));

  const firstAvg = firstHalf.reduce((sum, a) => sum + a.sentiment, 0) / firstHalf.length;
  const secondAvg = secondHalf.reduce((sum, a) => sum + a.sentiment, 0) / secondHalf.length;

  if (secondAvg > firstAvg + 0.15) return 'improving';
  if (secondAvg < firstAvg - 0.15) return 'declining';
  return 'stable';
}

function calculateSentimentConfidence(articles: Array<{ sentiment: number }>): number {
  // Confidence based on volume and consistency
  const volumeScore = Math.min(100, articles.length * 10); // More articles = higher confidence

  // Calculate variance (lower variance = higher confidence)
  const avg = calculateNewsSentiment(articles);
  const variance = articles.reduce((sum, a) => sum + Math.pow(a.sentiment - avg, 2), 0) / articles.length;
  const consistencyScore = Math.max(0, 100 - variance * 100);

  return (volumeScore * 0.4 + consistencyScore * 0.6);
}

function calculateVolatility(prices: number[]): number {
  if (prices.length < 2) return 0;

  // Calculate returns
  const returns: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
  }

  // Calculate standard deviation of returns
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
  const squaredDiffs = returns.map(r => Math.pow(r - mean, 2));
  const variance = squaredDiffs.reduce((sum, d) => sum + d, 0) / returns.length;

  return Math.sqrt(variance);
}

function assessSectorRisk(symbol: string): 'low' | 'medium' | 'high' {
  // Simulated sector risk based on symbol
  const hash = symbol.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const risk = hash % 3;
  return risk === 0 ? 'low' : risk === 1 ? 'medium' : 'high';
}

function calculateRegulatoryRisk(symbol: string, sectorRisk: 'low' | 'medium' | 'high'): number {
  // Regulatory risk score (0-100)
  const baseRisk = sectorRisk === 'high' ? 60 : sectorRisk === 'medium' ? 40 : 20;
  const hash = symbol.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const variation = (hash % 30) - 15; // -15 to +15
  return Math.max(0, Math.min(100, baseRisk + variation));
}




