# Child Workflows with Reset Points - Financial Research Example

## What This Demonstrates

- **Child Workflows**: Parent workflow coordinating multiple child workflows in parallel
- **Parallel Fan-Out**: Executing 4 research workflows simultaneously for faster results
- **Reset Points**: Strategic checkpoints to avoid re-running expensive operations
- **Real Computations**: Financial analysis with actual algorithms (P/E ratios, CAGR, volatility, sentiment scoring)
- **Cost Savings**: Demonstrates how reset points save API costs by reusing child workflow results

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 financialResearchWorkflow                    │
│                     (Parent Workflow)                        │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │   Parallel Fan-Out    │
        │   (4 Child Workflows) │
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┬───────────────┐
    │               │               │               │
    ▼               ▼               ▼               ▼
┌────────┐    ┌──────────┐    ┌───────────┐   ┌──────────┐
│ Market │    │Financial │    │ Sentiment │   │   Risk   │
│Analysis│    │ Metrics  │    │ Analysis  │   │Assessment│
└────────┘    └──────────┘    └───────────┘   └──────────┘
    │               │               │               │
    └───────────────┼───────────────┴───────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ 🔖 RESET POINT 1 │
          │ after-research   │
          └─────────┬────────┘
                    │
                    ▼
          ┌──────────────────┐
          │   Aggregate &    │
          │  Calculate Score │
          └─────────┬────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ 🔖 RESET POINT 2 │
          │ after-aggregation│
          └─────────┬────────┘
                    │
                    ▼
          ┌──────────────────┐
          │   Generate       │
          │ Recommendation   │
          └──────────────────┘
```

## Prerequisites

- Temporal server running: `temporal server start-dev`
- Temporal CLI installed
- Node.js 16+
- npm or yarn

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start the Worker

```bash
npm run worker
```

You should see:
```
========================================
Financial Research Worker Started
========================================
Task Queue: reset-child-ts
Registered Workflows:
  - financialResearchWorkflow (parent)
  - marketAnalysisChildWorkflow
  - financialMetricsChildWorkflow
  - sentimentAnalysisChildWorkflow
  - riskAssessmentChildWorkflow

Press Ctrl+C to stop...
========================================
```

### 3. Start a Workflow (in a new terminal)

Using the client script (recommended):
```bash
npm run workflow
```

Or with a specific company symbol:
```bash
npm run workflow TSLA deep
```

Or using the Temporal CLI:
```bash
temporal workflow start \
    --task-queue reset-child-ts \
    --type financialResearchWorkflow \
    --workflow-id research-AAPL-12345 \
    --input '{"companySymbol": "AAPL", "researchDepth": "deep"}'
```

## Understanding the Output

When you run the workflow, you'll see each phase:

```
========================================
Starting Financial Research for AAPL
Research Depth: deep
========================================

[Phase 1] Launching parallel research workflows...
  - Market Analysis
  - Financial Metrics
  - Sentiment Analysis
  - Risk Assessment

[Market Analysis] Starting analysis for AAPL
[Activity] Fetching historical data for AAPL...
[Activity] 💰 Simulated API Cost: $0.10
[Market Analysis] Market Score: 87.23/100

[Financial Metrics] Starting analysis for AAPL
[Activity] Fetching historical data for AAPL...
[Activity] 💰 Simulated API Cost: $0.10
[Financial Metrics] Health Score: 92.45/100

[Sentiment Analysis] Starting analysis for AAPL
[Activity] Fetching news data for AAPL...
[Activity] 💰 Simulated API Cost: $0.20
[Sentiment Analysis] Confidence Score: 78.56/100

[Risk Assessment] Starting analysis for AAPL
[Activity] Fetching historical data for AAPL...
[Activity] 💰 Simulated API Cost: $0.10
[Risk Assessment] Overall Risk: 25.34/100 (lower is better)

✓ All research workflows completed

Recorded reset point: after-research-complete

[Phase 2] Aggregating research results...

Individual Component Scores:
  Market Score:     87.23/100
  Financial Score:  92.45/100
  Sentiment Score:  78.56/100
  Risk Score:       25.34/100 (lower is better)

Weighted Overall Score: 83.67/100

Recorded reset point: after-aggregation

[Phase 3] Generating investment recommendation...

========================================
RECOMMENDATION: STRONG_BUY
Confidence: 85.23%
========================================
```

## Reset Points Explained

This example has **two strategic reset points** that demonstrate real cost savings:

### 1. `after-research-complete` - The Money Saver

**When to use**: 
- You found a bug in your aggregation formula
- You want to change how scores are weighted
- You're tweaking recommendation logic

**What it does**:
- Skips re-running all 4 child workflows
- Starts from the aggregation phase
- **Saves ~$0.50 in simulated API costs!**

**Example**:
```bash
temporal workflow reset \
    --workflow-id research-AAPL-12345 \
    --reset-point after-research-complete \
    --reason "Changed market analysis weight from 25% to 30%"
