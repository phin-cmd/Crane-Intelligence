from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from pathlib import Path

application = Flask(__name__)
app = application
CORS(app, origins=["*"])

# Serve static files from frontend directory
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory('frontend/css', filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory('frontend/js', filename)

@app.route('/images/<path:filename>')
def image_files(filename):
    return send_from_directory('frontend/images', filename)

# Serve frontend HTML files
@app.route('/')
def homepage():
    return send_from_directory('frontend', 'homepage.html')

@app.route('/valuation-terminal.html')
def valuation_terminal():
    return send_from_directory('frontend', 'valuation-terminal.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('frontend', 'dashboard.html')

@app.route('/login.html')
def login():
    return send_from_directory('frontend', 'login.html')

@app.route('/signup.html')
def signup():
    return send_from_directory('frontend', 'signup.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    frontend_path = Path('frontend') / filename
    if frontend_path.exists() and frontend_path.is_file():
        return send_from_directory('frontend', filename)
    else:
        # Serve homepage.html for unknown routes
        return send_from_directory('frontend', 'homepage.html')

# API Health endpoint
@app.route('/api/v1/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Crane Intelligence Platform",
        "version": "2.0.0",
        "features": [
            "Bloomberg Terminal Interface",
            "Real-time Market Data",
            "Professional Valuation Tools",
            "Advanced Analytics"
        ]
    })

# API Authentication endpoints
@app.route('/api/v1/auth/login', methods=['POST'])
def login_api():
    return jsonify({
        "status": "success",
        "message": "Demo login successful",
        "user": {
            "id": "demo_user",
            "name": "Demo User",
            "role": "professional"
        },
        "token": "demo_token_12345"
    })

@app.route('/api/v1/auth/signup', methods=['POST'])
def signup_api():
    return jsonify({
        "status": "success",
        "message": "Demo signup successful",
        "user": {
            "id": "new_demo_user",
            "name": "New Demo User",
            "role": "basic"
        }
    })

# API Valuation endpoints
@app.route('/api/v1/valuation/calculate', methods=['POST'])
def calculate_valuation():
    data = request.get_json() or {}
    
    # Demo valuation calculation
    base_value = 250000  # Base crane value
    year_factor = max(0.5, 1 - (2024 - int(data.get('year', 2020))) * 0.05)
    hours_factor = max(0.6, 1 - (int(data.get('hours', 1000)) / 10000) * 0.4)
    condition_factor = int(data.get('condition', 8)) / 10
    
    estimated_value = int(base_value * year_factor * hours_factor * condition_factor)
    
    return jsonify({
        "status": "success",
        "valuation": {
            "estimated_value": estimated_value,
            "confidence_score": 94,
            "deal_grade": "A+",
            "market_position": "Strong Buy",
            "factors": {
                "year_impact": f"{year_factor:.2f}",
                "hours_impact": f"{hours_factor:.2f}",
                "condition_impact": f"{condition_factor:.2f}"
            }
        }
    })

# API Market data endpoints
@app.route('/api/v1/market/overview')
def market_overview():
    return jsonify({
        "status": "success",
        "market_data": {
            "crane_index": {
                "value": 2847.3,
                "change": "+2.4%",
                "trend": "up"
            },
            "heavy_equipment": {
                "value": 1923.7,
                "change": "+1.8%",
                "trend": "up"
            },
            "construction": {
                "value": 3421.9,
                "change": "-0.3%",
                "trend": "down"
            }
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
