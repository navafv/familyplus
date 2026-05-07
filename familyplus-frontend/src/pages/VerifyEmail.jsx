import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';

const VerifyEmail = () => {
    const { uid, token } = useParams();
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('');

    useEffect(() => {
        const verify = async () => {
            try {
                const response = await api.post('accounts/verify-email/', {
                    uidb64: uid,
                    token: token
                });
                setStatus('success');
                setMessage(response.data.message || "Email verified successfully!");
            } catch (err) {
                console.error("Verification Error:", err);
                setStatus('error');
                setMessage(err.response?.data?.error || "Invalid or expired verification link.");
            }
        };

        if (uid && token) {
            verify();
        }
    }, [uid, token]);

    return (
        <div className="min-h-[80vh] flex items-center justify-center px-4 bg-gray-50">
            <div className="max-w-md w-full bg-white p-10 rounded-xl shadow-lg text-center border border-gray-100">
                {status === 'verifying' && (
                    <div className="py-8">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-6"></div>
                        <h2 className="text-2xl font-bold text-gray-900">Verifying Your Email...</h2>
                        <p className="text-gray-600 mt-2">Please wait a moment.</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className="py-8">
                        <div className="mb-6 text-green-500">
                            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Success!</h2>
                        <p className="text-gray-600 mb-8">{message}</p>
                        <Link to="/login" className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700 transition-all shadow-md">
                            Proceed to Login
                        </Link>
                    </div>
                )}

                {status === 'error' && (
                    <div className="py-8">
                        <div className="mb-6 text-red-500">
                            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h2>
                        <p className="text-gray-600 mb-8">{message}</p>
                        <Link to="/login" className="text-blue-600 font-bold hover:underline">
                            Return to Login
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};

export default VerifyEmail;
