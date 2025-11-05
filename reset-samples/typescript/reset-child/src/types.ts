/**
 * Type definitions for financial research workflow
 */

/**
 * Input for the financial research workflow
 */
export interface ResearchInput {
  companySymbol: string;
  researchDepth: 'basic' | 'deep';
}

/**
 * Result from market analysis child workflow
 */
export interface MarketAnalysisResult {
  marketShare: number;
  competitiveIndex: number;
  growthTrend: 'accelerating' | 'stable' | 'declining';
  overallScore: number; // Weighted composite 0-100
}

/**
 * Result from financial metrics child workflow
 */
export interface FinancialMetricsResult {
  peRatio: number;
  debtToEquity: number;
  revenueGrowthRate: number;
  profitMargin: number;
  healthScore: number; // 0-100
}

/**
 * Result from sentiment analysis child workflow
 */
export interface SentimentAnalysisResult {
  newsSentiment: number; // -1 to 1
  socialSentiment: number; // -1 to 1
  analystRating: number; // 1-5 scale
  trendDirection: 'improving' | 'stable' | 'declining';
  confidenceScore: number; // 0-100
}

/**
 * Result from risk assessment child workflow
 */
export interface RiskAssessmentResult {
  volatilityIndex: number;
  sectorRisk: 'low' | 'medium' | 'high';
  regulatoryRisk: number; // 0-100
  overallRisk: number; // 0-100 (lower is better)
  riskAdjustedScore: number; // 0-100
}

/**
 * Aggregated research results
 */
export interface AggregatedResearchResults {
  market: MarketAnalysisResult;
  financial: FinancialMetricsResult;
  sentiment: SentimentAnalysisResult;
  risk: RiskAssessmentResult;
}

/**
 * Investment recommendation
 */
export type InvestmentRecommendation = 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';

/**
 * Final research report
 */
export interface ResearchReport {
  companySymbol: string;
  timestamp: string;
  results: AggregatedResearchResults;
  weightedOverallScore: number; // 0-100
  recommendation: InvestmentRecommendation;
  confidence: number; // 0-100
  costSavings?: string; // For tracking API cost savings on reset
}

/**
 * Historical data for market analysis
 */
export interface HistoricalData {
  symbol: string;
  prices: number[];
  volumes: number[];
  marketCap: number;
}

/**
 * News data for sentiment analysis
 */
export interface NewsData {
  symbol: string;
  articles: Array<{
    headline: string;
    sentiment: number; // -1 to 1
    source: string;
  }>;
}

