from flask import Flask, jsonify, request
from flask_cors import CORS
from models.database import init_db
from routes.auth import auth_bp
from routes.auth_new import auth_new_bp
from routes.expense import expense_bp
from routes.analysis import analysis_bp
from routes.smart import smart_bp
from utils.email_service import mail
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey-change-in-production')

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize Flask-Mail
mail.init_app(app)

# CORS Configuration - Production ready
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://expense-analyzer-steel.vercel.app",
            "http://localhost:3000",
            "http://localhost:5001",
            "http://127.0.0.1:5001"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize Database
if not os.path.exists('expenses.db'):
    init_db()

# Register Blueprints with /api prefix
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(auth_new_bp, url_prefix='/api')  # New auth with OTP
app.register_blueprint(expense_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(smart_bp, url_prefix='/api')

# Root endpoint - API info
@app.route('/')
def index():
    return jsonify({
        'name': 'ExpenseSense Pro API',
        'version': '2.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/signup, /api/login, /api/logout',
            'expenses': '/api/add_expense, /api/expenses/<user_id>',
            'analysis': '/api/analysis/<user_id>'
        }
    }), 200

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Backend is running perfectly!'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
