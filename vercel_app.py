from flask import Flask, jsonify
from app import app
import traceback
import sys

# This file is specifically for Vercel deployment
# Add detailed error handling
@app.errorhandler(500)
def handle_500_error(error):
    # Get the full error traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_details = {
        'error': str(error),
        'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback)
    }
    return jsonify(error_details), 500

@app.errorhandler(404)
def handle_404_error(error):
    return str(error), 404

if __name__ == '__main__':
    # Enable debug mode only in development
    app.run(host='0.0.0.0', port=5000) 