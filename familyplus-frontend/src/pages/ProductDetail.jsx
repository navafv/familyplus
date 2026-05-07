import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/axios';

const ProductDetail = () => {
    const { slug } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedVariations, setSelectedVariations] = useState({});
    const [isAddingToCart, setIsAddingToCart] = useState(false);
    const [addMessage, setAddMessage] = useState(null);

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                // Fetch the list of products and find by slug
                // Note: Ideally, a dedicated endpoint like `/store/products/${slug}/` would be better for performance,
                // but based on current DRF setup, we filter the list.
                const response = await api.get('store/products/');
                const products = response.data.results || response.data;
                const foundProduct = products.find(p => p.slug === slug);

                if (foundProduct) {
                    setProduct(foundProduct);
                } else {
                    setError("Product not found.");
                }
            } catch (err) {
                console.error("Error fetching product:", err);
                setError("Failed to load product details.");
            } finally {
                setLoading(false);
            }
        };

        fetchProduct();
    }, [slug]);

    const handleVariationSelect = (category, value) => {
        setSelectedVariations(prev => ({
            ...prev,
            [category]: value
        }));
        // Clear success message when user changes selection
        if (addMessage) setAddMessage(null);
    };

    const handleAddToCart = async () => {
        if (!product) return;

        // Verify required variations
        const requiredColors = product.variations?.colors?.length > 0;
        const requiredSizes = product.variations?.sizes?.length > 0;

        if (requiredColors && !selectedVariations['color']) {
            setError("Please select a color.");
            return;
        }
        if (requiredSizes && !selectedVariations['size']) {
            setError("Please select a size.");
            return;
        }

        setError(null);
        setIsAddingToCart(true);
        setAddMessage(null);

        try {
            await api.post(`cart/add/${product.id}/`, {
                variations: selectedVariations
            });
            setAddMessage("Added to cart successfully!");
        } catch (err) {
            console.error("Error adding to cart:", err);
            setError("Failed to add to cart. Please try again.");
        } finally {
            setIsAddingToCart(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error && !product) {
        return (
            <div className="text-center text-red-600 min-h-[60vh] flex flex-col justify-center">
                <p className="text-xl font-semibold">{error}</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden flex flex-col lg:flex-row">
                
                {/* Left Column - Images */}
                <div className="lg:w-1/2 p-8 bg-gray-50 flex flex-col items-center">
                    <img 
                        src={product.images} 
                        alt={product.product_name} 
                        loading="lazy"
                        className="w-full max-w-md h-auto object-cover rounded-lg shadow-sm"
                    />
                    
                    {product.gallery && product.gallery.length > 0 && (
                        <div className="flex gap-4 mt-6 overflow-x-auto pb-2">
                            {product.gallery.map(img => (
                                <img 
                                    key={img.id}
                                    src={img.image}
                                    alt={`${product.product_name} thumbnail`}
                                    loading="lazy"
                                    className="w-20 h-20 object-cover rounded border border-gray-200 cursor-pointer hover:border-blue-500 transition-colors"
                                />
                            ))}
                        </div>
                    )}
                </div>

                {/* Right Column - Details & Actions */}
                <div className="lg:w-1/2 p-8 flex flex-col justify-center">
                    <div className="mb-2">
                        <span className="text-sm font-semibold text-blue-600 uppercase tracking-wider">
                            {product.category?.category_name}
                        </span>
                    </div>
                    
                    <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-4">
                        {product.product_name}
                    </h1>
                    
                    <div className="text-3xl font-bold text-gray-900 mb-6">
                        ${product.price}
                    </div>

                    <p className="text-gray-600 text-base mb-8 leading-relaxed">
                        {product.description}
                    </p>

                    {/* Variations Selection */}
                    <div className="mb-8 space-y-6">
                        {/* Colors */}
                        {product.variations?.colors?.length > 0 && (
                            <div>
                                <h3 className="text-sm font-medium text-gray-900 mb-3">Color</h3>
                                <div className="flex flex-wrap gap-3">
                                    {product.variations.colors.map(color => (
                                        <button
                                            key={color.id}
                                            onClick={() => handleVariationSelect('color', color.variation_value)}
                                            className={`px-4 py-2 border rounded-md text-sm font-medium transition-all ${
                                                selectedVariations['color'] === color.variation_value
                                                    ? 'border-blue-600 bg-blue-50 text-blue-700 ring-1 ring-blue-600'
                                                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                                            }`}
                                        >
                                            {color.variation_value}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Sizes */}
                        {product.variations?.sizes?.length > 0 && (
                            <div>
                                <h3 className="text-sm font-medium text-gray-900 mb-3">Size</h3>
                                <div className="flex flex-wrap gap-3">
                                    {product.variations.sizes.map(size => (
                                        <button
                                            key={size.id}
                                            onClick={() => handleVariationSelect('size', size.variation_value)}
                                            className={`px-4 py-2 border rounded-md text-sm font-medium transition-all ${
                                                selectedVariations['size'] === size.variation_value
                                                    ? 'border-blue-600 bg-blue-50 text-blue-700 ring-1 ring-blue-600'
                                                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                                            }`}
                                        >
                                            {size.variation_value}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Feedback Messages */}
                    {error && (
                        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-md mb-4 text-sm font-medium">
                            {error}
                        </div>
                    )}
                    {addMessage && (
                        <div className="bg-green-50 text-green-600 px-4 py-3 rounded-md mb-4 text-sm font-medium">
                            {addMessage}
                        </div>
                    )}

                    {/* Action Button */}
                    <button
                        onClick={handleAddToCart}
                        disabled={isAddingToCart || !product.is_available || product.stock <= 0}
                        className={`w-full py-4 px-8 rounded-lg font-bold text-white text-lg transition-all ${
                            isAddingToCart || !product.is_available || product.stock <= 0
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg'
                        }`}
                    >
                        {!product.is_available || product.stock <= 0 
                            ? "Out of Stock" 
                            : isAddingToCart 
                                ? "Adding..." 
                                : "Add to Cart"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProductDetail;
