/**
 * Worker script that processes workflows and activities.
 */

import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';
import { resetPointMarkerActivity } from './reset-point-helper';

async function run() {
  // Create connection to Temporal server
  const connection = await NativeConnection.connect({
    address: 'localhost:7233',
  });

  // Create and run worker
  const worker = await Worker.create({
    connection,
    namespace: 'default',
    taskQueue: 'reset-child-ts',
    workflowsPath: require.resolve('./workflows'),
    activities: {
      ...activities,
      resetPointMarker: resetPointMarkerActivity,
    },
  });

  console.log('========================================');
  console.log('Financial Research Worker Started');
  console.log('========================================');
  console.log('Task Queue: reset-child-ts');
  console.log('Registered Workflows:');
  console.log('  - financialResearchWorkflow (parent)');
  console.log('  - marketAnalysisChildWorkflow');
  console.log('  - financialMetricsChildWorkflow');
  console.log('  - sentimentAnalysisChildWorkflow');
  console.log('  - riskAssessmentChildWorkflow');
  console.log('');
  console.log('Press Ctrl+C to stop...');
  console.log('========================================\n');
  
  await worker.run();
}

run().catch((err) => {
  console.error('Worker failed:', err);
  process.exit(1);
});

