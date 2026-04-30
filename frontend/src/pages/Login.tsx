import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false); // New loading state
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE_URL}/binis_invoices/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      
      const data = await res.json();
      
      if (res.ok && data.token) {
        localStorage.setItem("token", data.token);
        navigate("/orders");
      } else {
        setError(data.error || "Σφάλμα σύνδεσης");
      }
    } catch (err) {
      setError("Αποτυχία σύνδεσης στον διακομιστή");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-surface-dark px-4">
      <form onSubmit={handleLogin} className="w-full max-w-md p-8 bg-surface-container rounded-2xl shadow-2xl border border-outline-variant/10">
        <h1 className="text-3xl font-extrabold text-on-surface mb-2 tracking-tighter">Binis Invoices</h1>
        <p className="text-on-surface-variant mb-8 font-light">Παρακαλώ συνδεθείτε για να συνεχίσετε.</p>
        
        {error && <div className="mb-4 p-3 bg-error-container text-on-error-container rounded-lg text-sm font-medium animate-pulse">
          {error}
        </div>}
        
        <div className="space-y-4">
          <input 
            type="text" 
            autoComplete="username"
            disabled={isLoading}
            placeholder="Όνομα χρήστη" 
            className="w-full p-4 rounded-xl bg-surface text-on-surface border border-outline focus:border-primary outline-none transition-all disabled:opacity-50"
            onChange={e => setUsername(e.target.value)}
          />
          <input 
            type="password" 
            autoComplete="current-password"
            disabled={isLoading}
            placeholder="Κωδικός" 
            className="w-full p-4 rounded-xl bg-surface text-on-surface border border-outline focus:border-primary outline-none transition-all disabled:opacity-50"
            onChange={e => setPassword(e.target.value)}
          />
          
          <button 
            disabled={isLoading}
            className={`w-full flex items-center justify-center gap-3 py-4 rounded-xl font-bold text-lg transition-all ${
              isLoading 
                ? "bg-gray-600 cursor-not-allowed opacity-70" 
                : "bg-primary text-on-primary hover:brightness-110 active:scale-[0.98] cursor-pointer"
            }`}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Σύνδεση...
              </>
            ) : (
              "Είσοδος"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}