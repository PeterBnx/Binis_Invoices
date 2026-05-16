import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Orders from './pages/Orders';
import ProductsOfOrder from './pages/ProductsOfOrder';
import Login from './pages/Login';

function App() {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/ordersPage" element={<Orders />} />
          <Route path="/productsOfOrderPage/:id" element={<ProductsOfOrder />} />
        </Routes>
    </Router>
  );
}

export default App;