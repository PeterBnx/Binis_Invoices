import Layout from './Layout';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Orders from './pages/Orders'
import ProductsOfOrder from './pages/ProductsOfOrder';


function App() {
return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          {/* These will render inside the <Outlet /> of Layout */}
          <Route path="orders" element={<Orders />} />
          <Route path="products_of_order" element={<ProductsOfOrder />} />
          <Route index element={<ProductsOfOrder />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;