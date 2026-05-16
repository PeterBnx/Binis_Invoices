import { useState, useEffect } from "react";

export default function Settings({ onClose }: { onClose: () => void }) {
  const [empUser, setEmpUser] = useState("");
  const [empPass, setEmpPass] = useState("");
  const [cisUser, setCisUser] = useState("");
  const [cisPass, setCisPass] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("");
  
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  const handleSave = async () => {
    setIsSaving(true);
    const success = await window.api.invoke('save_credentials', {
      empUser, empPass, cisUser, cisPass
    });
    
    if (success) {
      setMessage("Οι αλλαγές αποθηκεύτηκαν επιτυχώς");
      setTimeout(() => setMessage(""), 3000);
    }
    setIsSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-8">
      <div className="max-w-4xl w-full flex flex-col h-[85vh] relative rounded-lg shadow-2xl bg-[var(--bg)] border border-[var(--border-muted)] overflow-hidden">
        
        <button
          title="close"
          onClick={onClose}
          className="absolute top-6 right-6 p-2 rounded-full hover:bg-[var(--bg-dark)] text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer z-10"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="p-10 flex flex-col h-full">
          <header className="mb-8 flex-shrink-0">
            <h1 className="text-5xl font-bold mb-2 text-[var(--text)] tracking-tight">Ρυθμίσεις</h1>
          </header>

          <section className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              <div className="space-y-6">
                <header className="border-b border-[var(--border-muted)] pb-4">
                  <h2 className="text-2xl font-bold text-[var(--primary)]">Emporiorologion</h2>
                  <p className="text-sm text-[var(--text-muted)]">Στοιχεία σύνδεσης για το emporiorologion.gr</p>
                </header>
                
                <div className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Username</label>
                    <input 
                      title="empUser"
                      value={empUser}
                      onChange={(e) => setEmpUser(e.target.value)}
                      className="w-full p-3 rounded-lg bg-[var(--bg-dark)] border border-[var(--border-muted)] focus:border-[var(--primary)] outline-none text-[var(--text)]" 
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Password</label>
                    <input
                      title="empPass"
                      value={empPass}
                      onChange={(e) => setEmpPass(e.target.value)}
                      className="w-full p-3 rounded-lg bg-[var(--bg-dark)] border border-[var(--border-muted)] focus:border-[var(--primary)] outline-none text-[var(--text)]" 
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <header className="border-b border-[var(--border-muted)] pb-4">
                  <h2 className="text-2xl font-bold text-[var(--primary)]">LiveCIS</h2>
                  <p className="text-sm text-[var(--text-muted)]">Στοιχεία σύνδεσης για την πλατφόρμα CIS</p>
                </header>
                
                <div className="space-y-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Username</label>
                    <input
                      title="cisUser"
                      value={cisUser}
                      onChange={(e) => setCisUser(e.target.value)}
                      className="w-full p-3 rounded-lg bg-[var(--bg-dark)] border border-[var(--border-muted)] focus:border-[var(--primary)] outline-none text-[var(--text)]" 
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Password</label>
                    <input
                      title="cisPass"
                      value={cisPass}
                      onChange={(e) => setCisPass(e.target.value)}
                      className="w-full p-3 rounded-lg bg-[var(--bg-dark)] border border-[var(--border-muted)] focus:border-[var(--primary)] outline-none text-[var(--text)]" 
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>

          <div className="mt-8 pt-8 border-t border-[var(--border-muted)] flex items-center justify-between flex-shrink-0">
            <p className="text-[var(--primary)] font-medium">{message}</p>
            <div className="flex gap-4">
              <button 
                onClick={onClose}
                className="px-6 py-3 font-semibold rounded-lg border border-[var(--border-muted)] text-[var(--text)] hover:bg-[var(--bg-dark)] transition-all"
              >
                Κλείσιμο
              </button>
              <button 
                onClick={handleSave}
                disabled={isSaving}
                className="px-8 py-3 font-bold rounded-lg transition-all shadow-lg bg-[var(--primary)] text-[var(--bg-dark)] hover:opacity-90 active:scale-[0.98] disabled:opacity-50"
              >
                {isSaving ? "Αποθήκευση..." : "Αποθήκευση Αλλαγών"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}