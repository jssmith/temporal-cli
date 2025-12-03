/**
 * Client script to start a financial research workflow.
 */

import { Connection, Client } from '@temporalio/client';
import { financialResearchWorkflow } from './workflows';
import type { ResearchInput } from './types';

async function run() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const symbol = args[0] || 'AAPL';
  const depth = (args[1] as 'basic' | 'deep') || 'deep';

  // Connect to Temporal server
  const connection = await Connection.connect({
    address: 'localhost:7233',
  });

  const client = new Client({
    connection,
    namespace: 'default',
  });

  // Start workflow
  const workflowId = `research-${symbol}-${Date.now()}`;
  
  console.log(`\n========================================`);
  console.log(`Starting Financial Research Workflow`);
  console.log(`========================================`);
  console.log(`Company Symbol: ${symbol}`);
  console.log(`Research Depth: ${depth}`);
  console.log(`Workflow ID:    ${workflowId}`);
  console.log(`========================================\n`);

  const input: ResearchInput = {
    companySymbol: symbol,
    researchDepth: depth,
  };

  const handle = await client.workflow.start(financialResearchWorkflow, {
    taskQueue: 'reset-child-ts',
    workflowId,
    args: [input],
  });

  console.log(`✓ Workflow started successfully`);
  console.log(`  Run ID: ${await handle.firstExecutionRunId}\n`);
  console.log(`Waiting for workflow to complete...\n`);

  // Wait for result
  const result = await handle.result();
  
  // Display final report
  console.log(`\n========================================`);
  console.log(`FINAL RESEARCH REPORT`);
  console.log(`========================================`);
  console.log(`Company:        ${result.companySymbol}`);
  console.log(`Timestamp:      ${result.timestamp}`);
  console.log(`Overall Score:  ${result.weightedOverallScore.toFixed(2)}/100`);
  console.log(`Recommendation: ${result.recommendation}`);
  console.log(`Confidence:     ${result.confidence.toFixed(2)}%`);
  console.log(`========================================\n`);

  console.log(`Detailed Scores:`);
  console.log(`  Market Analysis:  ${result.results.market.overallScore.toFixed(2)}/100`);
  console.log(`    - Market Share:      ${result.results.market.marketShare.toFixed(2)}%`);
  console.log(`    - Competitive Index: ${result.results.market.competitiveIndex.toFixed(2)}/100`);
  console.log(`    - Growth Trend:      ${result.results.market.growthTrend}`);
  console.log(``);
  console.log(`  Financial Metrics: ${result.results.financial.healthScore.toFixed(2)}/100`);
  console.log(`    - P/E Ratio:         ${result.results.financial.peRatio.toFixed(2)}`);
  console.log(`    - Debt/Equity:       ${result.results.financial.debtToEquity.toFixed(2)}`);
  console.log(`    - Revenue Growth:    ${result.results.financial.revenueGrowthRate.toFixed(2)}%`);
  console.log(`    - Profit Margin:     ${result.results.financial.profitMargin.toFixed(2)}%`);
  console.log(``);
  console.log(`  Sentiment Analysis: ${result.results.sentiment.confidenceScore.toFixed(2)}/100`);
  console.log(`    - News Sentiment:    ${result.results.sentiment.newsSentiment.toFixed(2)}`);
  console.log(`    - Social Sentiment:  ${result.results.sentiment.socialSentiment.toFixed(2)}`);
  console.log(`    - Analyst Rating:    ${result.results.sentiment.analystRating.toFixed(2)}/5`);
  console.log(`    - Trend:             ${result.results.sentiment.trendDirection}`);
  console.log(``);
  console.log(`  Risk Assessment: ${result.results.risk.overallRisk.toFixed(2)}/100 (lower is better)`);
  console.log(`    - Volatility Index:  ${result.results.risk.volatilityIndex.toFixed(4)}`);
  console.log(`    - Sector Risk:       ${result.results.risk.sectorRisk}`);
  console.log(`    - Regulatory Risk:   ${result.results.risk.regulatoryRisk.toFixed(2)}/100`);
  console.log(``);

  console.log(`\n========================================`);
  console.log(`RESET POINT USAGE`);
  console.log(`========================================`);
  console.log(`You can now reset this workflow to specific points:\n`);
  console.log(`1. Reset after research (re-run aggregation only):`);
  console.log(`   temporal workflow reset \\`);
  console.log(`     --workflow-id ${workflowId} \\`);
  console.log(`     --reset-point after-research-complete \\`);
  console.log(`     --reason "Changed aggregation formula"\n`);
  console.log(`   💰 Saves: ~$0.50 in API costs (child workflows not re-executed)\n`);
  console.log(`2. Reset after aggregation (re-run recommendations only):`);
  console.log(`   temporal workflow reset \\`);
  console.log(`     --workflow-id ${workflowId} \\`);
  console.log(`     --reset-point after-aggregation \\`);
  console.log(`     --reason "Updated recommendation thresholds"\n`);
  console.log(`========================================\n`);
}

run().catch((err) => {
  console.error('Client failed:', err);
  process.exit(1);
});




