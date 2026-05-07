import React from 'react';
import { Link } from 'react-router-dom';

const ProductCard = ({ product }) => {
    return (
        <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
            <Link to={`/store/${product.slug}`}>
                <img 
                    src={product.images} 
                    alt={product.product_name} 
                    loading="lazy"
                    className="w-full h-64 object-cover hover:scale-105 transition-transform duration-300"
                />
            </Link>
            <div className="p-4">
                <span className="text-sm text-gray-500 uppercase tracking-wide font-semibold">
                    {product.category?.category_name}
                </span>
                <Link to={`/store/${product.slug}`}>
                    <h3 className="text-lg font-bold text-gray-800 mt-1 mb-2 hover:text-blue-600 transition-colors">
                        {product.product_name}
                    </h3>
                </Link>
                <div className="flex items-center justify-between mt-4">
                    <span className="text-xl font-extrabold text-gray-900">${product.price}</span>
                    <Link 
                        to={`/store/${product.slug}`}
                        className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm"
                    >
                        View Details
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ProductCard;
