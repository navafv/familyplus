import React from 'react';
import * as Sentry from "@sentry/react";

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI.
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Automatically transmit rendering crashes to the Sentry cloud dashboard
        Sentry.captureException(error, { extra: errorInfo });
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
                    <div className="max-w-md w-full text-center p-8 bg-white rounded-xl shadow-lg border border-red-100">
                        <div className="text-red-500 mb-6">
                            <svg className="w-20 h-20 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                            </svg>
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
                        <p className="text-gray-600 mb-8">
                            We encountered an unexpected error. Please try refreshing the page or returning home.
                        </p>
                        <button
                            onClick={() => window.location.href = '/'}
                            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700 transition-all shadow-md"
                        >
                            Back to Home
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children; 
    }
}

export default ErrorBoundary;
