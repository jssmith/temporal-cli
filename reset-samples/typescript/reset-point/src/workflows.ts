/**
 * Order workflow demonstrating reset points.
 */

import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';
import { recordResetPoint } from './reset-point-helper';

const { validateOrder, processPayment, shipOrder } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10s',
});

/**
 * Demonstrates using reset points for workflow checkpointing.
 * 
 * Reset points allow you to reset a workflow to a specific named point
 * in its execution history.
 */
export async function orderWorkflow(orderId: string): Promise<string> {
  console.log(`Order workflow started for ${orderId}`);

  // Step 1: Validate order
  const validationResult = await validateOrder(orderId);
  console.log(`Order validated: ${validationResult}`);

  // RESET POINT: Can reset to here if payment fails
  await recordResetPoint('after-validation');

  // Step 2: Process payment
  const paymentResult = await processPayment(orderId);
  console.log(`Payment processed: ${paymentResult}`);

  // RESET POINT: Can reset to here if shipping fails
  await recordResetPoint('after-payment');

  // Step 3: Ship order
  const shippingResult = await shipOrder(orderId);
  console.log(`Order shipped: ${shippingResult}`);

  return `Order completed: ${orderId}`;
}

