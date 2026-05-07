import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Store from './pages/Store';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Login from './pages/Login';
import Register from './pages/Register';
import VerifyEmail from './pages/VerifyEmail';
import Checkout from './pages/Checkout';
import OrderComplete from './pages/OrderComplete';

// Placeholder Pages
const Home = () => (
  <div className="p-8 text-center">
    <h1 className="text-4xl font-bold mb-4">Welcome to Family Plus</h1>
    <p className="text-gray-600">The React migration has officially started!</p>
  </div>
);

// Basic Layout Component
const Layout = ({ children }) => {
  const { user, logout } = React.useContext(AuthContext);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white shadow-sm py-4 px-8 flex justify-between items-center">
        <div className="font-bold text-xl text-blue-600">Family Plus</div>
        <nav className="flex gap-6 items-center">
          <Link to="/" className="text-gray-600 hover:text-blue-600">Home</Link>
          <Link to="/store" className="text-gray-600 hover:text-blue-600">Store</Link>
          <Link to="/cart" className="text-gray-600 hover:text-blue-600">Cart</Link>
          
          {user ? (
            <div className="flex gap-4 items-center">
              <span className="text-sm font-medium">Hi, {user.first_name}</span>
              <button 
                onClick={logout}
                className="text-red-500 text-sm hover:underline"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link to="/login" className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm">
              Login
            </Link>
          )}
        </nav>
      </header>
      
      <main className="flex-1">
        {children}
      </main>
      
      <footer className="bg-gray-800 text-white py-6 text-center text-sm">
        &copy; 2026 Family Plus Headless React Application
      </footer>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/store" element={<Store />} />
            <Route path="/store/:slug" element={<ProductDetail />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/order-complete/:orderNumber" element={<OrderComplete />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify/:uid/:token" element={<VerifyEmail />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
