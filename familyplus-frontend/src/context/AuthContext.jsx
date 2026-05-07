import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Check if user is already logged in on mount
    useEffect(() => {
        const checkAuthStatus = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    // Fetch the user profile using the token
                    const response = await api.get('accounts/profile/');
                    setUser(response.data);
                } catch (error) {
                    console.error("Authentication failed:", error);
                    // Token might be invalid or expired
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    setUser(null);
                }
            }
            setLoading(false);
        };

        checkAuthStatus();
    }, []);

    const login = async (email, password) => {
        try {
            // 1. Get the tokens
            const tokenResponse = await api.post('token/', { email, password });
            const { access, refresh } = tokenResponse.data;
            
            // 2. Save tokens to localStorage
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            
            // 3. Fetch user profile data
            const profileResponse = await api.get('accounts/profile/');
            setUser(profileResponse.data);

            // 4. (Optional but recommended) Trigger the Cart Merge API
            const cartId = localStorage.getItem('cart_id');
            if (cartId) {
                try {
                    await api.post('cart/merge/', { cart_id: cartId });
                    localStorage.removeItem('cart_id'); // Clean up local cart ID
                } catch (err) {
                    console.error("Cart merge failed:", err);
                }
            }

            return { success: true };
        } catch (error) {
            console.error("Login Error:", error);
            return { 
                success: false, 
                error: error.response?.data?.detail || "Invalid credentials." 
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
