import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';

const Checkout = () => {
    const { user, loading: authLoading } = useContext(AuthContext);
    const navigate = useNavigate();
    
    const [cartData, setCartData] = useState(null);
    const [cartLoading, setCartLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);

    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        address_line_1: '',
        address_line_2: '',
        city: '',
        state: '',
        country: '',
        order_note: ''
    });

    // 1. Protect Route & Pre-fill form
    useEffect(() => {
        if (!authLoading) {
            if (!user) {
                navigate('/login');
            } else {
                // Pre-fill form data from user profile
                setFormData({
                    first_name: user.first_name || '',
                    last_name: user.last_name || '',
                    email: user.email || '',
                    phone: user.phone_number || '',
                    address_line_1: user.user_profile?.address_line_1 || '',
                    address_line_2: user.user_profile?.address_line_2 || '',
                    city: user.user_profile?.city || '',
                    state: user.user_profile?.state || '',
                    country: user.user_profile?.country || '',
                    order_note: ''
                });
            }
        }
    }, [user, authLoading, navigate]);

    // 2. Fetch Cart Data
    useEffect(() => {
        const fetchCart = async () => {
            try {
                const response = await api.get('cart/');
                if (response.data.cart_items.length === 0) {
                    navigate('/store');
                } else {
                    setCartData(response.data);
                }
            } catch (err) {
                console.error("Cart fetch error:", err);
            } finally {
                setCartLoading(false);
            }
        };
        if (user) fetchCart();
    }, [user, navigate]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleCheckout = async (e) => {
        e.preventDefault();
        setError(null);
        setIsProcessing(true);

        try {
            // Step 1: Create Order
            const orderResponse = await api.post('orders/checkout/', formData);
            const { order_number } = orderResponse.data;

            // Step 2: Process Payment (Simulated COD for now)
            await api.post('orders/process-payment/', { order_number });

            // Step 3: Success!
            navigate(`/order-complete/${order_number}`);
        } catch (err) {
            console.error("Checkout Error:", err);
            const msg = err.response?.data ? JSON.stringify(err.response.data) : "An error occurred during checkout.";
            setError(msg);
            setIsProcessing(false);
        }
    };

    if (authLoading || cartLoading) {
        return (
            <div className="flex justify-center items-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-3xl font-extrabold text-gray-900 mb-8">Checkout</h1>
            
            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-8 border border-red-100 text-sm">
                    {error}
                </div>
            )}

            <form onSubmit={handleCheckout} className="flex flex-col lg:flex-row gap-12">
                {/* Left: Shipping Form */}
                <div className="lg:w-2/3 bg-white p-8 rounded-xl shadow-sm border border-gray-100">
                    <h2 className="text-xl font-bold text-gray-900 mb-6 pb-2 border-b">Shipping Information</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                            <input name="first_name" value={formData.first_name} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input name="last_name" value={formData.last_name} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                            <input name="email" type="email" value={formData.email} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                            <input name="phone" value={formData.phone} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 1</label>
                            <input name="address_line_1" value={formData.address_line_1} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Address Line 2 (Optional)</label>
                            <input name="address_line_2" value={formData.address_line_2} onChange={handleChange} className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                            <input name="city" value={formData.city} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">State/Province</label>
                            <input name="state" value={formData.state} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                            <input name="country" value={formData.country} onChange={handleChange} required className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Order Note (Optional)</label>
                            <textarea name="order_note" rows="3" value={formData.order_note} onChange={handleChange} className="w-full px-4 py-2.5 border rounded-lg focus:ring-blue-500" placeholder="Special instructions for delivery..."></textarea>
                        </div>
                    </div>
                </div>

                {/* Right: Order Summary */}
                <div className="lg:w-1/3">
                    <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 sticky top-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-6 pb-2 border-b">In Your Cart</h2>
                        <div className="max-h-[300px] overflow-y-auto space-y-4 mb-6 pr-2">
                            {cartData?.cart_items.map(item => (
                                <div key={item.id} className="flex gap-4">
                                    <img src={item.product.images} alt="" className="w-16 h-16 object-cover rounded shadow-sm" />
                                    <div className="flex-1">
                                        <h4 className="text-sm font-bold text-gray-900 leading-tight">{item.product.product_name}</h4>
                                        <p className="text-xs text-gray-500 mt-1">Qty: {item.quantity}</p>
                                        <p className="text-sm font-bold text-gray-700 mt-1">${item.sub_total}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="space-y-3 mb-8 pt-4 border-t border-gray-100">
                            <div className="flex justify-between text-gray-600 text-sm">
                                <span>Subtotal:</span>
                                <span>${cartData?.total}</span>
                            </div>
                            <div className="flex justify-between text-gray-600 text-sm">
                                <span>Shipping:</span>
                                <span>${cartData?.shipping}</span>
                            </div>
                            <div className="flex justify-between text-lg font-bold text-gray-900 pt-2 border-t">
                                <span>Total:</span>
                                <span>${cartData?.grand_total}</span>
                            </div>
                        </div>
                        <button
                            type="submit"
                            disabled={isProcessing}
                            className={`w-full py-4 px-6 rounded-lg font-bold text-white text-lg transition-all ${
                                isProcessing ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
                            }`}
                        >
                            {isProcessing ? 'Processing Order...' : 'Place Order'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default Checkout;
