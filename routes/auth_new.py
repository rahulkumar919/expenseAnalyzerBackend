"""Authentication routes with OTP and Google OAuth."""
from flask import Blueprint, request, jsonify
from models.mongodb import (
    get_user_by_email, get_user_by_username, create_user, 
    create_google_user, verify_user, save_otp, verify_otp
)
from utils.email_service import generate_otp, send_otp_email
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

auth_new_bp = Blueprint('auth_new', __name__)

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

def generate_jwt_token(user_id, email):
    """Generate JWT token."""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

@auth_new_bp.route('/auth/register', methods=['POST'])
def register():
    """Register new user - Step 1: Create account."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if get_user_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        if get_user_by_username(username):
            return jsonify({'error': 'Username already taken'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = create_user(username, email, password_hash)
        
        # Generate and send OTP
        otp_code = generate_otp()
        save_otp(email, otp_code)
        
        if send_otp_email(email, otp_code):
            return jsonify({
                'message': 'Registration successful! OTP sent to your email.',
                'email': email,
                'requires_otp': True
            }), 201
        else:
            return jsonify({'error': 'Failed to send OTP. Please try again.'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_new_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp_route():
    """Verify OTP and complete registration."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        otp_code = data.get('otp', '').strip()
        
        if not email or not otp_code:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        # Verify OTP
        if verify_otp(email, otp_code):
            # Mark user as verified
            verify_user(email)
            
            # Get user and generate token
            user = get_user_by_email(email)
            token = generate_jwt_token(user['_id'], user['email'])
            
            return jsonify({
                'message': 'Email verified successfully!',
                'token': token,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_new_bp.route('/auth/login', methods=['POST'])
def login():
    """Login with email/username and password - Step 1."""
    try:
        data = request.get_json()
        identifier = data.get('identifier', '').strip()  # email or username
        password = data.get('password', '')
        
        if not identifier or not password:
            return jsonify({'error': 'Email/Username and password are required'}), 400
        
        # Find user by email or username
        user = get_user_by_email(identifier.lower())
        if not user:
            user = get_user_by_username(identifier)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user registered with Google
        if user.get('auth_provider') == 'google':
            return jsonify({'error': 'Please login with Google'}), 400
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate and send OTP
        otp_code = generate_otp()
        save_otp(user['email'], otp_code)
        
        if send_otp_email(user['email'], otp_code):
            return jsonify({
                'message': 'OTP sent to your email',
                'email': user['email'],
                'requires_otp': True
            }), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_new_bp.route('/auth/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP to email."""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate and send new OTP
        otp_code = generate_otp()
        save_otp(email, otp_code)
        
        if send_otp_email(email, otp_code):
            return jsonify({'message': 'OTP resent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_new_bp.route('/auth/google', methods=['POST'])
def google_login():
    """Login with Google OAuth."""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Google token is required'}), 400
        
        # Verify Google token
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            email = idinfo['email']
            google_id = idinfo['sub']
            name = idinfo.get('name', email.split('@')[0])
            
            # Check if user exists
            user = get_user_by_email(email)
            
            if not user:
                # Create new user
                user = create_google_user(email, name, google_id)
            
            # Generate JWT token
            token = generate_jwt_token(user['_id'], user['email'])
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
            
        except ValueError:
            return jsonify({'error': 'Invalid Google token'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_new_bp.route('/auth/verify-token', methods=['GET'])
def verify_token():
    """Verify JWT token."""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return jsonify({
                'valid': True,
                'user_id': payload['user_id'],
                'email': payload['email']
            }), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
