# Child Workflows with Reset Points - Financial Research Example

## What This Demonstrates

- **Child Workflows**: Parent workflow coordinating multiple child workflows in parallel
- **Parallel Fan-Out**: Executing 4 research workflows simultaneously for faster results
- **Reset Points**: Strategic checkpoints to avoid re-running expensive operations
- **Cascading Resets**: Selectively reset 2 out of 4 child workflows based on shared logic
- **Real Computations**: Financial analysis with actual algorithms (P/E ratios, CAGR, volatility, sentiment scoring)
- **Deterministic Workflows**: Uses `workflow.random()` for deterministic randomness in workflows
- **Cost Savings**: Demonstrates how reset points save API costs by reusing child workflow results

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              FinancialResearchWorkflow                       │
│                  (Parent Workflow)                           │
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
│(has RP)│    │(has RP)  │    │ (no RP)   │   │ (no RP)  │
└────┬───┘    └─────┬────┘    └───────────┘   └──────────┘
     │              │               │               │
     │   🔖 RP in   │               │               │
     │   children   │               │               │
     └──────┬───────┘               │               │
            │                       │               │
            └───────────────┬───────┴───────────────┘
                            │
                            ▼
                  ┌──────────────────────┐
                  │ 🔖 RESET POINT 1     │
                  │ after-historical-    │
                  │ data-fetch (cascade) │
                  └─────────┬────────────┘
                            │
                (Market + Financial complete)
                            │
                            ▼
                  ┌──────────────────┐
                  │ 🔖 RESET POINT 2 │
                  │ after-research   │
                  └─────────┬────────┘
                            │
                     (All 4 complete)
                            │
                            ▼
                  ┌──────────────────┐
                  │   Aggregate &    │
                  │  Calculate Score │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ 🔖 RESET POINT 3 │
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
- Python 3.8+
- pip or poetry

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or create a virtual environment first (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the Worker

```bash
python worker.py
```

You should see:
```
========================================
Financial Research Worker Started
========================================
Task Queue: reset-child-python
Registered Workflows:
  - FinancialResearchWorkflow (parent)
  - MarketAnalysisChildWorkflow
  - FinancialMetricsChildWorkflow
  - SentimentAnalysisChildWorkflow
  - RiskAssessmentChildWorkflow

Press Ctrl+C to stop...
========================================
```

### 3. Start a Workflow (in a new terminal)

Using the client script (recommended):
```bash
python client.py
```

Or with a specific company symbol:
```bash
python client.py TSLA deep
```

Or using the Temporal CLI:
```bash
temporal workflow start \
    --task-queue reset-child-python \
    --type FinancialResearchWorkflow \
    --workflow-id research-AAPL-12345 \
    --input '{"company_symbol": "AAPL", "research_depth": "deep"}'
```

## Understanding the Output

When you run the workflow, you'll see each phase:

```
========================================
Starting Financial Research for AAPL
Research Depth: deep
========================================

[Phase 1a] Launching historical data research workflows...
  - Market Analysis
  - Financial Metrics

[Market Analysis] Starting analysis for AAPL
[Activity] Fetching historical data for AAPL...
[Activity] 💰 Simulated API Cost: $0.10
[Market Analysis] Market Score: 87.23/100

[Financial Metrics] Starting analysis for AAPL
[Activity] Fetching historical data for AAPL...
[Activity] 💰 Simulated API Cost: $0.10
[Financial Metrics] Health Score: 92.45/100

✓ Historical data workflows completed (Market + Financial)

Recorded reset point: after-historical-data-fetch

[Phase 1b] Waiting for remaining research workflows...
  - Sentiment Analysis
  - Risk Assessment

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

This example has **three strategic reset points** that demonstrate real cost savings and cascading resets:

### 1. `after-historical-data-fetch` - The Cascading Reset Demo 🌊

**When to use**: 
- You found a bug in how historical data is processed (Market or Financial calculations)
- You want to fix computation logic that uses historical data
- You need to reprocess only the data-intensive workflows

**What it does**:
- Resets parent workflow to after Market + Financial complete
- **With `--cascade` flag**: Also resets Market Analysis and Financial Metrics child workflows
- **Skips** Sentiment Analysis and Risk Assessment (they don't have this reset point)
- **Saves ~$0.20 in API costs** (avoids re-fetching historical data for 2 workflows)

**Example (with cascading)**:
```bash
temporal workflow reset \
    --workflow-id research-AAPL-12345 \
    --reset-point after-historical-data-fetch \
    --cascade \
    --reason "Fixed P/E ratio calculation bug"
```

**Result**:
- ✅ Parent resets → re-runs Sentiment + Risk + aggregation + recommendations
- ✅ Market Analysis child resets → re-runs calculations (skips data fetch)
- ✅ Financial Metrics child resets → re-runs calculations (skips data fetch)
- ❌ Sentiment Analysis child NOT reset (doesn't have this reset point)
- ❌ Risk Assessment child NOT reset (doesn't have this reset point)

**Why this is powerful**: This demonstrates **selective cascading** - only workflows with shared logic (historical data processing) are reset together, while unrelated workflows (news/sentiment) continue unchanged. This is perfect for fixing bugs that only affect specific data processing paths.

### 2. `after-research-complete` - The Money Saver

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

### 3. `after-aggregation` - Fine-Tuning Recommendations

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
- Fetch historical data activity (`$0.10`)
- **🔖 Reset Point**: `after-historical-data-fetch` (for cascading reset)
- Market share calculation
- Competitive positioning index (based on price stability and volume)
- Growth trend analysis (comparing first-half vs second-half growth rates)
- Weighted composite score

**Returns**:
```python
{
    'market_share': 12.5,           # Percentage
    'competitive_index': 87.3,      # 0-100 scale
    'growth_trend': 'accelerating', # 'accelerating' | 'stable' | 'declining'
    'overall_score': 87.2           # Weighted composite
}
```

### Financial Metrics Child Workflow

**Inputs**: Company symbol  
**Computations**:
- Fetch historical data activity (`$0.10`)
- **🔖 Reset Point**: `after-historical-data-fetch` (for cascading reset)
- P/E Ratio (Price-to-Earnings)
- Debt-to-Equity ratio
- CAGR (Compound Annual Growth Rate)
- Profit margin calculation
- Financial health score (weighted formula)

**Returns**:
```python
{
    'pe_ratio': 28.5,            # Typical range: 10-30
    'debt_to_equity': 0.45,      # Lower is better
    'revenue_growth_rate': 15.3, # Percentage
    'profit_margin': 22.1,       # Percentage
    'health_score': 92.4         # 0-100
}
```

### Sentiment Analysis Child Workflow

**Inputs**: Company symbol  
**Computations**:
- Fetch news data activity (`$0.20`)
- News sentiment aggregation (average of article sentiments)
- Social media sentiment simulation
- Analyst rating conversion (sentiment → 1-5 scale)
- Trend analysis (comparing early vs recent sentiment)
- Confidence score (based on volume and consistency)

**Note**: This workflow does NOT have `after-historical-data-fetch` reset point (uses different data source)

**Returns**:
```python
{
    'news_sentiment': 0.65,        # -1 to 1 scale
    'social_sentiment': 0.42,      # -1 to 1 scale
    'analyst_rating': 4.3,         # 1-5 scale
    'trend_direction': 'improving', # 'improving' | 'stable' | 'declining'
    'confidence_score': 78.5       # 0-100
}
```

### Risk Assessment Child Workflow

**Inputs**: Company symbol  
**Computations**:
- Fetch historical data activity (`$0.10`)
- Volatility index (standard deviation of price returns)
- Sector risk categorization
- Regulatory risk scoring
- Overall risk calculation (weighted composite, lower is better)
- Risk-adjusted score (inverse for consistency)

**Note**: This workflow does NOT have `after-historical-data-fetch` reset point (different processing logic than Market/Financial)

**Returns**:
```python
{
    'volatility_index': 0.0234,       # Standard deviation
    'sector_risk': 'medium',          # 'low' | 'medium' | 'high'
    'regulatory_risk': 45.2,          # 0-100
    'overall_risk': 25.3,             # 0-100 (lower is better)
    'risk_adjusted_score': 74.7       # 0-100 (100 - overall_risk)
}
```

## How Child Workflows Work

In Python, you start child workflows using `workflow.execute_child_workflow`:

```python
from temporalio import workflow

# Start a single child workflow
market_result = await workflow.execute_child_workflow(
    MarketAnalysisChildWorkflow.run,
    company_symbol,
    id=f"market-{company_symbol}-123",
    task_queue="reset-child-python",
)

# Start multiple child workflows in parallel
import asyncio

market_task = workflow.execute_child_workflow(
    MarketAnalysisChildWorkflow.run,
    company_symbol,
    id=f"market-{company_symbol}-123",
    task_queue="reset-child-python",
)

financial_task = workflow.execute_child_workflow(
    FinancialMetricsChildWorkflow.run,
    company_symbol,
    id=f"financial-{company_symbol}-123",
    task_queue="reset-child-python",
)

# Wait for all to complete
results = await asyncio.gather(market_task, financial_task)
```

**Key Benefits**:
- **Parallel Execution**: All children run simultaneously
- **Independent Scaling**: Each child can run on different workers
- **Isolated History**: Each child has its own workflow history
- **Reusable**: Child workflows can be called from multiple parents

## Cascading Resets - Selective Child Reset

The `after-historical-data-fetch` reset point demonstrates **cascading resets** - a powerful feature that automatically resets child workflows when you reset a parent.

### How Cascading Works

When you add the `--cascade` flag to a reset command:
1. The parent workflow is reset to the specified point
2. All child workflows that **have the same reset point name** are also reset
3. Child workflows **without that reset point** are skipped
4. This happens recursively through the entire workflow tree

### Why This Example Is Interesting

In our financial research workflow:
- **Market Analysis** and **Financial Metrics** both fetch historical data (`$0.10 each`)
- **Sentiment Analysis** and **Risk Assessment** fetch different data (news, etc.)

By adding `after-historical-data-fetch` to only Market and Financial:
- Resetting the parent **cascades** to Market + Financial children
- Sentiment and Risk are **intentionally skipped**
- This demonstrates **selective reset** based on shared logic

### Example: Fixing a P/E Ratio Bug

Scenario: You discover the P/E ratio calculation in `FinancialMetricsChildWorkflow` has a bug.

**Without cascading** (old way):
```bash
# Reset parent - but child still has bug!
temporal workflow reset --workflow-id research-AAPL-12345 --reset-point after-historical-data-fetch

# Result: Parent restarts, creates NEW Financial child with same bug
# Not helpful!
```

**With cascading** (new way):
```bash
# Fix the bug in code first, then:
temporal workflow reset \
    --workflow-id research-AAPL-12345 \
    --reset-point after-historical-data-fetch \
    --cascade \
    --reason "Fixed P/E ratio calculation"

# Result:
# - Parent resets and reconnects to RESET children
# - Financial Metrics child resets with fixed code
# - Market Analysis child also resets (has same reset point)  
# - Sentiment and Risk continue unchanged (don't have reset point)
# - Saves $0.20 by not re-fetching historical data
```

### Viewing Cascading Reset Results

After a cascading reset, you can see which workflows were reset:

```bash
# Check parent's new run
temporal workflow describe --workflow-id research-AAPL-12345

# Check child workflows - they'll have new run IDs too
temporal workflow describe --workflow-id market-AAPL-<timestamp>
temporal workflow describe --workflow-id financial-AAPL-<timestamp>
```

The parent will reconnect to the reset children automatically via Temporal's workflow reconnection mechanism.

## Common Use Cases for Reset Points

### Use Case 1: Bug in Aggregation Logic

**Scenario**: You discover that the weighted score formula has a bug. Market analysis should be 30%, not 25%.

**Solution**:
```bash
# Fix the code in workflows.py
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
# Update the threshold in workflows.py
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
# Modify scoring weights in workflows.py
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

### Project Structure

```
reset-child/
├── data_types.py            # Type definitions (TypedDict)
├── child_workflows.py       # 4 child workflow implementations
├── workflows.py             # Parent workflow
├── activities.py            # Data fetching activities
├── reset_point_helper.py    # Reset point marker utility
├── worker.py                # Worker process
├── client.py                # Workflow starter
├── requirements.txt         # Dependencies
├── pyproject.toml           # Project metadata
└── README.md                # This file
```

### Running Tests

To test the sample:

1. Start the Temporal dev server:
```bash
temporal server start-dev
```

2. Start the worker:
```bash
python worker.py
```

3. Run a workflow:
```bash
python client.py AAPL deep
```

4. Try resetting to different points:
```bash
temporal workflow reset \
    --workflow-id research-AAPL-<timestamp> \
    --reset-point after-research-complete \
    --reason "Testing reset functionality"
```

## Customization Ideas

### Add More Child Workflows

Want to add a "Competitor Analysis" child workflow?

1. Define types in `data_types.py`:
```python
class CompetitorAnalysisResult(TypedDict):
    top_competitors: List[str]
    relative_score: float
```

2. Implement child workflow in `child_workflows.py`:
```python
@workflow.defn
class CompetitorAnalysisChildWorkflow:
    @workflow.run
    async def run(self, symbol: str) -> CompetitorAnalysisResult:
        # Your analysis logic
        return {
            'top_competitors': [...],
            'relative_score': 85.5
        }
```

3. Add to parent workflow in `workflows.py`:
```python
competitor_task = workflow.execute_child_workflow(
    CompetitorAnalysisChildWorkflow.run,
    company_symbol,
    id=f"competitor-{company_symbol}-{current_time_ms}",
    task_queue="reset-child-python",
)
```

### Change Scoring Weights

Modify the weighted score calculation in `workflows.py`:

```python
# Current weights
weighted_overall_score = (
    market_result['overall_score'] * 0.25 +
    financial_result['health_score'] * 0.30 +
    sentiment_result['confidence_score'] * 0.20 +
    risk_result['risk_adjusted_score'] * 0.25
)

# Your custom weights
weighted_overall_score = (
    market_result['overall_score'] * 0.40 +      # Emphasize market
    financial_result['health_score'] * 0.30 +
    sentiment_result['confidence_score'] * 0.10 + # De-emphasize sentiment
    risk_result['risk_adjusted_score'] * 0.20
)
```

### Change Recommendation Thresholds

Modify the `_generate_recommendation` function in `workflows.py`:

```python
def _generate_recommendation(
    overall_score: float,
    risk_score: float,
    sentiment_trend: str
) -> InvestmentRecommendation:
    # Your custom logic
    if final_score >= 90:  # More strict
        return 'STRONG_BUY'
    # ...
```

## Comparison with Basic Reset Example

| Feature | reset-point | reset-child |
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
- Check out the TypeScript and Go versions for multi-language samples

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
- TypeScript: `reset-samples/typescript/reset-child`
- Go: Coming soon!

All use the same concepts:
- Child workflows for parallel processing
- Reset points for cost optimization
- Real computations for demonstrating value

### Key Differences from TypeScript

While the logic is identical, Python's Temporal SDK has different APIs:

| Feature | TypeScript | Python |
|---------|-----------|--------|
| Random numbers | `workflow.random.random()` | `workflow.random().random()` |
| Current time | `Date.now()` | `workflow.now()` |
| UTC time | `new Date()` | `workflow.utcnow()` |
| Child workflows | `startChild(WorkflowFn, {...})` | `workflow.execute_child_workflow(WorkflowClass.run, ...)` |
| Workflow definition | `export async function myWorkflow()` | `@workflow.defn class MyWorkflow:` |
| Parallel execution | `Promise.all([...])` | `asyncio.gather(...)` |

## How Reset Points Work

✅ **WORKING SOLUTION:** This example uses **local activities** to record reset point markers in workflow history.

### The Local Activity Approach

Since the Python SDK doesn't have a direct `workflow.record_marker()` API, we use a clever workaround:

1. **Local Activity as Marker**: We execute a lightweight local activity named `"temporal-reset-point"`
2. **Creates MarkerRecorded Event**: Local activities create `MarkerRecorded` events in history
3. **CLI Finds It**: The CLI looks for these markers and extracts the reset point name

### Implementation

```python
# reset_point_helper.py
@activity.defn(name="temporal-reset-point")
async def _reset_point_marker_activity(name: str) -> Dict[str, str]:
    """Local activity that records a reset point marker."""
    return {
        "marker_type": "temporal-reset-point",
        "name": name,
    }

async def record_reset_point(name: str) -> None:
    """Record a reset point using a local activity."""
    await workflow.execute_local_activity(
        _reset_point_marker_activity,
        name,
        start_to_close_timeout=timedelta(seconds=1),
    )
```

### Why This Works

- ✅ **No SDK Changes Needed**: Uses existing local activity APIs
- ✅ **Creates Real Markers**: `MarkerRecorded` events appear in history
- ✅ **Fast**: Local activities execute inline (no task queue delay)
- ✅ **Deterministic**: Replays correctly like any other local activity
- ✅ **Works Now**: No waiting for SDK features

## Troubleshooting

### Worker doesn't start

**Error**: `Connection refused`

**Solution**: Make sure Temporal dev server is running:
```bash
temporal server start-dev
```

### Workflow not executing

**Error**: No worker logs appear

**Solution**: Check that the task queue matches:
- Worker: `reset-child-python`
- Client: `reset-child-python`

### Import errors

**Error**: `ModuleNotFoundError: No module named 'temporalio'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Reset point not found

**Error**: `Reset point "after-research-complete" not found`

**Solution**: Make sure the workflow has completed at least once, and the reset point was recorded.

### Non-determinism errors

**Error**: `Cannot access random.random.__call__ from inside a workflow` or `Cannot access datetime.datetime.now.__call__ from inside a workflow`

**Solution**: Workflows must be deterministic. Common non-deterministic operations and their deterministic alternatives:

| Non-Deterministic (❌) | Deterministic (✅) | Notes |
|------------------------|-------------------|-------|
| `random.random()` | `workflow.random().random()` | Returns seeded Random instance |
| `datetime.now()` | `workflow.now()` | Returns workflow's logical time |
| `datetime.utcnow()` | `workflow.utcnow()` | Returns workflow's UTC time |
| `time.time()` | `workflow.now().timestamp()` | Use workflow time |

Activities can use regular non-deterministic functions since they're not subject to the same restrictions.

Example:
```python
# Wrong - will fail in workflow
import random
from datetime import datetime

value = random.random()
timestamp = datetime.now()

# Correct - deterministic in workflow  
import temporalio.workflow as workflow

value = workflow.random().random()
timestamp = workflow.now()
```

