#!/usr/bin/env python3
"""
Gmail SMTP Email Sender
"""

import smtplib
import ssl
import json
import os
import certifi
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailEmailSender:
    def __init__(self):
        self.config_file = "gmail_config.json"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def load_config(self):
        """Load Gmail configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return None
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return None
    
    def create_ssl_context(self):
        """Create SSL context with proper certificate handling"""
        try:
            # Try to use certifi for certificate verification
            context = ssl.create_default_context(cafile=certifi.where())
            return context
        except ImportError:
            # Fallback to default context
            context = ssl.create_default_context()
            return context
        except Exception:
            # If all else fails, create a context that doesn't verify certificates
            # This is less secure but will work for testing
            context = ssl._create_unverified_context()
            return context
    
    def send_email(self, to_email, subject, body, from_email=None):
        """Send email using Gmail SMTP"""
        config = self.load_config()
        if not config:
            return "❌ Gmail configuration not found. Please run gmail_config.py first."
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or config["email"]
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session with proper SSL context
            context = self.create_ssl_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(config["email"], config["app_password"])
                
                # Send email
                text = msg.as_string()
                server.sendmail(config["email"], to_email, text)
                
            return f"✅ Email sent successfully to {to_email}"
            
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
    
    def send_test_email(self, to_email="mywork461@gmail.com"):
        """Send a test email"""
        subject = "Test Email from Gmail SMTP"
        body = """Hi there!

This is a test email sent using Gmail SMTP through your MCP server.

Features:
- Gmail SMTP authentication
- Secure TLS connection
- MCP server integration

Best regards,
Your MCP Email Agent
"""
        
        print(f" Sending test email to {to_email}...")
        result = self.send_email(to_email, subject, body)
        print(result)
        return result

def main():
    """Main function"""
    sender = GmailEmailSender()
    
    print(" Gmail SMTP Email Sender")
    print("=" * 30)
    
    print("Choose an option:")
    print("1. Send test email to mywork461@gmail.com")
    print("2. Send custom email")
    print("3. Test Gmail SMTP connection")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        sender.send_test_email()
    elif choice == "2":
        to_email = input("To: ").strip()
        subject = input("Subject: ").strip()
        print("Message (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                lines.pop()
                break
            lines.append(line)
        message = "\n".join(lines)
        
        if to_email and subject and message:
            sender.send_email(to_email, subject, message)
        else:
            print("❌ All fields are required")
    elif choice == "3":
        config = sender.load_config()
        if config:
            try:
                import smtplib
                import ssl
                
                print(" Testing Gmail SMTP connection...")
                
                # Use the same SSL context creation method
                context = sender.create_ssl_context()
                
                with smtplib.SMTP(sender.smtp_server, sender.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(config["email"], config["app_password"])
                    print("✅ Gmail SMTP connection successful!")
                    
            except Exception as e:
                print(f"❌ Gmail SMTP connection failed: {e}")
        else:
            print("❌ No configuration found")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()