/**
 * Financial Research Workflow - Parent workflow demonstrating child workflows with reset points
 */

import { startChild } from '@temporalio/workflow';
import { recordResetPoint } from './reset-point-helper';
import {
  marketAnalysisChildWorkflow,
  financialMetricsChildWorkflow,
  sentimentAnalysisChildWorkflow,
  riskAssessmentChildWorkflow,
} from './child-workflows';
import type {
  ResearchInput,
  ResearchReport,
  AggregatedResearchResults,
  InvestmentRecommendation,
} from './types';

/**
 * Parent workflow that coordinates financial research using parallel child workflows.
 * 
 * This workflow demonstrates:
 * - Parallel execution of multiple child workflows (fan-out pattern)
 * - Reset points at key checkpoints to allow targeted re-execution
 * - Aggregation of results from multiple sources
 * - Weighted scoring and recommendation generation
 * 
 * Reset Points:
 * - after-research-complete: Reset here to re-run aggregation without re-running expensive child workflows
 * - after-aggregation: Reset here to regenerate recommendations with different thresholds
 */
export async function financialResearchWorkflow(input: ResearchInput): Promise<ResearchReport> {
  const { companySymbol, researchDepth } = input;
  
  console.log(`\n========================================`);
  console.log(`Starting Financial Research for ${companySymbol}`);
  console.log(`Research Depth: ${researchDepth}`);
  console.log(`========================================\n`);

  const startTime = Date.now();

  // ============================================================================
  // Phase 1: Parallel Child Workflow Execution (Fan-Out)
  // ============================================================================

  console.log(`[Phase 1] Launching parallel research workflows...`);
  console.log(`  - Market Analysis`);
  console.log(`  - Financial Metrics`);
  console.log(`  - Sentiment Analysis`);
  console.log(`  - Risk Assessment\n`);

  // Execute all 4 child workflows in parallel
  const [marketResult, financialResult, sentimentResult, riskResult] = await Promise.all([
    startChild(marketAnalysisChildWorkflow, {
      args: [companySymbol],
      workflowId: `market-${companySymbol}-${Date.now()}`,
    }),
    startChild(financialMetricsChildWorkflow, {
      args: [companySymbol],
      workflowId: `financial-${companySymbol}-${Date.now()}`,
    }),
    startChild(sentimentAnalysisChildWorkflow, {
      args: [companySymbol],
      workflowId: `sentiment-${companySymbol}-${Date.now()}`,
    }),
    startChild(riskAssessmentChildWorkflow, {
      args: [companySymbol],
      workflowId: `risk-${companySymbol}-${Date.now()}`,
    }),
  ]);

  console.log(`\n✓ All research workflows completed\n`);

  // RESET POINT: After all expensive child workflows complete
  // Reset here to re-run only aggregation and recommendations (saves API costs!)
  await recordResetPoint('after-research-complete');

  // ============================================================================
  // Phase 2: Aggregate Results
  // ============================================================================

  console.log(`[Phase 2] Aggregating research results...\n`);

  const aggregatedResults: AggregatedResearchResults = {
    market: marketResult,
    financial: financialResult,
    sentiment: sentimentResult,
    risk: riskResult,
  };

  // Display individual scores
  console.log(`Individual Component Scores:`);
  console.log(`  Market Score:     ${marketResult.overallScore.toFixed(2)}/100`);
  console.log(`  Financial Score:  ${financialResult.healthScore.toFixed(2)}/100`);
  console.log(`  Sentiment Score:  ${sentimentResult.confidenceScore.toFixed(2)}/100`);
  console.log(`  Risk Score:       ${riskResult.overallRisk.toFixed(2)}/100 (lower is better)\n`);

  // Calculate weighted overall score
  // Weights: Market 25%, Financial 30%, Sentiment 20%, Risk 25%
  const weightedOverallScore =
    marketResult.overallScore * 0.25 +
    financialResult.healthScore * 0.30 +
    sentimentResult.confidenceScore * 0.20 +
    riskResult.riskAdjustedScore * 0.25; // Using risk-adjusted (inverse) score

  console.log(`Weighted Overall Score: ${weightedOverallScore.toFixed(2)}/100\n`);

  // RESET POINT: After aggregation, before recommendations
  // Reset here to regenerate recommendations with different thresholds
  await recordResetPoint('after-aggregation');

  // ============================================================================
  // Phase 3: Generate Investment Recommendation
  // ============================================================================

  console.log(`[Phase 3] Generating investment recommendation...\n`);

  const recommendation = generateRecommendation(
    weightedOverallScore,
    riskResult.overallRisk,
    sentimentResult.trendDirection
  );

  const confidence = calculateConfidence(
    aggregatedResults,
    weightedOverallScore
  );

  console.log(`========================================`);
  console.log(`RECOMMENDATION: ${recommendation}`);
  console.log(`Confidence: ${confidence.toFixed(2)}%`);
  console.log(`========================================\n`);

  const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log(`Research completed in ${elapsedTime}s\n`);

  // ============================================================================
  // Return Final Report
  // ============================================================================

  return {
    companySymbol,
    timestamp: new Date().toISOString(),
    results: aggregatedResults,
    weightedOverallScore,
    recommendation,
    confidence,
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generate investment recommendation based on scores and risk
 */
function generateRecommendation(
  overallScore: number,
  riskScore: number,
  sentimentTrend: 'improving' | 'stable' | 'declining'
): InvestmentRecommendation {
  // Adjust score based on risk
  const riskAdjustedScore = overallScore - (riskScore * 0.2);

  // Adjust for sentiment trend
  let finalScore = riskAdjustedScore;
  if (sentimentTrend === 'improving') {
    finalScore += 5;
  } else if (sentimentTrend === 'declining') {
    finalScore -= 5;
  }

  // Generate recommendation based on final score
  if (finalScore >= 80) return 'STRONG_BUY';
  if (finalScore >= 65) return 'BUY';
  if (finalScore >= 45) return 'HOLD';
  if (finalScore >= 30) return 'SELL';
  return 'STRONG_SELL';
}

/**
 * Calculate confidence in the recommendation
 */
function calculateConfidence(
  results: AggregatedResearchResults,
  overallScore: number
): number {
  // Confidence based on:
  // 1. Consistency across metrics (lower variance = higher confidence)
  // 2. Sentiment confidence score
  // 3. Risk assessment confidence

  const scores = [
    results.market.overallScore,
    results.financial.healthScore,
    results.sentiment.confidenceScore,
    results.risk.riskAdjustedScore,
  ];

  // Calculate variance
  const mean = scores.reduce((sum, s) => sum + s, 0) / scores.length;
  const variance = scores.reduce((sum, s) => sum + Math.pow(s - mean, 2), 0) / scores.length;
  const consistencyScore = Math.max(0, 100 - variance);

  // Weighted confidence calculation
  const confidence =
    consistencyScore * 0.4 +
    results.sentiment.confidenceScore * 0.3 +
    (100 - results.risk.overallRisk) * 0.3;

  return Math.min(100, Math.max(0, confidence));
}




