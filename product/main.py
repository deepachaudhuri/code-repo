#!/usr/bin/env python3
"""
Product Catalog Service

Simple Flask REST API for an e-commerce product catalog.
"""

from flask import Flask, jsonify
import os
import socket
from datetime import datetime

app = Flask(__name__)

HOSTNAME = socket.gethostname()
CONTAINER_ID = os.getenv('HOSTNAME', 'unknown')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
VERSION = os.getenv('VERSION', '1.0.0')

PRODUCTS = [
    {"id": "sku-101", "name": "Wireless Headphones", "price": 79.99, "category": "audio"},
    {"id": "sku-102", "name": "Smart Watch", "price": 149.99, "category": "wearables"},
    {"id": "sku-103", "name": "Desk Lamp", "price": 39.50, "category": "home"},
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'product',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/products', methods=['GET'])
def list_products():
    return jsonify({
        'service': 'product',
        'version': VERSION,
        'environment': ENVIRONMENT,
        'products': PRODUCTS
    })

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = next((item for item in PRODUCTS if item['id'] == product_id), None)
    if product is None:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'service': 'product',
        'product': product,
        'hostname': HOSTNAME,
        'container_id': CONTAINER_ID,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Welcome to the ShopCart Product Service',
        'endpoints': {
            'health': '/health',
            'products': '/products',
            'product_detail': '/products/<product_id>'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
