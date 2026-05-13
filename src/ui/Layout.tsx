import { Outlet, useNavigate } from "react-router-dom";

function Layout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
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
      <footer className="z-30 fixed bottom-0 w-full py-12 border-t border-[#B32C3A]/10 bg-[#0E0E0E]">
        <div className="flex flex-col md:flex-row justify-between items-center px-12 max-w-7xl mx-auto gap-4">
          <div className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest">
            © developed by petros binis
          </div>
          <div className="flex items-center gap-8">
            <a
              className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest hover:text-[#B32C3A] transition-colors"
              href="#"
            >
              Privacy
            </a>
            <a
              className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest hover:text-[#B32C3A] transition-colors"
              href="#"
            >
              Terms
            </a>
            <a
              className="text-gray-600 font-['Inter'] text-xs uppercase tracking-widest hover:text-[#B32C3A] transition-colors"
              href="#"
            >
              Support
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}

export default Layout;