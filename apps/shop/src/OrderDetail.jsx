import { formatPence } from './api.js';

export default function OrderDetail({ order, invoice, error }) {
  if (!order) {
    return <p className="empty">Select an order to see its lines and invoice.</p>;
  }

  return (
    <>
      <table className="lines">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Description</th>
            <th className="num">Qty</th>
            <th className="num">Unit</th>
            <th className="num">Line total</th>
          </tr>
        </thead>
        <tbody>
          {order.lines.map((line) => (
            <tr key={line.sku}>
              <td>{line.sku}</td>
              <td>{line.description}</td>
              <td className="num">{line.quantity}</td>
              <td className="num">{formatPence(line.unit_price_pence, order.currency)}</td>
              <td className="num">
                {formatPence(line.quantity * line.unit_price_pence, order.currency)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {invoice && (
        <div className="totals">
          <div className="totals__row">
            <span className="totals__label">Subtotal</span>
            <span>{formatPence(invoice.subtotal_pence, invoice.currency)}</span>
          </div>
          <div className="totals__row">
            <span className="totals__label">VAT</span>
            <span>{formatPence(invoice.tax_pence, invoice.currency)}</span>
          </div>
          <div className="totals__row totals__row--grand">
            <span>Total</span>
            <span>{formatPence(invoice.total_pence, invoice.currency)}</span>
          </div>
        </div>
      )}

      {invoice && invoice.source === 'fallback' && (
        <p className="notice">
          Billing service unavailable. Totals were calculated by OrderCore instead.
        </p>
      )}

      {error && <p className="notice notice--error">{error}</p>}
    </>
  );
}
