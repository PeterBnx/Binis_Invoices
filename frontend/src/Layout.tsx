import { Outlet, useNavigate } from "react-router-dom"; // Added useNavigate

function Layout() {
  const navigate = useNavigate(); // Initialize the navigate hook

  const handleLogout = () => {
    localStorage.removeItem("token"); // Remove the security token
    navigate("/login"); // Redirect back to the login screen
  };

  return (
    <>
      {/* --- STATIC NAVBAR --- */}
      <nav className="fixed top-0 w-full z-50 bg-[#131313]/90 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
        <div className="flex justify-between items-center w-full px-8 h-16">
          <div className="flex items-center gap-12">
            <span className="text-xl font-bold tracking-tighter text-[#B32C3A] font-['Manrope']">
              Binis Invoices
            </span>
          </div>
          
          {/* --- ADDED LOGOUT BUTTON --- */}
          <button 
            onClick={handleLogout}
            className="text-gray-400 hover:text-[#B32C3A] font-['Inter'] text-xs uppercase tracking-widest transition-colors cursor-pointer"
          >
            Αποσύνδεση
          </button>
        </div>
        <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-[#B32C3A]/20 to-transparent" />
      </nav>

      {/* --- DYNAMIC CONTENT --- */}
      <main className="pt-12 px-8 max-w-[1600px] mx-auto mb-8 mt-4">
        <Outlet />
      </main>

      {/* --- STATIC FOOTER --- */}
      {/* Keep your footer as is... */}
    </>
  );
}

export default Layout;