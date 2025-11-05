/**
 * Activities for the order workflow.
 */

/**
 * Validate an order.
 */
export async function validateOrder(orderId: string): Promise<string> {
  console.log(`Validating order ${orderId}`);
  // Simulate validation work
  await new Promise((resolve) => setTimeout(resolve, 100));
  return `Validated-${orderId}`;
}

/**
 * Process payment for an order.
 */
export async function processPayment(orderId: string): Promise<string> {
  console.log(`Processing payment for ${orderId}`);
  // Simulate payment processing
  await new Promise((resolve) => setTimeout(resolve, 100));
  return `Paid-${orderId}`;
}

/**
 * Ship an order.
 */
export async function shipOrder(orderId: string): Promise<string> {
  console.log(`Shipping order ${orderId}`);
  // Simulate shipping
  await new Promise((resolve) => setTimeout(resolve, 100));
  return `Shipped-${orderId}`;
}

