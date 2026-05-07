import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';

const Cart = () => {
    const [cartData, setCartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCart = useCallback(async () => {
        try {
            const response = await api.get('cart/');
            setCartData(response.data);
            setError(null);
        } catch (err) {
            console.error("Error fetching cart:", err);
            setError("Failed to load cart.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCart();
    }, [fetchCart]);

    const mapVariations = (variations) => {
        const mapped = {};
        variations.forEach(v => {
            mapped[v.variation_category.toLowerCase()] = v.variation_value;
        });
        return mapped;
    };

    const increaseQuantity = async (item) => {
        try {
            const variations = mapVariations(item.variations);
            await api.post(`cart/add/${item.product.id}/`, { variations });
            fetchCart();
        } catch (err) {
            console.error("Error increasing quantity:", err);
        }
    };

    const decreaseQuantity = async (item) => {
        try {
            await api.post(`cart/decrease/${item.product.id}/${item.id}/`);
            fetchCart();
        } catch (err) {
            console.error("Error decreasing quantity:", err);
        }
    };

    const removeItem = async (item) => {
        try {
            await api.delete(`cart/remove/${item.product.id}/${item.id}/`);
            fetchCart();
        } catch (err) {
            console.error("Error removing item:", err);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!cartData || !cartData.cart_items || cartData.cart_items.length === 0) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-20 text-center">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Your Cart is Empty</h2>
                <p className="text-gray-600 mb-8">Looks like you haven't added anything to your cart yet.</p>
                <Link 
                    to="/store" 
                    className="bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700 transition-colors"
                >
                    Continue Shopping
                </Link>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-3xl font-extrabold text-gray-900 mb-8">Shopping Cart</h1>
            
            <div className="flex flex-col lg:flex-row gap-12">
                {/* Left Column: Cart Items */}
                <div className="lg:w-2/3">
                    <div className="space-y-6">
                        {cartData.cart_items.map((item) => (
                            <div key={item.id} className="flex flex-col sm:flex-row items-center gap-6 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <img 
                                    src={item.product.images} 
                                    alt={item.product.product_name} 
                                    className="w-24 h-24 object-cover rounded-lg"
                                />
                                <div className="flex-1 text-center sm:text-left">
                                    <Link to={`/store/${item.product.slug}`} className="text-lg font-bold text-gray-900 hover:text-blue-600">
                                        {item.product.product_name}
                                    </Link>
                                    <div className="mt-1 flex flex-wrap justify-center sm:justify-start gap-2">
                                        {item.variations.map((v, idx) => (
                                            <span key={idx} className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                                {v.variation_category}: {v.variation_value}
                                            </span>
                                        ))}
                                    </div>
                                    <div className="mt-2 text-gray-500 font-medium">
                                        ${item.product.price}
                                    </div>
                                </div>
                                
                                <div className="flex items-center gap-4">
                                    <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                                        <button 
                                            onClick={() => decreaseQuantity(item)}
                                            className="px-3 py-1 bg-gray-50 hover:bg-gray-100 text-gray-600 transition-colors"
                                        >
                                            -
                                        </button>
                                        <span className="px-4 py-1 font-semibold text-gray-900">{item.quantity}</span>
                                        <button 
                                            onClick={() => increaseQuantity(item)}
                                            className="px-3 py-1 bg-gray-50 hover:bg-gray-100 text-gray-600 transition-colors"
                                        >
                                            +
                                        </button>
                                    </div>
                                    <button 
                                        onClick={() => removeItem(item)}
                                        className="text-red-500 hover:text-red-700 text-sm font-medium"
                                    >
                                        Remove
                                    </button>
                                </div>
                                
                                <div className="text-right min-w-[100px]">
                                    <div className="text-lg font-bold text-gray-900">${item.sub_total}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Column: Order Summary */}
                <div className="lg:w-1/3">
                    <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 sticky top-8">
                        <h2 className="text-xl font-bold text-gray-900 mb-6">Order Summary</h2>
                        <div className="space-y-4 mb-6">
                            <div className="flex justify-between text-gray-600">
                                <span>Total Price:</span>
                                <span>${cartData.total}</span>
                            </div>
                            <div className="flex justify-between text-gray-600">
                                <span>Tax/Shipping:</span>
                                <span>${cartData.shipping}</span>
                            </div>
                            <div className="border-t border-gray-100 pt-4 flex justify-between text-xl font-bold text-gray-900">
                                <span>Grand Total:</span>
                                <span>${cartData.grand_total}</span>
                            </div>
                        </div>
                        <Link 
                            to="/login"
                            className="block w-full bg-blue-600 text-white text-center py-4 rounded-lg font-bold text-lg hover:bg-blue-700 shadow-md hover:shadow-lg transition-all"
                        >
                            Proceed to Checkout
                        </Link>
                        <div className="mt-6 flex justify-center gap-4">
                            <img src="https://img.icons8.com/color/48/000000/visa.png" alt="visa" className="h-8"/>
                            <img src="https://img.icons8.com/color/48/000000/mastercard.png" alt="mastercard" className="h-8"/>
                            <img src="https://img.icons8.com/color/48/000000/paypal.png" alt="paypal" className="h-8"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Cart;
