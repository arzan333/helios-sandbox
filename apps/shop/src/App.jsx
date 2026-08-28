import { useEffect, useState } from 'react';
import { getInvoice, getOrder, listOrders } from './api.js';
import OrderDetail from './OrderDetail.jsx';
import OrderList from './OrderList.jsx';

export default function App() {
  const [orders, setOrders] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [order, setOrder] = useState(null);
  const [invoice, setInvoice] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    listOrders()
      .then((data) => {
        if (cancelled) return;
        setOrders(data);
        if (data.length > 0) setSelectedId(data[0].order_id);
      })
      .catch((exc) => {
        if (!cancelled) setError(`Could not reach OrderCore. ${exc.message}`);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) return undefined;
    let cancelled = false;
    setError(null);
    setInvoice(null);

    Promise.all([getOrder(selectedId), getInvoice(selectedId)])
      .then(([orderData, invoiceData]) => {
        if (cancelled) return;
        setOrder(orderData);
        setInvoice(invoiceData);
      })
      .catch((exc) => {
        if (!cancelled) setError(exc.message);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  return (
    <>
      <header className="masthead">
        <span className="masthead__mark">Helios</span>
        <span className="masthead__title">Shop &mdash; order review</span>
        <span className="masthead__env">Training environment</span>
      </header>

      <div className="layout">
        <section className="panel">
          <div className="panel__head">
            <span className="panel__title">Orders</span>
          </div>
          <OrderList orders={orders} selectedId={selectedId} onSelect={setSelectedId} />
        </section>

        <section className="panel">
          <div className="panel__head">
            <span className="panel__title">{order ? order.order_id : 'Order detail'}</span>
            {order && <span className={`badge badge--${order.status}`}>{order.status}</span>}
          </div>
          <div className="panel__body">
            <OrderDetail order={order} invoice={invoice} error={error} />
          </div>
        </section>
      </div>
    </>
  );
}