```

**Why this is powerful**: In a real production system, each child workflow might call expensive external APIs:
- Market data API: $0.10 per request
- Financial data API: $0.10 per request
- News/sentiment API: $0.20 per request
- Risk data API: $0.10 per request

Total per research: **$0.50** × number of workflow executions

With reset points, you can fix bugs in aggregation/recommendation logic WITHOUT paying for API calls again. For a high-volume system, this can save thousands of dollars.

### 2. `after-aggregation` - Fine-Tuning Recommendations

**When to use**:
- You want to adjust recommendation thresholds (e.g., "buy" threshold from 80→85)
- You're testing different recommendation strategies
- You need to regenerate the final report

**What it does**:
- Skips both research AND aggregation
- Only regenerates recommendations
- Extremely fast (< 1 second)

**Example**:
```bash
temporal workflow reset \
    --workflow-id research-AAPL-12345 \
    --reset-point after-aggregation \
    --reason "Testing more conservative recommendation thresholds"
```

## Child Workflows in Detail

Each child workflow performs real financial analysis computations:

### Market Analysis Child Workflow

**Inputs**: Company symbol  
**Computations**:
- Market share calculation
- Competitive positioning index (based on price stability and volume)
- Growth trend analysis (comparing first-half vs second-half growth rates)
- Weighted composite score

**Returns**:
```typescript
{
  marketShare: 12.5,           // Percentage
  competitiveIndex: 87.3,      // 0-100 scale
  growthTrend: 'accelerating', // 'accelerating' | 'stable' | 'declining'
  overallScore: 87.2           // Weighted composite
}
```

### Financial Metrics Child Workflow

**Inputs**: Company symbol  
**Computations**:
- P/E Ratio (Price-to-Earnings)
- Debt-to-Equity ratio
- CAGR (Compound Annual Growth Rate)
- Profit margin calculation
- Financial health score (weighted formula)

**Returns**:
```typescript
{
  peRatio: 28.5,           // Typical range: 10-30
  debtToEquity: 0.45,      // Lower is better
  revenueGrowthRate: 15.3, // Percentage
  profitMargin: 22.1,      // Percentage
  healthScore: 92.4        // 0-100
}
```

### Sentiment Analysis Child Workflow

**Inputs**: Company symbol  
**Computations**:
- News sentiment aggregation (average of article sentiments)
- Social media sentiment simulation
- Analyst rating conversion (sentiment → 1-5 scale)
- Trend analysis (comparing early vs recent sentiment)
- Confidence score (based on volume and consistency)

**Returns**:
```typescript
{
  newsSentiment: 0.65,       // -1 to 1 scale
  socialSentiment: 0.42,     // -1 to 1 scale
  analystRating: 4.3,        // 1-5 scale
  trendDirection: 'improving', // 'improving' | 'stable' | 'declining'
  confidenceScore: 78.5      // 0-100
}
```

### Risk Assessment Child Workflow

**Inputs**: Company symbol  
**Computations**:
- Volatility index (standard deviation of price returns)
- Sector risk categorization
- Regulatory risk scoring
- Overall risk calculation (weighted composite, lower is better)
- Risk-adjusted score (inverse for consistency)

**Returns**:
```typescript
{
  volatilityIndex: 0.0234,      // Standard deviation
  sectorRisk: 'medium',         // 'low' | 'medium' | 'high'
  regulatoryRisk: 45.2,         // 0-100
  overallRisk: 25.3,            // 0-100 (lower is better)
  riskAdjustedScore: 74.7       // 0-100 (100 - overallRisk)
}
```

## How Child Workflows Work

In TypeScript, you start child workflows using `startChild`:

```typescript
import { startChild } from '@temporalio/workflow';

// Start a single child workflow
const marketResult = await startChild(marketAnalysisChildWorkflow, {
  args: ['AAPL'],
  workflowId: 'market-AAPL-123',
});

// Start multiple child workflows in parallel
const [market, financial, sentiment, risk] = await Promise.all([
  startChild(marketAnalysisChildWorkflow, { args: ['AAPL'] }),
  startChild(financialMetricsChildWorkflow, { args: ['AAPL'] }),
  startChild(sentimentAnalysisChildWorkflow, { args: ['AAPL'] }),
  startChild(riskAssessmentChildWorkflow, { args: ['AAPL'] }),
]);
```

**Key Benefits**:
- **Parallel Execution**: All children run simultaneously
- **Independent Scaling**: Each child can run on different workers
- **Isolated History**: Each child has its own workflow history
- **Reusable**: Child workflows can be called from multiple parents

## Common Use Cases for Reset Points

### Use Case 1: Bug in Aggregation Logic

**Scenario**: You discover that the weighted score formula has a bug. Market analysis should be 30%, not 25%.

**Solution**:
```bash
# Fix the code
# Reset to after-research-complete
temporal workflow reset \
    --workflow-id research-AAPL-12345 \
    --reset-point after-research-complete \
    --reason "Fixed market analysis weight (25% → 30%)"
```

**Result**: All 4 child workflows don't re-run. Only aggregation and recommendation phases execute.

### Use Case 2: Updated Recommendation Thresholds

**Scenario**: You want to be more conservative. "STRONG_BUY" should require 85+ instead of 80+.

**Solution**:
```bash
# Update the threshold in code
# Reset to after-aggregation
temporal workflow reset \
    --workflow-id research-AAPL-12345 \
    --reset-point after-aggregation \
    --reason "More conservative thresholds"
