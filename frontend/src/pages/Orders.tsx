import { useEffect, useState } from "react";
import OrderRow from "../components/OrderRow";

interface Order {
  id: string;
  client: string;
  date: string;
  status: string;
}


function Orders() {

    const [orders, setOrders] = useState<Order[] | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/binis_invoices/orders')
      .then(res => res.json())
      .then(data => setOrders(data))
  }, [])

  return (
  <>
      <nav className="fixed top-0 w-full z-50 bg-[#131313]/90 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
        <div className="flex justify-between items-center w-full px-8 h-16">
          <div className="flex items-center gap-12">
            <span className="text-xl font-bold tracking-tighter text-[#B32C3A] font-['Manrope']">
              Binis Invoices
            </span>
          </div>
          <div className="flex items-center gap-6">
            <div className="relative lg:block">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
                search
              </span>
              <input
                className="bg-surface-container-lowest border-none rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-1 focus:ring-primary-container w-64 transition-all"
                placeholder="Search orders..."
                type="text"
              />
            </div>
            <div className="flex items-center gap-4">
              <button className="p-2 text-gray-400 hover:bg-white/5 transition-all duration-300 rounded-lg active:scale-95">
                <span className="material-symbols-outlined">settings</span>
              </button>
            </div>
          </div>
        </div>
        <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-[#B32C3A]/20 to-transparent" />
      </nav>
      <main className="pt-32 px-8 max-w-[1600px] mx-auto pb-24">
        <header className="mb-16">
          <h1 className="text-6xl font-extrabold font-headline tracking-tighter mb-4 text-on-surface">
            Παραγγελίες
          </h1>
          <p className="text-on-surface-variant font-light tracking-wide max-w-2xl">
            Αυτόματη καταχώρηση προϊόντων και εξαγωγή τιμολογίων.
          </p>
        </header>

        <section className="bg-surface-container-low rounded-xl overflow-hidden border border-outline-variant/10">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-surface-container-lowest">
                  <th className="px-8 py-4 text-xs font-label uppercase tracking-widest text-on-surface-variant">
                    Παραγγελια
                  </th>
                  <th className="px-8 py-4 text-xs font-label uppercase tracking-widest text-on-surface-variant">
                    Πελατης
                  </th>
                  <th className="px-8 py-4 text-xs font-label uppercase tracking-widest text-on-surface-variant">
                    Ημερομηνια
                  </th>

                  <th className="px-8 py-4 text-xs font-label uppercase tracking-widest text-on-surface-variant">
                    κατασταση
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/5">
                {
                  orders?.map((order: Order) => {
                    return(
                      < OrderRow
                        order_id={order.id}
                        client={order.client}
                        date={order.date}
                        status={order.status}
                      />
                    )
                  })
                }
                {/* Order Rows */}
              </tbody>
            </table>
          </div>
        </section>
      </main>
      <footer className="w-full py-12 mt-20 border-t border-[#B32C3A]/10 bg-[#0E0E0E]">
        <div className="flex flex-col md:flex-row justify-between items-center px-12 max-w-7xl mx-auto gap-4">
          <div className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest">
            © developed by petros binis
          </div>
          <div className="flex items-center gap-8">
            <a
              className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest hover:text-[#B32C3A] transition-colors"
              href="#"
            >
              Privacy
            </a>
            <a
              className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest hover:text-[#B32C3A] transition-colors"
              href="#"
            >
              Terms
            </a>
            <a
              className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest hover:text-[#B32C3A] transition-colors"
              href="#"
            >
              Support
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}

export default Orders;