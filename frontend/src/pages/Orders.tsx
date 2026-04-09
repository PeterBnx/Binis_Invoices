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
    </>
  );
}

export default Orders;