```

**Result**: Ultra-fast reset. Only the recommendation generation runs.

### Use Case 3: A/B Testing Strategies

**Scenario**: You want to compare two different scoring strategies.

**Solution**:
```bash
# Run workflow once
# Record results
# Modify scoring weights
# Reset to after-research-complete
# Compare results
```

**Result**: Test multiple strategies without paying for API calls repeatedly.

## Viewing Reset Points

You can view the reset points in the workflow history:

```bash
temporal workflow show \
    --workflow-id research-AAPL-12345 \
    | grep -A 5 "temporal-reset-point"
```

You should see markers:
```
EventType: MarkerRecorded
MarkerName: temporal-reset-point
Details: {"name": "after-research-complete"}
...
MarkerName: temporal-reset-point
Details: {"name": "after-aggregation"}
```

## Development

### Build the Project

```bash
npm run build
```

### Watch Mode (for development)

```bash
npm run start.watch
```

### Project Structure

```
reset-child/
├── src/
│   ├── types.ts              # Type definitions
│   ├── child-workflows.ts    # 4 child workflow implementations
│   ├── workflows.ts          # Parent workflow
│   ├── activities.ts         # Data fetching activities
│   ├── reset-point-helper.ts # Reset point marker utility
│   ├── worker.ts             # Worker process
│   └── client.ts             # Workflow starter
├── package.json
├── tsconfig.json
└── README.md
```

## Customization Ideas

### Add More Child Workflows

Want to add a "Competitor Analysis" child workflow?

1. Define types in `types.ts`:
```typescript
export interface CompetitorAnalysisResult {
  topCompetitors: string[];
  relativeScore: number;
}
```

2. Implement child workflow in `child-workflows.ts`:
```typescript
export async function competitorAnalysisChildWorkflow(
  symbol: string
): Promise<CompetitorAnalysisResult> {
  // Your analysis logic
  return { topCompetitors: [...], relativeScore: 85.5 };
}
```

3. Add to parent workflow in `workflows.ts`:
```typescript
const competitorResult = await startChild(competitorAnalysisChildWorkflow, {
  args: [companySymbol],
});
```

### Change Scoring Weights

Modify the weighted score calculation in `workflows.ts`:

```typescript
// Current weights
const weightedOverallScore =
  marketResult.overallScore * 0.25 +
  financialResult.healthScore * 0.30 +
  sentimentResult.confidenceScore * 0.20 +
  riskResult.riskAdjustedScore * 0.25;

// Your custom weights
const weightedOverallScore =
  marketResult.overallScore * 0.40 +      // Emphasize market
  financialResult.healthScore * 0.30 +
  sentimentResult.confidenceScore * 0.10 + // De-emphasize sentiment
  riskResult.riskAdjustedScore * 0.20;
```

### Change Recommendation Thresholds

Modify the `generateRecommendation` function in `workflows.ts`:

```typescript
function generateRecommendation(
  overallScore: number,
  riskScore: number,
  sentimentTrend: string
): InvestmentRecommendation {
  // Your custom logic
  if (finalScore >= 90) return 'STRONG_BUY'; // More strict
  // ...
}
```

## Comparison with Basic Reset Example

| Feature | reset-basic | reset-child |
|---------|-------------|-------------|
| Child Workflows | ❌ No | ✅ Yes (4 workflows) |
| Parallel Execution | ❌ No | ✅ Yes (fan-out pattern) |
| Activities | Simple | Simulated API calls |
| Computations | None | Real financial algorithms |
| Reset Points | 2 | 2 (but more valuable) |
| Cost Savings Demo | ❌ No | ✅ Yes (~$0.50 per reset) |
| Use Case | Learning basics | Real-world pattern |

## Next Steps

- Try modifying the scoring weights and using reset points
- Add your own child workflow for additional analysis
- Experiment with different recommendation strategies
- Check out the Go and Python versions for multi-language samples

## Real-World Applications

This pattern is used in production for:

- **Financial Analysis**: Research reports, portfolio optimization
- **Risk Assessment**: Credit scoring, fraud detection
- **Market Research**: Competitor analysis, trend detection
- **Data Pipelines**: ETL processes with multiple data sources
- **ML Workflows**: Feature engineering, model ensemble
- **Document Processing**: OCR, classification, extraction in parallel

## Tips

1. **Use reset points after expensive operations** - API calls, ML inference, heavy computations
2. **Name reset points descriptively** - "after-research-complete" not "checkpoint1"
3. **Test reset points during development** - Verify workflows reset correctly
4. **Monitor cost savings** - Track how much you save by avoiding re-execution
5. **Document when to use each reset point** - Help your team understand the strategy

## Same Pattern, Different Languages

This example demonstrates the same pattern used in:
- Python: `samples-python/financial_research_agent`
- Go: Coming soon!

All use the same concepts:
- Child workflows for parallel processing
- Reset points for cost optimization
- Real computations for demonstrating value




