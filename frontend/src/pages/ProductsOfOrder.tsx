import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

interface Product {
  quantity: string;
  code: string;
  description: string;
  price: string;
  isRegistered: string;
}

// Mock data structured by brand as requested
const INITIAL_DATA = [
    {
        brand: "Titan Industrial",
        products: [
            { id: 1, code: "EA-2024-X1-A", desc: "Primary Strut Assembly", price: "4,280.00", isRegistered: "Registered" },
            { id: 2, code: "EA-2024-X1-D", desc: "Anchor Pivot Bolt", price: "45.00", isRegistered: "Registered" },
        ]
    },
    {
        brand: "Apex Hydraulics",
        products: [
            { id: 3, code: "EA-2024-X1-B", desc: "Hydraulic Valve Core", price: "1,150.00", isRegistered: "Pending Sync" },
        ]
    }
];

function ProductsOfOrder() {
    const location = useLocation();
    const fetchedData = location.state?.orderData;
    const [brands, setBrands] = useState(INITIAL_DATA);

    useEffect(() => {
        if (fetchedData) {
            // Logic to transform your backend data to match the UI structure
            // This assumes 'fetchedData' is an array or object containing your products
            console.log("Received data:", fetchedData);
            
            // If your API returns the exact structure needed:
            // setBrands(fetchedData); 
            
            // Otherwise, map your API response here to match the brand/product structure
        }
    }, [fetchedData]);

    return (
        <main className="px-8 max-w-[1600px] mx-auto pb-24">
            {/* Header Section matching Orders.tsx */}
            <header className="mb-16 mt-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <h1 className="text-6xl font-extrabold font-headline tracking-tighter mb-4 text-on-surface">
                        Λεπτομέρειες Παραγγελίας
                    </h1>
                    <p className="text-on-surface-variant font-light tracking-wide max-w-2xl">
                        Επεξεργασία προϊόντων ανά κατασκευαστή και έλεγχος στοιχείων.
                    </p>
                </div>
                <div className="flex gap-4">
                    <button className="px-6 py-3 border border-outline-variant/20 hover:bg-on-surface/5 transition-all text-sm font-semibold tracking-wide flex items-center gap-2 rounded-lg text-on-surface">
                        <span className="material-symbols-outlined text-sm">description</span>
                        Invoice Extractor
                    </button>
                    <button className="px-6 py-3 bg-primary-container text-on-primary-container hover:opacity-90 transition-all text-sm font-semibold tracking-wide flex items-center gap-2 rounded-lg shadow-sm">
                        <span className="material-symbols-outlined text-sm">add_box</span>
                        Εισαγωγή Προϊόντος
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Column: Stats Cards */}
                <aside className="lg:col-span-3 space-y-6">
                    <div className="bg-surface-container-high p-6 rounded-xl border border-outline-variant/10">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">Items</p>
                                <p className="text-2xl font-black text-on-surface">1,248</p>
                            </div>
                            <div>
                                <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">Mismatches</p>
                                <p className="text-2xl font-black text-error">04</p>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Right Column: Tables Grouped by Brand */}
                <div className="lg:col-span-9 space-y-12">
                    {brands.map((brandGroup, idx) => (
                        <section key={idx} className="bg-surface-container-low rounded-xl overflow-hidden border border-outline-variant/10">
                            {/* Brand Sub-header */}
                            <div className="bg-surface-container-lowest px-8 py-4 border-b border-outline-variant/10 flex justify-between items-center">
                                <h2 className="text-sm font-bold uppercase tracking-widest text-primary flex items-center gap-3">
                                    <span className="w-6 h-[2px] bg-primary"></span>
                                    {brandGroup.brand}
                                </h2>
                                <span className="text-[10px] font-bold text-on-surface-variant opacity-50">
                                    {brandGroup.products.length} 
                                </span>
                            </div>

                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="bg-surface-container-lowest/50">
                                            <th className="px-8 py-3 text-xs font-label uppercase tracking-widest text-on-surface-variant">κωδικος</th>
                                            <th className="px-8 py-3 text-xs font-label uppercase tracking-widest text-on-surface-variant">περιγραφη</th>
                                            <th className="px-8 py-3 text-xs font-label uppercase tracking-widest text-on-surface-variant">τιμη</th>
                                            <th className="px-8 py-3 text-xs font-label uppercase tracking-widest text-on-surface-variant text-right">κατασταση</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-outline-variant/5">
                                        {brandGroup.products.map((product) => (
                                            <tr key={product.id} className="hover:bg-on-surface/[0.02] transition-colors group">
                                                {/* Editable Code */}
                                                <td 
                                                    contentEditable 
                                                    suppressContentEditableWarning
                                                    className="px-8 py-5 font-mono font-bold text-primary focus:bg-surface-container-highest focus:outline-none"
                                                >
                                                    {product.code}
                                                </td>

                                                {/* Editable Description */}
                                                <td className="px-8 py-5">
                                                    <p 
                                                        contentEditable 
                                                        suppressContentEditableWarning
                                                        className="font-semibold text-on-surface focus:outline-none"
                                                    >
                                                        {product.desc}
                                                    </p>
                                                </td>

                                                {/* Editable Price */}
                                                <td className="px-8 py-5 font-medium text-on-surface">
                                                    <span className="mr-0.5">$</span>
                                                    <span 
                                                        contentEditable 
                                                        suppressContentEditableWarning 
                                                        className="focus:outline-none"
                                                    >
                                                        {product.price}
                                                    </span>
                                                </td>

                                                {/* Status (Non-editable badge) */}
                                                <td className="px-8 py-5 text-right">
                                                    <span className={`inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-tight ${
                                                        product.isRegistered === 'Registered' ? 'text-primary' : 'text-tertiary'
                                                    }`}>
                                                        <span className={`w-1.5 h-1.5 rounded-full ${
                                                            product.isRegistered === 'Registered' ? 'bg-primary' : 'bg-tertiary animate-pulse'
                                                        }`} />
                                                        {product.isRegistered}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    ))}
                </div>
            </div>
        </main>
    );
}

export default ProductsOfOrder;