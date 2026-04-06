"""Test email configuration."""
from flask import Flask
from utils.email_service import mail, send_otp_email, generate_otp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail.init_app(app)

def test_email():
    """Test email sending."""
    print("Testing email configuration...")
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    
    test_email = input("\nEnter email address to send test OTP: ").strip()
    
    if not test_email:
        print("❌ Email address required!")
        return
    
    with app.app_context():
        otp = generate_otp()
        print(f"\n📧 Sending OTP: {otp}")
        
        if send_otp_email(test_email, otp):
            print(f"✅ Test email sent successfully to {test_email}")
            print(f"🔑 OTP: {otp}")
            print("\nCheck your inbox (and spam folder)!")
        else:
            print("❌ Failed to send email. Check your configuration.")
            print("\nCommon issues:")
            print("1. Gmail App Password not set correctly")
            print("2. 2FA not enabled on Gmail")
            print("3. MAIL_USERNAME or MAIL_PASSWORD incorrect in .env")
            print("4. Less secure app access disabled")

if __name__ == '__main__':
    test_email()
