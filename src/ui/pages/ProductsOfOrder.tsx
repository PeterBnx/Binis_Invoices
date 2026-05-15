/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { MdAdd, MdError, MdOutlineRemove } from "react-icons/md";
import type { OrderData } from "../../electron/types/objects";
import { FaCheckCircle, FaFileInvoice } from "react-icons/fa";
import { IoMdAddCircleOutline, IoMdArrowBack } from "react-icons/io";
import { IoCheckmark, IoCloseCircle, IoInformationCircleOutline, IoWarning } from "react-icons/io5";
import { CiCircleCheck } from "react-icons/ci";


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
    const { id } = useParams();
    const [orderData, setOrderData] = useState<OrderData>({
        orderNumber : 'Δεν Βρέθηκε',
        products : [],
        shippingTax : '0.00',
        clientVAT : 'Δεν Βρέθηκε',
        clientName: 'Δεν Βρέθηκε'
    });
    const [productsData, setProductsData] = useState<Product[]>([]);
    const [showInvoiceWarning, setShowInvoiceWarning] = useState<boolean>(false);
    const [productsNotRegistered, setProductsNotRegistered] = useState<Product[]>([]);
    const [extractionStatus, setExtractionStatus] = useState<Record<string, 'pending' | 'loading' | 'completed' | 'skipped'>>({});
    const [isExtracting, setIsExtracting] = useState(false);
    const [isRegisteringProducts, setIsRegisteringProducts] = useState(false);
    const [registerStatus, setRegisterStatus] = useState<Record<string, 'pending' | 'loading' | 'completed' | 'skipped'>>({});
    const [updatedBrands, setUpdatedBrands] = useState<Brand[]>([]);
    const [extractionFinished, setExtractionFinished] = useState<boolean>(false);
    const [registeringFinished, setRegisteringFinished] = useState<boolean>(false);
    const [productsToRegister, setProductsToRegister] = useState<Product[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const navigate = useNavigate();

    useEffect(() => {
        const unsubscribe = window.api.receive('socket_message', (message: any) => {
            if (message?.type === "order_data") {
                try {
                    const raw = typeof message === 'string' ? JSON.parse(message) : message;
                    const payload = raw.data;
                    
                    if (!payload) return;
                    
                    const parsedData: OrderData = {
                        orderNumber: payload.order_number,
                        clientVAT: payload.client_afm,
                        shippingTax: payload.shipping_tax,
                        clientName: payload.client_name,
                        products: (payload.products || []).map((p: any) => {
                        const { is_registered, brand_full, brand_short, ...rest } = p;
                        return {
                            ...rest,
                            isRegistered: is_registered,
                            brandFull: brand_full,
                            brandShort: brand_short,
                        };
                    })
                };
                    console.log("Parsed Data: ", parsedData);
                    setOrderData(parsedData);
                    setProductsData(parsedData.products)
                    setIsLoading(false);
                } catch (e) {
                    console.error('[Products] Failed to parse message:', e);
                    setIsLoading(false);
                }
            } else if (message?.type === "register_products") {
                const code = message.data;
                if (code) {
                    setRegisterStatus(prev => ({
                        ...prev,
                        [code]: message.status === 'completed' ? 'completed' : 'skipped'
                    }));

                    setProductsData(prev => prev.map(product =>
                        product.code === code 
                        ? { ...product, isRegistered: message.status === 'completed' } 
                        : product
                    ));
                }}

            else if (message.type === 'registering_finished') {
                setRegisteringFinished(true);
            }
            else if (message.type === 'extract_invoice') {
                try {
                    const code = message.data;
                    if (code) {
                        setExtractionStatus(prev => ({
                            ...prev,
                            [code]: message.status === 'completed' ? 'completed' : 'skipped'
                        }));
                    }
                } catch (e) {
                    console.log(e);
                }
            }
            else if (message.type === 'invoice_extraction_finished') {
                setIsExtracting(true);
                setExtractionFinished(true);
            }
            else return;
        });

        return unsubscribe;
    }, []);

    useEffect(() => {
        console.log('[Products] Fetching products...');
        if (id) {
            window.api.invoke('get_order_data', ['get_order_data', id]).catch(e => {
                console.error('[Products] Error:', e);
                setIsLoading(false);
            });
        }
    }, [id]);

    const groupedData = useMemo(() => {
        return productsData.reduce((acc: GroupedProducts, product: Product) => {
            const brand = product.brandShort || 'Δεν Βρέθηκε';
            if (!acc[brand]) acc[brand] = [];
            acc[brand].push(product);
            return acc;
        }, {});
    }, [productsData]);

    const productsToUse = useMemo(() => {
        return productsData.filter((p) => p.quantity > 0);
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

    const updateShippingTax = (val: string) => {
        setOrderData((prev) => {
            return {
                ...prev,
                shippingTax: val
            };
        })
    }

    const onRegisterProducts = async() => {
        const missingProducts = productsData.filter(p => !p.isRegistered);
        if (missingProducts.length === 0) {
            console.log(`Missing  ${missingProducts.length}  products`)
            alert("Όλα τα είδη είναι καταχωρημένα.")
            return;
        }
        setProductsToRegister(missingProducts);
        setShowInvoiceWarning(false);
        setIsRegisteringProducts(true);
        try {
            console.log('[Products] Registering products...');
            window.api.invoke('register_products', JSON.stringify({ 
                    "products": missingProducts,
                    "order_number": orderData.orderNumber,
                    "updated_brands": updatedBrands,
                 })).catch(e => {
                console.error('[Register Products] Error:', e);
                setIsLoading(false);
            });
        } catch (err) {
            console.error("Failed to initiate product registering", err);
            setIsRegisteringProducts(false);
        }
    }

    const onExtractInvoiceClick = async(checkProducts: boolean) => {
        setExtractionStatus({});
        const missingProducts = productsData.filter(p => !p.isRegistered);
        if (missingProducts.length > 0 && checkProducts) {
            setProductsNotRegistered(missingProducts);
            setShowInvoiceWarning(true);
            return;
        }
        if (productsToUse.length === 0) {
            alert("Δεν υπάρχουν προϊόντα για εξαγωγή. Ελέγξτε τις ποσότητες για κάθε είδος.");
            return;
        }

        setIsExtracting(true);
        setShowInvoiceWarning(false);

        try {
            console.log('[Invoice] Extracting invoice...');
            window.api.invoke('extract_invoice', JSON.stringify({ 
                    "products": productsToUse,
                    "client_name": orderData.clientName,
                    "client_afm": orderData.clientVAT,
                    "order_number": orderData.orderNumber,
                    "shipping_tax": orderData.shippingTax,
                    "updated_brands": updatedBrands,
                 })).catch(e => {
                console.error('[Register Products] Error:', e);
                setIsLoading(false);
                onCloseExtractingWindow()
            });
            
        } catch (err) {
            console.error("Failed to initiate extraction", err);
            setIsExtracting(false);
        }
    };
    
    const onCloseExtractingWindow = () => {
        setShowInvoiceWarning(false);
        setExtractionFinished(false);
        setIsExtracting(false);
    }

    const onCloseRegisteringWindow = () => {
        setShowInvoiceWarning(false);
        setRegisteringFinished(false);
        setIsRegisteringProducts(false);
    }

    function onVisitLiveCis(): void {
       window.open('https://live.livecis.gr/live/Documents.aspx?tp=%u03a0%u03a9%u039b%u0397%u03a3%u0395%u0399%u03a3', '_blank', 'noreferrer');
    }
    if (isLoading) {
        return (
            <main className="h-screen w-screen flex flex-col items-center justify-center bg-[var(--bg-dark)]">
                <div className="relative flex items-center justify-center">
                    {/* Outer Ring */}
                    <div className="w-20 h-20 border-4 border-[var(--border-muted)] rounded-full"></div>
                    
                    {/* Spinning Top Ring */}
                    <div className="absolute w-20 h-20 border-4 border-t-[var(--primary)] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                    
                </div>

                <div className="mt-8 flex flex-col items-center gap-2">
                    <h2 className="text-2xl font-bold tracking-tight text-[var(--text)]">
                        Φόρτωση δεδομένων παραγγελίας
                    </h2>
                    <p className="text-[var(--text-muted)] animate-pulse">
                        Παρακαλώ περιμένετε...
                    </p>
                </div>
            </main>
        );
    }
    else return (
        <main className="h-screen flex flex-col p-8 bg-[var(--bg-dark)] text-[var(--text)] overflow-y-auto">
            <header className="mb-16 mx-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="mt-4">
                    <button 
                        onClick={() => navigate(`/ordersPage`)}
                        className="flex items-center gap-2 text-[var(--text-muted)] hover:text-[var(--primary)] transition-colors mb-6 group cursor-pointer"
                    >
                        <IoMdArrowBack className="text-xl group-hover:-translate-x-1 transition-transform" />
                        <span className="text-sm font-medium uppercase tracking-widest">πισω</span>
                    </button>

                    <h1 className="text-5xl font-bold mb-4 text-[var(--text)]">
                        Λεπτομέρειες Παραγγελίας
                    </h1>
                    <p className="text-[var(--text-muted)] font-light tracking-wide max-w-2xl">
                        Παραγγελία {orderData.orderNumber}
                    </p>
                </div>

                <div className="flex gap-4">
                    <button 
                        className="cursor-pointer px-6 py-3 border border-[var(--border-muted)] hover:bg-[var(--text)]/5 transition-all text-sm font-semibold tracking-wide flex items-center gap-2 rounded-lg text-[var(--text)]"
                        onClick={() => onExtractInvoiceClick(true)}
                    >
                        <FaFileInvoice className="text-lg" />
                        Εξαγωγή Τιμολογίου
                    </button>
                    <button 
                        className="cursor-pointer px-6 py-3 bg-[var(--primary)] text-[var(--bg-dark)] hover:opacity-90 transition-all text-sm font-semibold tracking-wide flex items-center gap-2 rounded-lg shadow-lg"
                        onClick={() => onRegisterProducts()}
                    >
                        <IoMdAddCircleOutline className="text-xl" />
                        Καταχώρηση Ειδών
                    </button>
                </div>
            </header>
            {/* Invoice Warning Popup */}
            {showInvoiceWarning && (
            <div className="overscroll-none fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                <div className="relative bg-[var(--bg)] border border-[var(--border-muted)] p-8 rounded-2xl max-w-md w-full shadow-2xl animate-in fade-in zoom-in duration-200">

                    <button 
                        onClick={() => setShowInvoiceWarning(false)}
                        className="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full text-[var(--text-muted)] hover:bg-white/10 hover:text-[var(--text)] transition-all cursor-pointer"
                        aria-label="Close"
                    >
                        <span className="material-symbols-outlined text-2xl"><IoCloseCircle /></span>
                    </button>

                    {/* Header */}
                    <div className="flex items-center gap-4 text-red-500 mb-4 pr-8"> {/* Added padding-right so text doesn't hit the X */}
                        <span className="select-none material-symbols-outlined text-4xl">
                            <IoWarning />   
                        </span>
                        <h3 className="select-none text-xl font-bold text-[var(--text)]">Εκκρεμεί Καταχώρηση</h3>
                    </div>

                    <p className="text-[var(--text-muted)] mb-6 leading-relaxed">
                        Υπάρχουν {productsNotRegistered.length} είδη που δεν έχουν καταχωρηθεί ακόμα. Παρακαλώ ελέγξτε τα παρακάτω:
                    </p>

                    <div className="mb-8 overflow-hidden border border-[var(--border-muted)] rounded-xl bg-black/20">
                        <div className="max-h-48 overflow-y-auto p-4 custom-scrollbar">
                            <ul className="space-y-3">
                                {productsNotRegistered.map((product) => (
                                    <li key={product.code} className="flex flex-col gap-1 pb-3 border-b border-[var(--border-muted)]/30 last:border-0 last:pb-0">
                                        <div className="flex justify-between items-center">
                                            <span className="text-xs font-mono font-bold text-red-500 bg-red-500/10 px-2 py-0.5 rounded">
                                                {product.code}
                                            </span>
                                            <span className="text-[10px] text-[var(--text-muted)] uppercase font-medium">
                                                Ποσ: {product.quantity}
                                            </span>
                                        </div>
                                        <span className="text-xs text-[var(--text)]/70 truncate italic">
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
                            className="cursor-pointer py-3 border border-[var(--primary)] text-[var(--primary)] font-bold rounded-lg hover:bg-[var(--primary)]/10 transition-all text-sm"
                        >
                            Εξαγωγή Τιμολογίου
                        </button>
                        <button 
                            onClick={() => onRegisterProducts()}
                            className="cursor-pointer py-3 bg-[var(--primary)] text-[var(--bg-dark)] font-bold rounded-lg hover:opacity-90 active:scale-[0.98] transition-all text-sm"
                        >
                            Καταχώρηση Ειδών
                        </button>
                    </div>
                </div>
            </div>
            )}

            {isRegisteringProducts && (
                <div className="overscroll-none fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-md p-4">
                    <div className="relative bg-[var(--bg)] border border-[var(--border-muted)] p-8 rounded-2xl max-w-lg w-full shadow-2xl animate-in fade-in zoom-in duration-300">
                        
                        {/* Header with Global Spinner */}
                        <div className="flex items-center gap-5 mb-8">
                            <div className="relative">
                                {
                                    !registeringFinished ? (
                                        <div className="w-12 h-12 border-4 border-[var(--border-muted)] border-t-[var(--primary)] rounded-full animate-spin"></div> 
                                    ) : (
                                        <div className="w-12 h-12 bg-emerald-500 rounded-full flex items-center justify-center animate-in zoom-in duration-300">
                                            <span className="material-symbols-outlined text-white text-3xl">
                                                <IoCheckmark />
                                            </span>
                                        </div>
                                        )
                                }
                            </div>
                            <div>
                                <h3 className="text-2xl font-black text-[var(--text)] tracking-tight">Καταχώρηση Ειδών</h3>
                                {!registeringFinished &&
                                    <p className="text-sm text-[var(--text-muted)] flex items-center gap-2">
                                        <span className="relative flex h-2 w-2">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--primary)] opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--primary)]"></span>
                                        </span>
                                        Παρακαλώ περιμένετε...
                                    </p>
                                }
                            </div>
                        </div>

                        {/* Live Progress List */}
                        <div className="mb-8 border border-[var(--border-muted)] rounded-xl bg-black/40 shadow-inner">
                            <div className="max-h-[350px] overflow-y-auto p-2 custom-scrollbar">
                                <div className="space-y-1">
                                    {productsToRegister.filter((p) => !p.isRegistered).map((product) => {
                                        const status = registerStatus[product.code] || 'pending';
                                        return (
                                            <div 
                                                key={product.code} 
                                                className={`flex items-center justify-between p-3 rounded-lg transition-all ${
                                                    status === 'loading' ? 'bg-[var(--primary)]/5 ring-1 ring-[var(--primary)]/20' : ''
                                                }`}
                                            >
                                                <div className="flex items-center gap-4">
                                                    {/* Dynamic Status Icon */}
                                                    <div className="flex items-center justify-center w-6">
                                                        {status === 'completed' && <span className="material-symbols-outlined text-emerald-400 scale-110"><CiCircleCheck /></span>}
                                                        {status === 'pending' && <span className="w-2 h-2 bg-[var(--text)]/20 rounded-full"></span>}
                                                        {status === 'loading' && <div className="w-4 h-4 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin"></div>}
                                                    </div>
                                                    
                                                    <div className="flex flex-col">
                                                        <span className={`text-sm font-mono font-bold tracking-wider ${
                                                            status === 'completed' ? 'text-emerald-400' : 
                                                            status === 'skipped' ? 'text-rose-400' : 'text-[var(--text)]/40'
                                                        }`}>
                                                            {product.code}
                                                        </span>
                                                        <span className="text-[10px] text-[var(--text-muted)]/60 truncate max-w-[200px]">
                                                            {product.description || "Προϊόν"}
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Badge Status */}
                                                <div className="flex flex-col items-end">
                                                    <span className={`text-[10px] font-black uppercase tracking-tighter px-2 py-1 rounded ${
                                                        status === 'completed' ? 'bg-emerald-500/10 text-emerald-500' : 
                                                        status === 'skipped' ? 'bg-rose-500/10 text-rose-500' : 'text-[var(--text)]/20'
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
                            <div className="flex items-center gap-3 bg-[var(--text)]/5 p-4 rounded-xl">
                                <span className="material-symbols-outlined text-[var(--text-muted)] text-lg">
                                    <IoInformationCircleOutline />
                                </span>
                                <p className="text-[11px] text-[var(--text-muted)] leading-tight flex-1">
                                    Η διαδικασία είναι αυτοματοποιημένη. Παρακαλώ μην ανανεώσετε τη σελίδα μέχρι να ολοκληρωθεί η καταχώρηση των ειδών.
                                </p>
                                
                                {/* The Close Button */}
                                { registeringFinished && <button 
                                    onClick={() => onCloseRegisteringWindow()}
                                    className="px-4 py-2 border border-[var(--danger)] text-xs font-bold uppercase tracking-wider text-[var(--text)] cursor-pointer hover:bg-[var(--primary)]/10 rounded-lg transition-colors"
                                >
                                    κλεισιμο
                                </button>}
                            </div>
                        </div>
                    </div>
                </div>
            )}

        {isExtracting && (
                <div className="overscroll-none fixed inset-0 z-[60] flex items-center justify-center bg-black/70 backdrop-blur-md p-4">
                    <div className="relative bg-[var(--bg)] border border-[var(--border-muted)] p-8 rounded-2xl max-w-lg w-full shadow-2xl animate-in fade-in zoom-in duration-300">
                        
                        {/* Header with Global Spinner */}
                        <div className="flex items-center gap-5 mb-8">
                                {
                                    !extractionFinished ? (
                                        <div className="w-12 h-12 border-4 border-[var(--border-muted)] border-t-[var(--primary)] rounded-full animate-spin"></div> 
                                    ) : (
                                        <div className="w-12 h-12 bg-emerald-500 rounded-full flex items-center justify-center animate-in zoom-in duration-300">
                                            <span className="material-symbols-outlined text-white text-3xl"><IoCheckmark /></span>
                                        </div>
                                        )
                                }
                            <div>
                                <h3 className="text-2xl font-black text-[var(--text)] tracking-tight">Εξαγωγή Τιμολογίου</h3>
                                {
                                    !extractionFinished &&
                                    <p className="text-sm text-[var(--text-muted)] flex items-center gap-2">
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--primary)] opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--primary)]"></span>
                                    </span>
                                    Παρακαλώ περιμένετε...
                                    </p>
                                }
                            </div>
                        </div>

                        {/* Live Progress List */}
                        <div className="mb-8 border border-[var(--border-muted)] rounded-xl bg-black/40 shadow-inner">
                            <div className="max-h-[350px] overflow-y-auto p-2 custom-scrollbar">
                                <div className="space-y-1">
                                    {productsToUse.map((product) => {
                                        const status = extractionStatus[product.code] || 'pending';
                                        return (
                                            <div 
                                                key={product.code} 
                                                className={`flex items-center justify-between p-3 rounded-lg transition-all ${
                                                    status === 'loading' ? 'bg-[var(--primary)]/5 ring-1 ring-[var(--primary)]/20' : ''
                                                }`}
                                            >
                                                <div className="flex items-center gap-4">
                                                    {/* Dynamic Status Icon */}
                                                    <div className="flex items-center justify-center w-6">
                                                        {status === 'completed' && <span className="material-symbols-outlined text-emerald-400 scale-110"><FaCheckCircle /></span>}
                                                        {status === 'skipped' && <span className="material-symbols-outlined text-rose-400 animate-pulse"><MdError /></span>}
                                                        {status === 'pending' && <span className="w-2 h-2 bg-[var(--text)]/20 rounded-full"></span>}
                                                        {status === 'loading' && <div className="w-4 h-4 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin"></div>}
                                                    </div>
                                                    
                                                    <div className="flex flex-col">
                                                        <span className={`text-sm font-mono font-bold tracking-wider ${
                                                            status === 'completed' ? 'text-emerald-400' : 
                                                            status === 'skipped' ? 'text-rose-400' : 'text-[var(--text)]/40'
                                                        }`}>
                                                            {product.code}
                                                        </span>
                                                        <span className="text-[10px] text-[var(--text-muted)]/60 truncate max-w-[200px]">
                                                            {product.description || "Προϊόν"}
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Badge Status */}
                                                <div className="flex flex-col items-end">
                                                    <span className={`text-[10px] font-black uppercase tracking-tighter px-2 py-1 rounded ${
                                                        status === 'completed' ? 'bg-emerald-500/10 text-emerald-500' : 
                                                        status === 'skipped' ? 'bg-rose-500/10 text-rose-500' : 'text-[var(--text)]/20'
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
                            <div className="flex items-center gap-3 bg-[var(--text)]/5 p-4 rounded-xl">
                                <span className="material-symbols-outlined text-[var(--text-muted)] text-lg">
                                    <IoInformationCircleOutline />
                                </span>
                                    <p className="text-[11px] text-[var(--text-muted)] leading-tight flex-1">
                                    {extractionFinished ? (
                                        <>
                                        Η Εξαγωγή Τιμολογίου Ολοκληρώθηκε. Πατήστε{' '}
                                        <button 
                                            onClick={onVisitLiveCis}
                                            className="text-[var(--primary)] font-bold hover:underline cursor-pointer transition-colors"
                                        >
                                            εδώ
                                        </button>{' '}
                                        για να προχωρήσετε σε καταχώρηση.
                                        </>
                                    ) : (
                                        `Η διαδικασία είναι αυτοματοποιημένη. Παρακαλώ μην ανανεώσετε τη σελίδα μέχρι να ολοκληρωθεί η εξαγωγή του τιμολογίου.`
                                    )}
                                    </p>
                                
                                {/* The Close Button */}
                                { extractionFinished && <button 
                                    onClick={() => onCloseExtractingWindow()}
                                    className="px-4 py-2 border border-[var(--danger)] text-xs font-bold uppercase tracking-wider text-[var(--text)] cursor-pointer hover:bg-[var(--text)]/10 rounded-lg transition-colors"
                                >
                                    κλεισιμο
                                </button>}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="mx-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Column: Stats Cards */}
                <aside className="lg:col-span-3 space-y-6">
                    {/* Statistics Card */}
                    <div className="bg-[var(--bg)] p-6 rounded-xl border border-[var(--border-muted)]">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold mb-1">ειδη</p>
                                <p className="text-2xl font-black text-[var(--text)]">
                                    {Object.values(groupedData).flat().length.toLocaleString()}
                                </p>
                            </div>
                            <div>
                                <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold mb-1">λειπουν</p>
                                <p className={`text-2xl font-black ${
                                    productsData.filter(p => !p.isRegistered).length > 0 
                                    ? 'text-[var(--danger)]' 
                                    : 'text-[var(--success)]'
                                }`}>
                                    {productsData.filter(p => !p.isRegistered).length}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Order & Client Details Card */}
                    <div className="bg-[var(--bg)] p-6 rounded-xl border border-[var(--border-muted)] space-y-4">
                        <div>
                            <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold mb-1">πελατης</p>
                            <p className="text-base font-bold text-[var(--text)]">{orderData.clientName}</p>
                        </div>

                        <div>
                            <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold mb-1">ΑΦΜ</p>
                            <p className="text-sm font-medium text-[var(--text)]">{orderData.clientVAT}</p>
                        </div>

                        <div>
                            <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-bold mb-1">
                                εξοδα αποστολης
                            </p>
                            <div className="flex items-center gap-1 text-sm font-medium text-[var(--text)]">
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
                                className="inline-block min-w-[4rem] text-center text-sm font-mono font-bold p-1 text-[var(--text)] rounded-md transition-all cursor-text outline-none hover:bg-[var(--primary)]/10 focus:bg-[var(--primary)]/10 focus:ring-1 focus:ring-[var(--primary)]/30 border border-[var(--primary)]"
                                >
                                {orderData.shippingTax}
                                </div>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Products */}
                <div className="lg:col-span-9 space-y-12">
                    {Object.entries(groupedData).map(([brandName, products]) => (
                        <section key={brandName} className="bg-[var(--bg)] rounded-xl overflow-hidden border border-[var(--border-muted)]">
                            {/* Brand Sub-header */}
                            <div className="bg-[var(--bg-light)] px-8 py-4 border-b border-[var(--border-muted)] flex justify-between items-center">
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
                                        text-sm font-bold p-1 uppercase tracking-widest text-[var(--text)] 
                                        flex items-center rounded-md transition-all 
                                        cursor-text outline-none
                                        hover:bg-[var(--text)]/10 
                                        focus:bg-[var(--text)]/10 focus:ring-1 focus:ring-[var(--text)]/30
                                        border border-[var(--text)]/30
                                    "
                                >
                                    <span className="outline-none">{brandName}</span>
                                </h2>
                                <span className="text-[10px] font-bold uppercase text-[var(--text-muted)] opacity-50">
                                    {products.length} {products.length === 1 ? 'ειδος' : 'ειδη'}
                                </span>
                            </div>

                            {/* Scrollable Table Container */}
                        <div className="overflow-y-auto max-h-[500px] relative rounded-b-xl">
                            <table className="w-full text-left border-separate border-spacing-0">
                                <thead className="sticky top-0 z-20">
                                    <tr>
                                        <th className="sticky top-0 bg-[var(--highlight)] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-[var(--text)] border-b border-[var(--border-muted)]">ποσοτητα</th>                                
                                        <th className="sticky top-0 bg-[var(--highlight)] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-[var(--text)] border-b border-[var(--border-muted)]">κωδικος</th>
                                        <th className="sticky top-0 bg-[var(--highlight)] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-[var(--text)] border-b border-[var(--border-muted)]">περιγραφη</th>
                                        <th className="sticky top-0 bg-[var(--highlight)] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-[var(--text)] border-b border-[var(--border-muted)]">τιμη</th>
                                        <th className="sticky top-0 bg-[var(--highlight)] px-8 h-14 vertical-align-middle text-xs font-label uppercase tracking-widest text-[var(--text)] text-center border-b border-[var(--border-muted)]">καταχωρημενο</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[var(--border-muted)]/30">
                                    {products.map((product, pIdx) => (
                                        <tr key={pIdx} className="hover:bg-[var(--text)]/[0.05] transition-colors group">
                                    {/* Quantity */}
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-1 group/stepper">
                                            {/* Decrease Button */}
                                            <button
                                                title="decrease-button"
                                                onClick={() => updateQuantity(product.code, -1)}
                                                className="w-8 h-8 flex items-center justify-center rounded-md border border-[var(--primary)]/20 text-[var(--primary)] hover:bg-[var(--primary)]/10 transition-all active:scale-90"
                                            >
                                                <span className="material-symbols-outlined text-sm"><MdOutlineRemove /></span>
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
                                                className="w-16 text-center text-sm font-mono font-bold p-1 text-[var(--text)]/70 rounded-md transition-all cursor-text outline-none hover:bg-[var(--primary)]/10 focus:bg-[var(--primary)]/10 focus:ring-1 focus:ring-[var(--primary)]/30 border border-[var(--primary)]"
                                            >
                                                {product.quantity}
                                            </div>

                                            {/* Increase Button */}
                                            <button
                                                title="increase-button"
                                                onClick={() => updateQuantity(product.code, 1)}
                                                className="w-8 h-8 flex items-center justify-center rounded-md border border-[var(--primary)]/20 text-[var(--primary)] hover:bg-[var(--primary)]/10 transition-all active:scale-90"
                                            >
                                                <span className="material-symbols-outlined text-sm"><MdAdd /></span>
                                            </button>
                                        </div>
                                    </td>

                                            {/* Code */}
                                            <td className="px-4 py-3">
                                                <div 
                                                    contentEditable 
                                                    suppressContentEditableWarning
                                                    className="text-sm font-semibold p-1 text-[var(--text)] rounded-md transition-all cursor-text outline-none 
                                                    hover:bg-[var(--primary)]/10 focus:bg-[var(--primary)]/10 focus:ring-1 focus:ring-[var(--primary)]/30 border border-transparent hover:border-[var(--primary)]/30 
                                                    focus:border-[var(--primary)] max-w-[175px] whitespace-normal break-words block
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
                                                    className="text-sm font-semibold p-1 text-[var(--text)] rounded-md transition-all cursor-text outline-none 
                                                            hover:bg-[var(--primary)]/10 focus:bg-[var(--primary)]/10 focus:ring-1 focus:ring-[var(--primary)]/30 
                                                            border border-transparent hover:border-[var(--primary)]/30 focus:border-[var(--primary)] 
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
                                                <div className="flex items-center gap-1">
                                                    <span className="text-sm font-semibold text-[var(--text-muted)]">€</span>
                                                    <div
                                                    contentEditable
                                                    suppressContentEditableWarning
                                                    className="text-sm font-semibold p-1 text-[var(--text)] rounded-md transition-all cursor-text outline-none 
                                                                hover:bg-[var(--primary)]/10 focus:bg-[var(--primary)]/10 
                                                                border border-transparent hover:border-[var(--primary)]/30 
                                                                focus:border-[var(--primary)] min-w-[60px] inline-block"
                                                    onBlur={(e) => {
                                                        const newText = e.currentTarget.textContent || "";
                                                        const formattedPrice = newText.replace(',', '.').trim();
                                                        updateProduct(product.code, 'price', formattedPrice);
                                                    }}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter') {
                                                        e.preventDefault();
                                                        e.currentTarget.blur();
                                                        }
                                                    }}
                                                    >
                                                    {product.price}
                                                    </div>
                                                </div>
                                                </td>

                                            <td className="px-4 py-3 text-center">
                                                <div 
                                                    className={`inline-block text-xs font-bold p-2 uppercase rounded-md transition-all 
                                                    ${product.isRegistered 
                                                        ? "text-emerald-300 bg-emerald-500/20"
                                                        : "text-red-300 bg-red-500/20"
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