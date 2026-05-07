import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';

const OrderComplete = () => {
    const { orderNumber } = useParams();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                // Fetch the detailed order from the API
                const response = await api.get(`orders/${orderNumber}/`);
                setOrder(response.data);
            } catch (err) {
                console.error("Order fetch error:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchOrder();
    }, [orderNumber]);

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-20 text-center">
                <h2 className="text-3xl font-bold text-gray-900">Order Not Found</h2>
                <Link to="/store" className="text-blue-600 hover:underline mt-4 inline-block">Back to Store</Link>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                {/* Header Section */}
                <div className="bg-blue-600 p-10 text-center text-white">
                    <div className="mb-4 bg-white/20 w-20 h-20 rounded-full flex items-center justify-center mx-auto">
                        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path>
                        </svg>
                    </div>
                    <h1 className="text-3xl font-extrabold mb-2">Thank You For Your Order!</h1>
                    <p className="text-blue-100 opacity-90">A confirmation email has been sent to {order.email}</p>
                </div>

                {/* Top Details */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 p-8 border-b border-gray-100 bg-gray-50/50">
                    <div>
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Order Number</p>
                        <p className="text-sm font-bold text-gray-900">#{order.order_number}</p>
                    </div>
                    <div>
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Date</p>
                        <p className="text-sm font-bold text-gray-900">{new Date(order.created_at).toLocaleDateString()}</p>
                    </div>
                    <div>
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Status</p>
                        <p className="text-sm font-bold text-green-600">{order.status}</p>
                    </div>
                    <div>
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Total Paid</p>
                        <p className="text-sm font-bold text-gray-900">${order.order_total}</p>
                    </div>
                </div>

                {/* Items List */}
                <div className="p-8">
                    <h3 className="text-lg font-bold text-gray-900 mb-6">Purchase Details</h3>
                    <div className="space-y-6">
                        {order.order_products?.map((item) => (
                            <div key={item.id} className="flex items-center gap-6 pb-6 border-b border-gray-100 last:border-0 last:pb-0">
                                <img src={item.product.images} alt="" className="w-20 h-20 object-cover rounded-lg shadow-sm" />
                                <div className="flex-1">
                                    <h4 className="text-lg font-bold text-gray-900">{item.product.product_name}</h4>
                                    <div className="flex flex-wrap gap-2 mt-1">
                                        {item.variation?.map((v, idx) => (
                                            <span key={idx} className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                                {v.variation_category}: {v.variation_value}
                                            </span>
                                        ))}
                                    </div>
                                    <p className="text-sm text-gray-500 mt-1">Quantity: {item.quantity}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-lg font-bold text-gray-900">${item.product_price}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Payment & Shipping Summary */}
                <div className="p-8 bg-gray-50 border-t border-gray-100">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                        <div>
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Shipping Address</h4>
                            <div className="text-sm text-gray-700 leading-relaxed">
                                <p className="font-bold text-gray-900">{order.first_name} {order.last_name}</p>
                                <p>{order.address_line_1}</p>
                                {order.address_line_2 && <p>{order.address_line_2}</p>}
                                <p>{order.city}, {order.state}, {order.country}</p>
                                <p className="mt-2 text-gray-500">{order.phone}</p>
                            </div>
                        </div>
                        <div className="space-y-3">
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Payment Summary</h4>
                            <div className="flex justify-between text-sm text-gray-600">
                                <span>Subtotal:</span>
                                <span>${(parseFloat(order.order_total) - parseFloat(order.shipping)).toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-sm text-gray-600">
                                <span>Shipping:</span>
                                <span>${order.shipping}</span>
                            </div>
                            <div className="flex justify-between text-xl font-extrabold text-gray-900 pt-3 border-t border-gray-200">
                                <span>Total Paid:</span>
                                <span>${order.order_total}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-8 text-center bg-white border-t border-gray-100">
                    <Link to="/store" className="bg-blue-600 text-white px-10 py-3 rounded-lg font-bold hover:bg-blue-700 shadow-md transition-all">
                        Continue Shopping
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default OrderComplete;
