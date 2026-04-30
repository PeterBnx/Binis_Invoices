import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
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
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-surface-dark px-4">
      <form onSubmit={handleLogin} className="w-full max-w-md p-8 bg-surface-container rounded-2xl shadow-2xl border border-outline-variant/10">
        <h1 className="text-3xl font-extrabold text-on-surface mb-2 tracking-tighter">Binis Invoices</h1>
        <p className="text-on-surface-variant mb-8 font-light">Παρακαλώ συνδεθείτε για να συνεχίσετε.</p>
        
        {error && <div className="mb-4 p-3 bg-error-container text-on-error-container rounded-lg text-sm">{error}</div>}
        
        <div className="space-y-4">
          <input 
            type="text" 
            placeholder="Όνομα χρήστη" 
            className="w-full p-4 rounded-xl bg-surface text-on-surface border border-outline focus:border-primary outline-none transition-all"
            onChange={e => setUsername(e.target.value)}
          />
          <input 
            type="password" 
            placeholder="Κωδικός" 
            className="w-full p-4 rounded-xl bg-surface text-on-surface border border-outline focus:border-primary outline-none transition-all"
            onChange={e => setPassword(e.target.value)}
          />
          <button className="w-full bg-primary text-on-primary py-4 rounded-xl font-bold text-lg hover:brightness-110 active:scale-[0.98] transition-all">
            Είσοδος
          </button>
        </div>
      </form>
    </div>
  );
}