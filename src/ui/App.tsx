import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Orders from './pages/Orders';
import ProductsOfOrder from './pages/ProductsOfOrder';


function App() {
  return (
    <Router>
        <Routes>
          {/* <Route path="/" element={<Login />} /> */}
          <Route path="/" element={<Orders />}/>
          <Route path="/ordersPage" element={<Orders />} />
          <Route path="/productsOfOrderPage" element={<ProductsOfOrder />} />
        </Routes>
    </Router>
  );
}

export default App;
