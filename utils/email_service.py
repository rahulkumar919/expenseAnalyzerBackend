"""Email service for sending OTPs."""
from flask_mail import Mail, Message
import random
import string

mail = Mail()

def generate_otp(length=6):
    """Generate random OTP."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(recipient_email, otp_code):
    """Send OTP via email."""
    try:
        msg = Message(
            subject='ExpenseSense - Your Login OTP',
            recipients=[recipient_email],
            html=f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #58a6ff; text-align: center;">ExpenseSense Pro</h2>
                        <h3 style="color: #333;">Your Login OTP</h3>
                        <p style="color: #666; font-size: 16px;">Hello,</p>
                        <p style="color: #666; font-size: 16px;">Your OTP for login is:</p>
                        <div style="background-color: #f0f6fc; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                            <h1 style="color: #58a6ff; font-size: 36px; letter-spacing: 8px; margin: 0;">{otp_code}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px;">This OTP is valid for 10 minutes.</p>
                        <p style="color: #666; font-size: 14px;">If you didn't request this OTP, please ignore this email.</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">ExpenseSense Pro - Track • Analyze • Save Smartly</p>
                    </div>
                </body>
            </html>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
