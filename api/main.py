#!/usr/bin/env python3
"""
LWPlabs API Service

Simple Flask API for demonstration purposes.
"""

from flask import Flask, jsonify
import os
import socket
from datetime import datetime

app = Flask(__name__)

# Get environment info
HOSTNAME = socket.gethostname()
CONTAINER_ID = os.getenv('HOSTNAME', 'unknown')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
VERSION = os.getenv('VERSION', '1.0.0')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'lwplabs-api',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/info', methods=['GET'])
def info():
    """Service information endpoint"""
    return jsonify({
        'service': 'lwplabs-api',
        'version': VERSION,
        'environment': ENVIRONMENT,
        'hostname': HOSTNAME,
        'container_id': CONTAINER_ID,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'lwplabs-api',
        'uptime': 'Check deployment logs',
        'requests_processed': 'N/A'
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Welcome to LWPlabs API',
        'endpoints': {
            'health': '/health',
            'info': '/api/info',
            'status': '/api/status'
        }
    })

if __name__ == '__main__':
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
