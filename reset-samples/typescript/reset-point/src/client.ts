/**
 * Client script to start a workflow.
 */

import { Connection, Client } from '@temporalio/client';
import { orderWorkflow } from './workflows';

async function run() {
  // Connect to Temporal server
  const connection = await Connection.connect({
    address: 'localhost:7233',
  });

  const client = new Client({
    connection,
    namespace: 'default',
  });

  // Start workflow
  const workflowId = `ts-order-${Date.now()}`;
  
  console.log(`Starting workflow with ID: ${workflowId}`);

  const handle = await client.workflow.start(orderWorkflow, {
    taskQueue: 'reset-point-ts',
    workflowId,
    args: ['ORD-001'],
  });

  console.log(`Started workflow: ${handle.workflowId}`);
  console.log(`Run ID: ${await handle.firstExecutionRunId}`);

  // Wait for result
  const result = await handle.result();
  console.log(`Workflow result: ${result}`);
  
  console.log('\nWorkflow completed successfully!');
  console.log('You can now reset this workflow to a specific point using:');
  console.log(`  temporal workflow reset --workflow-id ${workflowId} --reset-point after-validation`);
  console.log(`  temporal workflow reset --workflow-id ${workflowId} --reset-point after-payment`);
}

run().catch((err) => {
  console.error('Client failed:', err);
  process.exit(1);
});

