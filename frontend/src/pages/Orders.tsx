import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import OrderRow from "../components/OrderRow";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface Order {
  id: string;
  client: string;
  date: string;
  price: string;
}

function Orders() {
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [reload, setReload] = useState<boolean>(false);

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`${API_BASE_URL}/binis_invoices/orders`, {
      headers: {
        "Authorization": `Token ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => setOrders(data));
  }, [reload]);


  const [isLoading, setIsLoading] = useState(false);

  const onOrderClick = (id: string): void => {
      setIsLoading(true);

      fetch(`${API_BASE_URL}/binis_invoices/orders/${id}`)
        .then(res => {
            if (!res.ok) throw new Error("Failed to fetch");
            return res.json();
        })
        .then(data => {
            navigate('/products_of_order', { state: { orderData: data } });
        })
        .catch(err => {
            console.error(err);
            alert("Σφάλμα κατά τη φόρτωση της παραγγελίας.");
        })
        .finally(() => {
            setIsLoading(false);
        });
    };

  const onReloadClick = () => {
    setOrders(null);
    const temp: boolean = reload;
    setReload(!temp);
  }

  return (
    <main className="max-w-[1600px] mx-auto p-6">
      <header className="mb-4">
        <h1 className="text-4xl font-extrabold tracking-tighter text-on-surface">
          Παραγγελίες
        </h1>
        <p className="text-on-surface-variant font-light tracking-wide max-w-2xl">
          Επιλέξτε μία από τις παρακάτω παραγγελίες
        </p>
      </header>

      {isLoading && (
        <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-surface-dark/80 backdrop-blur-md">
            {/* Simple CSS Spinner */}
            <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin mb-4"></div>
            <p className="text-on-surface font-medium animate-pulse tracking-widest uppercase text-xs">
                Φoρτωση Παραγγελiας...
            </p>
        </div>
        )}

      <section className="bg-surface-container-low rounded-xl border border-outline-variant/10 shadow-xl">
        <div className="min-w-[900px] ">
          <table className="w-full table-auto border-separate border-spacing-0">
            <thead className="bg-surface-container-low">
              <tr>
                <th className="w-1/5 px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                  Παραγγελια
                </th>
                <th className="w-1/4 px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                  Πελατης
                </th>
                <th className="w-1/4 px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                  Ημερομηνια
                </th>
                <th className="w-1/6 px-6 py-4 text-xs font-bold uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20 text-left">
                  Τιμη
                </th>
                <th className="w-[80px] border-b border-outline-variant/20" />
              </tr>
            </thead>
          </table>

          {/* Body */}
          <div className="h-[470px] overflow-auto">
            <table className="w-full table-auto border-separate border-spacing-0">
              <tbody className="divide-y divide-outline-variant/10">
                {!orders ? (
                  /* Loading State */
                  <tr><td colSpan={5} className="py-10 text-center">Φόρτωση...</td></tr>
                ) : orders.length === 0 ? (
                  /* Empty State */
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-on-surface-variant">
                      <p>Δεν βρέθηκαν παραγγελίες.</p>
                  <button className="px-4 py-2 m-4 cursor-pointer border border-gray-300 rounded hover:bg-gray-100"
                  onClick={() => onReloadClick()}>
                    Επαναφόρτωση
                      </button>
                    </td>
                  </tr>
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
