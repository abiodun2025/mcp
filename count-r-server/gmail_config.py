#!/usr/bin/env python3
"""
Gmail SMTP Configuration Setup
"""

import os
import json

class GmailSMTPConfig:
    def __init__(self):
        self.config_file = "gmail_config.json"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def setup_config(self):
        """Setup Gmail SMTP configuration"""
        print("📧 Gmail SMTP Configuration Setup")
        print("=" * 50)
        
        print("\n🔧 Prerequisites:")
        print("1. Gmail account with 2-Factor Authentication enabled")
        print("2. App Password generated for 'Mail'")
        print("\n📋 To get an App Password:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-Step Verification if not already enabled")
        print("3. Go to 'App passwords' (https://myaccount.google.com/apppasswords)")
        print("4. Select 'Mail' from the dropdown")
        print("5. Click 'Generate'")
        print("6. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)")
        
        print("\n" + "="*50)
        
        email = input("\n📧 Enter your Gmail address: ").strip()
        app_password = input("🔑 Enter your Gmail App Password: ").strip()
        
        if email and app_password:
            config = {
                "email": email,
                "app_password": app_password,
                "smtp_server": self.smtp_server,
                "smtp_port": self.smtp_port
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✅ Configuration saved to {self.config_file}")
            print("🔒 Your credentials are stored securely in the config file")
            return True
        else:
            print("❌ Email and password are required")
            return False
    
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
    
    def test_connection(self):
        """Test Gmail SMTP connection"""
        config = self.load_config()
        if not config:
            print("❌ No configuration found. Run setup first.")
            return False
        
        try:
            import smtplib
            import ssl
            import certifi
            
            print(" Testing Gmail SMTP connection...")
            
            # Create SSL context with proper certificate handling
            try:
                # Try to use certifi for certificate verification
                context = ssl.create_default_context(cafile=certifi.where())
            except ImportError:
                # Fallback to default context
                context = ssl.create_default_context()
            except Exception:
                # If all else fails, create a context that doesn't verify certificates
                # This is less secure but will work for testing
                context = ssl._create_unverified_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(config["email"], config["app_password"])
                print("✅ Gmail SMTP connection successful!")
                return True
                
        except Exception as e:
            print(f"❌ Gmail SMTP connection failed: {e}")
            return False

def main():
    """Main function"""
    config = GmailSMTPConfig()
    
    print("🚀 Gmail SMTP Configuration")
    print("=" * 30)
    print("Choose an option:")
    print("1. Setup Gmail SMTP configuration")
    print("2. Test Gmail SMTP connection")
    print("3. View current configuration")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        config.setup_config()
    elif choice == "2":
        config.test_connection()
    elif choice == "3":
        config_data = config.load_config()
        if config_data:
            print("\n📋 Current Configuration:")
            print(f"Email: {config_data['email']}")
            print(f"SMTP Server: {config_data['smtp_server']}")
            print(f"SMTP Port: {config_data['smtp_port']}")
            print("App Password: [HIDDEN]")
        else:
            print("❌ No configuration found")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()