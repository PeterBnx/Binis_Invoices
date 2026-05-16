import { useEffect, useState } from "react";
import type { Order } from "../../electron/types/objects";
import { useNavigate } from "react-router-dom";
import OrderRow from "../components/OrderRow";
import Settings from "../components/Settings";
import { MdSettings } from "react-icons/md";

function Orders() {
  const [settingsView, setSettingsView] = useState<boolean>(false);
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [reload, setReload] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const unsubscribe = window.api.receive('socket_message', (message: any) => {
      if (message.type === "emp_orders") {
        console.log('[Orders] Received socket_message:', message);
        try {
          const data = typeof message === 'string' ? JSON.parse(message) : message;
          console.log('[Orders] Parsed data:', data);
          setOrders(Array.isArray(data.data) ? data.data : []);
          setIsLoading(false);
        } catch (e) {
          console.error('[Orders] Failed to parse message:', e);
          setOrders([]);
          setIsLoading(false);
        }
      } 
      else if (message.type === "empty_credentials") {
        // alert('Παρακαλώ ενημερώστε τους κωδικούς σας.')
        setSettingsView(true);
      }
      else if (message.type === "playwright_installed") {
        onReloadClick();
      }
      else return;
      });
    return unsubscribe;
  }, []);

  useEffect(() => {
    console.log('[Orders] Fetching orders...');
    window.api.invoke('get_orders').catch(e => {
      console.error('[Orders] Error:', e);
      setIsLoading(false);
    });
  }, [reload]);


  const onOrderClick = (id: string): void => {
    setIsLoading(true);
    navigate(`/productsOfOrderPage/${id}`);
  };

  const onReloadClick = () => {
    setOrders(null);
    const temp: boolean = reload;
    setReload(!temp);
  }

  return (
    <div>
      {settingsView && (
        <Settings onClose={() => {
          setSettingsView(false);
          onReloadClick();
        }}/>
      )}
    <main className="h-screen flex flex-col p-8 bg-[var(--bg-dark)] text-[var(--text)] overflow-hidden">
      <div className="max-w-6xl w-full mx-auto flex flex-col h-full">
        <header className="mb-8 flex-shrink-0 flex items-start justify-between">
          <div>
            <h1 className="text-5xl font-bold mb-2 text-[var(--text)] tracking-tight">
              Παραγγελίες
            </h1>
            <p className="text-lg text-[var(--text-muted)]">
              Επιλέξτε μία από τις παρακάτω παραγγελίες
            </p>
          </div>

          <div className="flex gap-4 items-center">
            <button
              onClick={() => setSettingsView(true)}
              className="p-2 rounded-xl bg-[var(--bg-dark)] border border-[var(--border-muted)] text-[var(--text-muted)] hover:text-[var(--primary)] hover:border-[var(--primary)] transition-all group"
              title="Ρυθμίσεις"
            >
              <MdSettings size={25}/>
            </button>

            {/* The New Action Button */}
            <button 
              onClick={onReloadClick} // or whatever action you need
              className="flex items-center gap-2 px-6 py-3 font-bold rounded-xl bg-[var(--primary)] text-[var(--bg-dark)] hover:opacity-90 active:scale-95 transition-all shadow-lg shadow-[var(--primary)]/10"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Ανανέωση
            </button>
          </div>
        </header>


        {isLoading && (
          <div className="fixed inset-0 z-50 flex flex-col items-center justify-center backdrop-blur-sm bg-black/60">
            <div className="w-16 h-16 border-4 rounded-full animate-spin mb-4 border-[var(--border-muted)] border-t-[var(--primary)]"></div>
            <p className="font-semibold tracking-wide animate-pulse text-[var(--text)]">
              Φόρτωση Παραγγελίας...
            </p>
          </div>
        )}
        <section className="flex-1 min-h-0 flex flex-col rounded-lg shadow-2xl bg-[var(--bg)] border border-[var(--border-muted)] overflow-hidden">
          
          <div className="overflow-y-auto h-full">
            <table className="w-full">
              <thead className="sticky top-0 z-10 bg-[var(--highlight)]">
                <tr>
                  {["παραγγελια", "πελατης", "ημερομηνια", "τιμη"].map((head) => (
                    <th key={head} className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-[var(--text)]">
                      {head}
                    </th>
                  ))}
                  <th className="px-6 py-4 w-12"></th>
                </tr>
              </thead>
              <tbody className="border-t border-[var(--border-muted)]">
                {!orders ? (
                  <tr>
                    <td colSpan={5} className="py-16 text-center text-[var(--text-muted)]">
                      Φόρτωση δεδομένων...
                    </td>
                  </tr>
                ) : orders.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-16 text-center">
                      <div className="flex flex-col items-center gap-4">
                        <p className="text-lg text-[var(--text-muted)]">Δεν βρέθηκαν παραγγελίες</p>
                        <button 
                          onClick={onReloadClick}
                          className="px-6 py-2 font-medium rounded-lg transition-colors duration-200 shadow-lg bg-[var(--primary)] text-[var(--bg-dark)] hover:opacity-90"
                          >
                          Επαναφόρτωση
                        </button>
                      </div>
                    </td>
                  </tr>
                ) : (
                  orders.map((order) => (
                    <OrderRow order_id={order.id} key={order.id} {...order} onClick={() => onOrderClick(order.id)} />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
      </div>
  );
}
export default Orders;
