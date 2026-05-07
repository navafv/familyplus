import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/axios';

const Register = () => {
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        password: '',
        confirm_password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        // Validation
        if (formData.password !== formData.confirm_password) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('accounts/register/', formData);
            setSuccessMessage("Account created! Please check your email to verify your account.");
        } catch (err) {
            console.error("Registration Error:", err);
            const msg = err.response?.data ? JSON.stringify(err.response.data) : "Registration failed.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    if (successMessage) {
        return (
            <div className="min-h-[80vh] flex items-center justify-center px-4 bg-gray-50">
                <div className="max-w-md w-full bg-white p-10 rounded-xl shadow-lg text-center border border-green-100">
                    <div className="mb-4 text-green-500">
                        <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email</h2>
                    <p className="text-gray-600 mb-8">{successMessage}</p>
                    <Link to="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 transition-colors">
                        Proceed to Login
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[90vh] flex items-center justify-center px-4 py-12 bg-gray-50">
            <div className="max-w-2xl w-full space-y-8 bg-white p-10 rounded-xl shadow-lg border border-gray-100">
                <div className="text-center">
                    <h2 className="text-3xl font-extrabold text-gray-900">Create Account</h2>
                    <p className="mt-2 text-sm text-gray-600">Join the Family Plus community</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-md text-sm font-medium border border-red-100">
                        {error}
                    </div>
                )}

                <form className="mt-8 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4" onSubmit={handleSubmit}>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                        <input name="first_name" type="text" required onChange={handleChange} className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="John" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                        <input name="last_name" type="text" required onChange={handleChange} className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="Doe" />
                    </div>
                    <div className="sm:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                        <input name="email" type="email" required onChange={handleChange} className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="john.doe@example.com" />
                    </div>
                    <div className="sm:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                        <input name="phone_number" type="text" required onChange={handleChange} className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="+1 234 567 890" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                        <input name="password" type="password" required onChange={handleChange} className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="••••••••" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                        <input name="confirm_password" type="password" required onChange={handleChange} className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="••••••••" />
                    </div>

                    <div className="sm:col-span-2 pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-lg text-white transition-all ${
                                loading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
                            }`}
                        >
                            {loading ? 'Creating Account...' : 'Register'}
                        </button>
                    </div>
                </form>

                <div className="text-center mt-4">
                    <p className="text-sm text-gray-600">
                        Already have an account?{' '}
                        <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500 underline">
                            Log in here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register;
