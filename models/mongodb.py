"""MongoDB connection and models."""
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['expensesense']

# Collections
users_collection = db['users']
otps_collection = db['otps']
expenses_collection = db['expenses']

# Create indexes
users_collection.create_index('email', unique=True)
users_collection.create_index('username', unique=True)
otps_collection.create_index('email')
otps_collection.create_index('created_at', expireAfterSeconds=600)  # OTP expires after 10 minutes

def get_user_by_email(email):
    """Get user by email."""
    return users_collection.find_one({'email': email})

def get_user_by_username(username):
    """Get user by username."""
    return users_collection.find_one({'username': username})

def create_user(username, email, password_hash):
    """Create new user."""
    user_data = {
        'username': username,
        'email': email,
        'password': password_hash,
        'is_verified': False,
        'auth_provider': 'email',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = users_collection.insert_one(user_data)
    user_data['_id'] = result.inserted_id
    return user_data

def create_google_user(email, username, google_id):
    """Create user from Google OAuth."""
    user_data = {
        'username': username,
        'email': email,
        'google_id': google_id,
        'is_verified': True,
        'auth_provider': 'google',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    result = users_collection.insert_one(user_data)
    user_data['_id'] = result.inserted_id
    return user_data

def verify_user(email):
    """Mark user as verified."""
    users_collection.update_one(
        {'email': email},
        {'$set': {'is_verified': True, 'updated_at': datetime.utcnow()}}
    )

def save_otp(email, otp_code):
    """Save OTP to database."""
    otp_data = {
        'email': email,
        'otp': otp_code,
        'created_at': datetime.utcnow()
    }
    # Delete old OTPs for this email
    otps_collection.delete_many({'email': email})
    # Insert new OTP
    otps_collection.insert_one(otp_data)

def verify_otp(email, otp_code):
    """Verify OTP."""
    otp_record = otps_collection.find_one({'email': email, 'otp': otp_code})
    if otp_record:
        # Delete OTP after verification
        otps_collection.delete_one({'_id': otp_record['_id']})
        return True
    return False
