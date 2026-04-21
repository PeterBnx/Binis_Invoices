import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import OrderRow from "../components/OrderRow";

interface Order {
  id: string;
  client: string;
  date: string;
  price: string;
}

function Orders() {
  const [orders, setOrders] = useState<Order[] | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/binis_invoices/orders")
      .then((res) => res.json())
      .then((data) => setOrders(data));
  }, []);

  const onOrderClick = (id: string): void => {
    navigate('/products_of_order');
    fetch(`http://localhost:8000/binis_invoices/orders/${id}`)
      .then(res => res.json())
      .then(data => {console.log(data); navigate('/products_of_order', { state: { orderData: data } })})
  }

  return (
    <main className="max-w-[1600px] mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold tracking-tighter mb-4 text-on-surface">
          Παραγγελίες
        </h1>
        <p className="text-on-surface-variant font-light tracking-wide max-w-2xl">
          Επιλέξτε μία από τις παρακάτω παραγγελίες
        </p>
      </header>

      <section className="bg-surface-container-low rounded-xl border border-outline-variant/10 shadow-xl">
        {/* Scroll container */}
        <div className="h-[600px] overflow-auto">
          {/* Prevent layout breaking on small widths */}
          <div className="min-w-[900px]">
            <table className="w-full table-fixed border-separate border-spacing-0">
              <thead>
                <tr>
                  <th className="w-1/5 sticky top-0 z-10 bg-surface-container-low px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                    Παραγγελια
                  </th>
                  <th className="w-1/4 sticky top-0 z-10 bg-surface-container-low px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                    Πελατης
                  </th>
                  <th className="w-1/4 sticky top-0 z-10 bg-surface-container-low px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                    Ημερομηνια
                  </th>
                  <th className="w-1/6 sticky top-0 z-10 bg-surface-container-low px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                    Τιμη
                  </th>
                  <th className="w-[80px] sticky top-0 z-10 bg-surface-container-low border-b border-outline-variant/20" />
                </tr>
              </thead>

              <tbody className="divide-y divide-outline-variant/10">
                {!orders ? (
                  /* Loading State */
                  <tr><td colSpan={5} className="py-10 text-center">Φόρτωση...</td></tr>
                ) : orders.length === 0 ? (
                  /* Empty State */
                  <tr><td colSpan={5} className="py-10 text-center text-on-surface-variant">Δεν υπάρχουν δεδομένα.</td></tr>
                ) : (
                  /* Data State */
                  orders.map((order) => (
                    <OrderRow order_id={order.id} key={order.id} {...order} onClick={() => onOrderClick(order.id)} />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Orders;
