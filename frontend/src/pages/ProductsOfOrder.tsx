import { useMemo, useRef, useState } from "react";
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

type Brand = {
    brandFull: string;
    brandShort: string;
}

function ProductsOfOrder() {
    const location = useLocation();
    const orderData = useMemo(() => location.state?.orderData || [], [location.state?.orderData]);    
    const [productsData, setProductsData] = useState<Product[]>(orderData.products);
    const [shippingTax, setShippingTax] = useState<string>(orderData.shippingTax);
    const [showInvoiceWarning, setShowInvoiceWarning] = useState<boolean>(false);
    const [productsNotRegistered, setProductsNotRegistered] = useState<Product[]>([]);
    const [extractionStatus, setExtractionStatus] = useState<Record<string, 'pending' | 'loading' | 'completed' | 'skipped'>>({});
    const [isExtracting, setIsExtracting] = useState(false);
    const [updatedBrands, setUpdatedBrands] = useState<Brand[]>([]);
    const [invoiceType, setInvoiceType] = useState<string>('tda');
    const [extractionFinished, setExtractionFinished] = useState<boolean>(false);
    const eventSourceRef = useRef<EventSource | null>(null);

    const groupedData = useMemo(() => {
        return productsData.reduce((acc: GroupedProducts, product: Product) => {
            const brand = product.brandShort || 'Δεν Βρέθηκε';
            if (!acc[brand]) acc[brand] = [];
            acc[brand].push(product);
            return acc;
        }, {});
    }, [productsData]);

    const updateQuantity = (productCode: string, amount: number, isDirectSet: boolean = false) => {
        setProductsData(prev => prev.map(p => {
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
        setProductsData(prev => prev.map(p => {
            if (p.code === productCode) {
                return { ...p, [key]: value };
            }
            return p;
        }));
    };

    const updateBrand = (brandName: string, newValue: string) => {
        const trimmedValue = newValue.trim();
        const nextProducts = productsData.map(p => {
            if (p.brandShort === brandName) {
                const productType = p.description.split(" ")[0];
                return { 
                    ...p, 
                    brandShort: trimmedValue, 
                    description: `${productType} ${trimmedValue}` 
                };
            }
            return p;
        });
        const matchingProduct = nextProducts.find(p => p.brandShort === trimmedValue);
        if (matchingProduct) {
            const brandToChange: Brand = {
                brandFull: matchingProduct.brandFull,
                brandShort: trimmedValue
            };

            const uniqueMap = new Map(
                [...updatedBrands, brandToChange].map(b => [b.brandFull, b])
            );
            const nextBrands = Array.from(uniqueMap.values());
            setProductsData(nextProducts);
            setUpdatedBrands(nextBrands);
        }
    };

    const log = () => {
        console.log(updatedBrands);
    }

    const updateShippingTax = (val: string) => {
        setShippingTax(val)
    }

    const onRegisterProducts = () => {
        setShowInvoiceWarning(false);
        log()
    }

    const onExtractInvoiceClick = async(checkProducts: boolean) => {
        const missingProducts = productsData.filter(p => !p.isRegistered);
        if (missingProducts.length > 0 && checkProducts) {
            setProductsNotRegistered(missingProducts);
            setShowInvoiceWarning(true);
            return;
        }

        setIsExtracting(true);
        setShowInvoiceWarning(false);
        
        try {
            const response = await fetch('http://localhost:8000/binis_invoices/store_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "products": productsData,
                    "client_name": orderData.clientName,
                    "client_afm": orderData.clientVAT,
                    "order_number": orderData.orderNumber,
                    "shipping_tax": shippingTax,
                    "updated_brands": updatedBrands,
                    "invoice_type": invoiceType,
                 }),
            });
            
            const { session_id } = await response.json();
            eventSourceRef.current = new EventSource(`http://localhost:8000/binis_invoices/extract_invoice/${session_id}`);

            eventSourceRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.code) {
                    setExtractionStatus(prev => ({
                        ...prev,
                        [data.code]: data.type === 'START' ? 'loading' : 
                                    data.type === 'COMPLETE' ? 'completed' : 'skipped'
                    }));
                }

                if (data.type === 'FINISHED') {
                    setIsExtracting(true);
                    setExtractionFinished(true);
                }
            };

            eventSourceRef.current.onerror = () => {
                onCloseWindow();
            };

        } catch (err) {
            console.error("Failed to initiate extraction", err);
            setIsExtracting(false);
        }
    };
    
    const onCloseWindow = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }
        setShowInvoiceWarning(false);
        setExtractionFinished(false);
        setIsExtracting(false);
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
                    Παραγγελία {orderData.orderNumber}
                </p>
            </div>
            <div className="flex gap-4">
                <button className="cursor-pointer px-6 py-3 border border-outline-variant/20 hover:bg-on-surface/5 transition-all text-sm font-semibold tracking-wide flex items-center gap-2 rounded-lg text-on-surface"
                onClick={() => onExtractInvoiceClick(true)}>
                    <span className="material-symbols-outlined text-sm">description</span>
                    Εξαγωγή Τιμολογίου
                </button>
                <button className="cursor-pointer px-6 py-3 bg-primary-container text-on-primary-container hover:opacity-90 transition-all text-sm font-semibold tracking-wide flex items-center gap-2 rounded-lg shadow-sm"
                    onClick={() => onRegisterProducts()}>
                    <span className="material-symbols-outlined text-sm">add_box</span>
                    Καταχώρηση Ειδών
                </button>
            </div>
        </header>

        {/* Invoice Warning Popup */}
        {showInvoiceWarning && (
        <div className="overscroll-none fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="relative bg-surface-container-high border border-outline-variant/20 p-8 rounded-2xl max-w-md w-full shadow-2xl animate-in fade-in zoom-in duration-200">

                <button 
                    onClick={() => setShowInvoiceWarning(false)}
                    className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full text-on-surface-variant hover:bg-white/10 hover:text-on-surface transition-all cursor-pointer"
                    aria-label="Close"
                >
                    <span className="material-symbols-outlined text-2xl">close</span>
                </button>

                {/* Header */}
                <div className="flex items-center gap-4 text-error mb-4 pr-8"> {/* Added padding-right so text doesn't hit the X */}
                    <span className="select-none material-symbols-outlined text-4xl">warning</span>
                    <h3 className="select-none text-xl font-bold text-on-surface">Εκκρεμεί Καταχώρηση</h3>
                </div>

                <p className="text-on-surface-variant mb-6 leading-relaxed">
                    Υπάρχουν {productsNotRegistered.length} είδη που δεν έχουν καταχωρηθεί ακόμα. Παρακαλώ ελέγξτε τα παρακάτω:
                </p>

                <div className="mb-8 overflow-hidden border border-outline-variant/10 rounded-xl bg-black/20">
                    <div className="max-h-48 overflow-y-auto p-4 custom-scrollbar">
                        <ul className="space-y-3">
                            {productsNotRegistered.map((product) => (
                                <li key={product.code} className="flex flex-col gap-1 pb-3 border-b border-outline-variant/5 last:border-0 last:pb-0">
                                    <div className="flex justify-between items-center">
                                        <span className="text-xs font-mono font-bold text-error bg-error/10 px-2 py-0.5 rounded">
                                            {product.code}
                                        </span>
                                        <span className="text-[10px] text-on-surface-variant uppercase font-medium">
                                            Ποσ: {product.quantity}
                                        </span>
                                    </div>
                                    <span className="text-xs text-on-surface/70 truncate italic">
                                        {product.description || "Χωρίς περιγραφή"}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                    <button 
                        onClick={() => onExtractInvoiceClick(false)}
                        className="cursor-pointer py-3 border border-on-primary-container text-on-primary-container font-bold rounded-lg hover:bg-white/5 transition-all text-sm"
                    >
                        Εξαγωγή Τιμολογίου
                    </button>
                    <button 
                        onClick={() => onRegisterProducts()}
                        className="cursor-pointer py-3 bg-primary text-white font-bold rounded-lg hover:opacity-90 active:scale-[0.98] transition-all text-sm"
                    >
                        Καταχώρηση Ειδών
                    </button>
                </div>
            </div>
        </div>
        )}

       {isExtracting && (
            <div className="overscroll-none fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-md p-4">
                <div className="relative bg-surface-container-high border border-outline-variant/30 p-8 rounded-2xl max-w-lg w-full shadow-2xl animate-in fade-in zoom-in duration-300">
                    
                    {/* Header with Global Spinner */}
                    <div className="flex items-center gap-5 mb-8">
                        <div className="relative">
                            <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-on-surface tracking-tight">Εξαγωγή Τιμολογίου</h3>
                            <p className="text-sm text-on-surface-variant flex items-center gap-2">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                                </span>
                                Παρακαλώ περιμένετε...
                            </p>
                        </div>
                    </div>

                    {/* Live Progress List */}
                    <div className="mb-8 border border-outline-variant/10 rounded-xl bg-black/40 shadow-inner">
                        <div className="max-h-[350px] overflow-y-auto p-2 custom-scrollbar">
                            <div className="space-y-1">
                                {productsData.map((product) => {
                                    const status = extractionStatus[product.code] || 'pending';
                                    return (
                                        <div 
                                            key={product.code} 
                                            className={`flex items-center justify-between p-3 rounded-lg transition-all ${
                                                status === 'loading' ? 'bg-primary/5 ring-1 ring-primary/20' : ''
                                            }`}
                                        >
                                            <div className="flex items-center gap-4">
                                                {/* Dynamic Status Icon */}
                                                <div className="flex items-center justify-center w-6">
                                                    {status === 'completed' && <span className="material-symbols-outlined text-emerald-400 scale-110">check_circle</span>}
                                                    {status === 'skipped' && <span className="material-symbols-outlined text-rose-400 animate-pulse">error</span>}
                                                    {status === 'pending' && <span className="w-2 h-2 bg-on-surface/20 rounded-full"></span>}
                                                    {status === 'loading' && <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>}
                                                </div>
                                                
                                                <div className="flex flex-col">
                                                    <span className={`text-sm font-mono font-bold tracking-wider ${
                                                        status === 'completed' ? 'text-emerald-400' : 
                                                        status === 'skipped' ? 'text-rose-400' : 'text-on-surface/40'
                                                    }`}>
                                                        {product.code}
                                                    </span>
                                                    <span className="text-[10px] text-on-surface-variant/60 truncate max-w-[200px]">
                                                        {product.description || "Προϊόν"}
                                                    </span>
                                                </div>
                                            </div>

                                            {/* Badge Status */}
                                            <div className="flex flex-col items-end">
                                                <span className={`text-[10px] font-black uppercase tracking-tighter px-2 py-1 rounded ${
                                                    status === 'completed' ? 'bg-emerald-500/10 text-emerald-500' : 
                                                    status === 'skipped' ? 'bg-rose-500/10 text-rose-500' : 'text-on-surface/20'
                                                }`}>
                                                    {status === 'completed' ? 'Done' : status === 'skipped' ? 'Skipped' : 'Waiting'}
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    {/* Bottom Note & Action */}
                    <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-3 bg-on-surface/5 p-4 rounded-xl">
                            <span className="material-symbols-outlined text-on-surface-variant text-lg">info</span>
                            <p className="text-[11px] text-on-surface-variant leading-tight flex-1">
                                Η διαδικασία είναι αυτοματοποιημένη. Παρακαλώ μην ανανεώσετε τη σελίδα μέχρι να ολοκληρωθεί η λήψη του στιγμιότυπου.
                            </p>
                            
                            {/* The Close Button */}
                            { extractionFinished && <button 
                                onClick={() => onCloseWindow()}
                                className="px-4 py-2 border border-error text-xs font-bold uppercase tracking-wider text-on-surface cursor-pointer hover:bg-on-surface/10 rounded-lg transition-colors"
                            >
                                κλεισιμο
                            </button>}
                        </div>
                    </div>
                </div>
            </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Column: Stats Cards */}
            <aside className="lg:col-span-3 space-y-6">
                {/* Statistics Card */}
                <div className="bg-surface-container-high p-6 rounded-xl border border-outline-variant/10">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">ειδη</p>
                            <p className="text-2xl font-black text-on-surface">
                                {Object.values(groupedData).flat().length.toLocaleString()}
                            </p>
                        </div>
                        <div>
                            <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">λειπουν</p>
                            <p className=" text-2xl font-black text-rose-600">
                                {productsData.filter(p => !p.isRegistered).length}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Order & Client Details Card */}
                <div className="bg-surface-container-high p-6 rounded-xl border border-outline-variant/10 space-y-4">                                         
                    <div>
                        <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">πελατης</p>
                        <p className="text-base font-bold text-on-surface">{orderData.clientName}</p>
                    </div>

                    <div>
                        <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">ΑΦΜ</p>
                        <p className="text-sm font-medium text-on-surface">{orderData.clientVAT}</p>
                    </div>

                    <div>
                        <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">
                            εξοδα αποστολης
                        </p>
                        <div className="flex items-center gap-1 text-sm font-medium text-on-surface">
                            <span>&#8364;</span>
                            <div 
                            contentEditable 
                            suppressContentEditableWarning
                            onBlur={(e) => {
                                const text = e.currentTarget.textContent || "0";
                                let val = parseFloat(text);
                                if (isNaN(val) || val < 0) val = 0;
                                if (val > 10000) val = 10000;
                                e.currentTarget.textContent = val.toString();
                                updateShippingTax(val.toString());
                            }}
                            className="inline-block min-w-[4rem] text-center text-sm font-mono font-bold p-1 text-on-surface rounded-md transition-all cursor-text outline-none hover:bg-primary/10 focus:bg-primary/10 focus:ring-1 focus:ring-primary/30 border border-primary"
                            >
                            {shippingTax}
                            </div>
                        </div>
                    </div>
                    <div>
                    <p className="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-1">
                        ΤΥΠΟΣ ΤΙΜΟΛΟΓΙΟΥ
                    </p>
                    <div className="flex items-center gap-1 text-sm font-medium text-on-surface">
                        <select 
                        name="invoice_type" 
                        title="invoice_type"
                        className="bg-transparent border border-primary rounded-md p-1 outline-none focus:ring-1 focus:ring-primary/30"
                        value={invoiceType}
                        onChange={(e) => setInvoiceType(e.target.value)}
                        >
                        <option value="tda">ΤΔΑ</option>
                        <option value="inve">INVE</option>
                        </select>
                    </div>
                    </div>
                </div>
            </aside>

            {/* Products */}
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

                                        {/* Price */}
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