"""
Mail extension configuration.

This module configures email functionality using Flask-Mail.
It provides utilities for sending emails, including password reset links.
"""

from flask_mail import Mail, Message
from flask import current_app, render_template_string
from typing import List, Optional

# Initialize mail extension
mail = Mail()

def init_mail(app):
    """Initialize mail with the application.
    
    Args:
        app: Flask application instance
    """
    mail.init_app(app)

def send_password_reset_email(to_email: str, reset_token: str) -> None:
    """Send password reset email with token.
    
    Args:
        to_email: Recipient email address
        reset_token: Password reset token
    """
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
    
    # HTML template for the email
    html = """
    <h2>Password Recovery</h2>
    <p>You have requested to reset your password. Click the link below to continue:</p>
    <p><a href="{{ reset_url }}">Reset Password</a></p>
    <p>If you didn't request this change, you can ignore this email.</p>
    <p>This link will expire in 1 hour.</p>
    """
    
    # Text version for email clients that don't support HTML
    text = f"""
    Password Recovery

    You have requested to reset your password. Use the link below to continue:
    
    {reset_url}
    
    If you didn't request this change, you can ignore this email.
    This link will expire in 1 hour.
    """
    
    msg = Message(
        subject='Password Recovery - Billax',
        recipients=[to_email],
        body=text,
        html=render_template_string(html, reset_url=reset_url)
    )
    
    mail.send(msg) 