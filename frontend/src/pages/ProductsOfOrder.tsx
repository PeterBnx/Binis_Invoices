import {  useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

interface Product {
  quantity: number;
  code: string;
  description: string;
  price: string;
  isRegistered: boolean;
  brandFull: string;
  brandShort: string;
}

type GroupedProducts = {
    [brand: string]: Product[];
};

function ProductsOfOrder() {
    const location = useLocation();
    const orderData = useMemo(() => location.state?.orderData || [], [location.state?.orderData]);    
    const [data, setData] = useState<Product[]>(orderData);
    
    useEffect(() => {
        setData(orderData);
    }, [orderData]);

    const groupedData = useMemo(() => {
        return data.reduce((acc: GroupedProducts, product: Product) => {
            const brand = product.brandShort || 'Δεν Βρέθηκε';
            if (!acc[brand]) acc[brand] = [];
            acc[brand].push(product);
            return acc;
        }, {});
    }, [data]);

    const updateQuantity = (productCode: string, amount: number, isDirectSet: boolean = false) => {
        setData(prev => prev.map(p => {
            if (p.code === productCode) {
                let newQty;
                if (isDirectSet) {
                    newQty = Math.max(0, Math.min(1000, amount));
                } else {
                    newQty = Math.max(0, Math.min(1000, (p.quantity || 0) + amount));
                }
                return { ...p, quantity: newQty };
            }
            return p;
        }));
    };

    const updateProduct = (productCode: string, key: keyof Product, value: string) => {
    setData(prev => prev.map(p => {
        if (p.code === productCode) {
            return { ...p, [key]: value };
        }
        return p;
        }));
    };

    const updateBrand = (brandName: string, value: string) => {
        setData(prev => prev.map(p => {
            if (p.brandShort === brandName) {
                const productType = p.description.split(" ")[0];
                return {...p, ['brandShort']: value.trim(), ['description']: productType + ' ' + value.trim()};
            }
            return p;
        }))
    }
    
return (
    <main className="px-8 max-w-[1600px] mx-auto pb-24">
        {/* Header Section */}
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
                            <p className="text-2xl font-black text-on-surface">
                                {Object.values(groupedData).flat().length.toLocaleString()}
                            </p>
                        </div>
                        <div>
                            <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">Mismatches</p>
                            <p className="text-2xl font-black text-rose-600">04</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Right Column: Tables Grouped by Brand */}
            <div className="lg:col-span-9 space-y-12">
                {Object.entries(groupedData).map(([brandName, products]) => (
                    <section key={brandName} className="bg-surface-container-low rounded-xl overflow-hidden border border-outline-variant/10">
                        {/* Brand Sub-header */}
                        <div className="bg-surface-container-lowest px-8 py-4 border-b border-outline-variant/10 flex justify-between items-center">
                            <h2 
                                contentEditable 
                                suppressContentEditableWarning
                                onBlur={(e) => {
                                    const newBrandName = e.currentTarget.textContent || "";
                                    updateBrand(brandName, newBrandName);
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        (e.target as HTMLElement).blur();
                                    }
                                }}
                                className="
                                    text-sm font-bold p-1 uppercase tracking-widest text-primary 
                                    flex items-center rounded-md transition-all 
                                    cursor-text outline-none
                                    hover:bg-primary/10 
                                    focus:bg-primary/10 focus:ring-1 focus:ring-primary/30
                                    border border-primary
                                "
                            >
                                <span className="outline-none">{brandName}</span>
                            </h2>
                            <span className="text-[10px] font-bold uppercase text-on-surface-variant opacity-50">
                                {products.length} {products.length === 1 ? 'ειδος' : 'ειδη'}
                            </span>
                        </div>

                        {/* Scrollable Table Container */}
                      <div className="overflow-y-auto max-h-[500px] relative rounded-b-xl">
                        <table className="w-full text-left border-separate border-spacing-0">
                            <thead className="sticky top-0 z-20">
                                <tr>
                                    <th className="sticky top-0 bg-[#1c1b1f] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">ποσοτητα</th>                                
                                    <th className="sticky top-0 bg-[#1c1b1f] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">κωδικος</th>
                                    <th className="sticky top-0 bg-[#1c1b1f] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">περιγραφη</th>
                                    <th className="sticky top-0 bg-[#1c1b1f] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/20">τιμη</th>
                                    <th className="sticky top-0 bg-[#1c1b1f] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-on-surface-variant text-center border-b border-outline-variant/20">καταχωρημενο</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-outline-variant/5">
                                {products.map((product, pIdx) => (
                                    <tr key={pIdx} className="hover:bg-white/[0.05] transition-colors group">
                                        {/* Editable Quantity */}
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1 group/stepper">
                                        {/* Decrease Button */}
                                        <button 
                                            onClick={() => updateQuantity(product.code, -1)}
                                            className="w-8 h-8 flex items-center justify-center rounded-md border border-primary/20 text-primary hover:bg-primary/10 transition-all active:scale-90"
                                        >
                                            <span className="material-symbols-outlined text-sm">remove</span>
                                        </button>

                                        {/* The Value Display */}
                                        <div 
                                            contentEditable 
                                            suppressContentEditableWarning
                                            onBlur={(e) => {
                                                const text = e.currentTarget.textContent || "0";
                                                let val = parseInt(text);
                                                if (isNaN(val) || val < 0) val = 0;
                                                if (val > 1000) val = 1000;
                                                e.currentTarget.textContent = val.toString();
                                                updateQuantity(product.code, val, true);
                                            }}
                                            className="w-16 text-center text-sm font-mono font-bold p-1 text-on-surface/70 rounded-md transition-all cursor-text outline-none hover:bg-primary/10 focus:bg-primary/10 focus:ring-1 focus:ring-primary/30 border border-primary"
                                        >
                                            {product.quantity}
                                        </div>

                                        {/* Increase Button */}
                                        <button 
                                            onClick={() => updateQuantity(product.code, 1)}
                                            className="w-8 h-8 flex items-center justify-center rounded-md border border-primary/20 text-primary hover:bg-primary/10 transition-all active:scale-90"
                                        >
                                            <span className="material-symbols-outlined text-sm">add</span>
                                        </button>
                                    </div>
                                </td>

                                        {/* Code */}
                                        <td className="px-4 py-3">
                                            <div 
                                                contentEditable 
                                                suppressContentEditableWarning
                                                className="text-sm font-semibold p-1 text-on-surface rounded-md transition-all cursor-text outline-none 
                                                hover:bg-primary/10 focus:bg-primary/10 focus:ring-1 focus:ring-primary/30 border border-transparent hover:border-primary/30 
                                                focus:border-primary min-w-[175px] max-w-[175px] whitespace-normal break-words block
                                                "
                                                onBlur={(e) => {
                                                    const newText = e.currentTarget.textContent || "";
                                                    updateProduct(product.code, 'code', newText);
                                                }}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter' && !e.shiftKey) {
                                                        e.preventDefault();
                                                        (e.target as HTMLElement).blur();
                                                    }
                                                }}
                                            >
                                                {product.code}
                                            </div>
                                        </td>

                                        {/* Description */}
                                        <td className="px-4 py-3 align-top">
                                            <div 
                                                contentEditable 
                                                suppressContentEditableWarning
                                                className="text-sm font-semibold p-1 text-on-surface rounded-md transition-all cursor-text outline-none 
                                                        hover:bg-primary/10 focus:bg-primary/10 focus:ring-1 focus:ring-primary/30 
                                                        border border-transparent hover:border-primary/30 focus:border-primary 
                                                        min-w-[175px] max-w-[175px] whitespace-normal break-words block"
                                                onBlur={(e) => {
                                                    const newText = e.currentTarget.textContent || "";
                                                    updateProduct(product.code, 'description', newText);
                                                }}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter' && !e.shiftKey) {
                                                        e.preventDefault();
                                                        (e.target as HTMLElement).blur();
                                                    }
                                                }}
                                            >
                                                {product.description}
                                            </div>
                                        </td>

                                        {/* Editable Price */}
                                        <td className="px-4 py-3">
                                            <div 
                                                contentEditable 
                                                suppressContentEditableWarning
                                                className="text-sm font-semibold p-1 text-on-surface rounded-md transition-all cursor-text outline-none 
                                                hover:bg-primary/10 focus:bg-primary/10 focus:ring-1 focus:ring-primary/30 border border-transparent hover:border-primary/30 
                                                focus:border-primary min-w-[100px] max-w-[100px] whitespace-normal break-words block
                                                "
                                                onBlur={(e) => {
                                                    const newText = e.currentTarget.textContent || "";
                                                    updateProduct(product.code, 'price', newText);
                                                }}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter' && !e.shiftKey) {
                                                        e.preventDefault();
                                                        (e.target as HTMLElement).blur();
                                                    }
                                                }}
                                            >
                                                €{product.price}
                                            </div>
                                        </td>

                                        {/* Toggleable Boolean Status */}
                                        <td className="px-4 py-3 text-center">
                                            <div 
                                                className={`inline-block text-xs font-bold p-2 uppercase rounded-md transition-all 
                                                ${product.isRegistered 
                                                    ? "text-emerald-300 bg-success/20"
                                                    : "text-rose-300 bg-error/20"
                                                }`}
                                            >
                                                {product.isRegistered ? "ναι" : "οχι"}
                                            </div>
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