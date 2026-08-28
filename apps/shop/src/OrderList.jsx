export default function OrderList({ orders, selectedId, onSelect }) {
  if (orders.length === 0) {
    return <p className="empty">No orders loaded.</p>;
  }

  return (
    <ul className="order-list">
      {orders.map((order) => (
        <li key={order.order_id}>
          <button
            type="button"
            className="order-list__item"
            aria-current={order.order_id === selectedId}
            onClick={() => onSelect(order.order_id)}
          >
            <div className="order-list__id">{order.order_id}</div>
            <div className="order-list__customer">{order.customer}</div>
            <span className={`badge badge--${order.status}`}>{order.status}</span>
          </button>
        </li>
      ))}
    </ul>
  );
}
