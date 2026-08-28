/**
 * The only place the Shop talks to OrderCore.
 *
 * Requests go to /api/... and Vite proxies them to OrderCore. The target port
 * lives in vite.config.js and nowhere else.
 * Keeping every call here means a Week 3 API change touches one file.
 */

const BASE = '/api';

async function request(path) {
  const response = await fetch(`${BASE}${path}`);
  if (!response.ok) {
    throw new Error(`OrderCore returned ${response.status} for ${path}`);
  }
  return response.json();
}

export function listOrders() {
  return request('/orders');
}

export function getOrder(orderId) {
  return request(`/orders/${orderId}`);
}

export function getInvoice(orderId) {
  return request(`/orders/${orderId}/invoice`);
}

/** Money always crosses the wire as whole pence. Format only at the edge. */
export function formatPence(pence, currency = 'GBP') {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency,
  }).format(pence / 100);
}
