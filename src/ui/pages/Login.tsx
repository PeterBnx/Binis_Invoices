import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../../electron/supabaseClient"; 

export default function Login() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const userEmail = import.meta.env.VITE_USER_EMAIL;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    if (userEmail === undefined) {
      alert('Δεν βρέθηκε το email');
      return;
    }
    try {
      const { error: authError } = await supabase.auth.signInWithPassword({
        email: userEmail,
        password: password,
      });

      if (authError) {
        console.error("Supabase Error:", authError.message);
        setError("Πρόβλημα κατά τη σύνδεση: " + authError.message);
        return;
      }
      navigate("/ordersPage");

    } catch (err) {
      setError(`Παρουσιάστηκε σφάλμα κατά τη σύνδεση: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };

return (
  <main className="h-screen flex flex-col p-8 bg-[var(--bg-dark)] text-[var(--text)] overflow-hidden">
    {isLoading && (
      <div className="fixed inset-0 z-50 flex flex-col items-center justify-center backdrop-blur-sm bg-black/60">
        <div className="w-16 h-16 border-4 rounded-full animate-spin mb-4 border-[var(--border-muted)] border-t-[var(--primary)]"></div>
        <p className="font-semibold tracking-wide animate-pulse">
          Σύνδεση στο σύστημα...
        </p>
      </div>
    )}

    <div className="max-w-6xl w-full mx-auto flex flex-col h-full justify-center items-center">
      <header className="mb-12 text-center">
        <h1 className="select-none text-6xl font-bold mb-3 text-[var(--text)] tracking-tight">
          Binis Invoices
        </h1>
        <p className="select-none text-xl text-[var(--text-muted)]">
          Παρακαλώ εισάγετε τον κωδικό σας για να συνδεθείτε
        </p>
      </header>

      <section className="select-none w-full max-w-md p-10 rounded-lg shadow-2xl bg-[var(--bg)] border border-[var(--border-muted)]">
        <form onSubmit={handleLogin} className="flex flex-col gap-6">
          
          {error && (
            <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/50 text-red-500 text-sm font-medium animate-pulse">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">
              κωδικος προσβασης
            </label>
            <input 
              title="password"
              type="password" 
              autoComplete="current-password"
              disabled={isLoading}
              className="w-full p-4 rounded-lg bg-[var(--bg-dark)] text-[var(--text)] border border-[var(--border-muted)] focus:border-[var(--primary)] outline-none transition-all duration-200"
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <button 
            type="submit"
            disabled={isLoading}
            className="mt-4 px-6 py-4 font-bold text-lg rounded-lg transition-all duration-200 shadow-lg bg-[var(--primary)] text-[var(--bg-dark)] hover:opacity-90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Είσοδος
          </button>
        </form>
      </section>

      {/* Footer hint */}
      <footer className="mt-8">
        <p className="text-[var(--text-muted)] text-sm opacity-50 uppercase tracking-[0.2em]">
          Petros Binis &copy;2026
        </p>
      </footer>
    </div>
  </main>
);
}