import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import Layout from './Layout';
import Orders from './pages/Orders';
import ProductsOfOrder from './pages/ProductsOfOrder';
import Login from './pages/Login';

const ProtectedRoute = () => {
  const token = localStorage.getItem("token");
  return token ? <Outlet /> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<Orders />} />
            <Route path="orders" element={<Orders />} />
            <Route path="products_of_order" element={<ProductsOfOrder />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;