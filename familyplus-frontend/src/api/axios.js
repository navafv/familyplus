import axios from 'axios';

// Utility function to generate a simple UUID for the cart
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to attach tokens and cart IDs
api.interceptors.request.use((config) => {
    // 1. Handle Authentication Token
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    // 2. Handle Anonymous Cart ID
    // We only need the X-Cart-Id if the user is not authenticated
    if (!token) {
        let cartId = localStorage.getItem('cart_id');
        if (!cartId) {
            cartId = generateUUID();
            localStorage.setItem('cart_id', cartId);
        }
        config.headers['X-Cart-Id'] = cartId;
    }

    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;
