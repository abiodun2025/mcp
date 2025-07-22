#!/usr/bin/env python3
"""
Gmail SMTP Setup Guide
"""

def print_setup_guide():
    """Print Gmail SMTP setup guide"""
    print("📧 Gmail SMTP Setup Guide")
    print("=" * 60)
    
    print("\n Step 1: Enable 2-Factor Authentication")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Click on '2-Step Verification'")
    print("3. Follow the steps to enable it")
    print("4. This is required to generate App Passwords")
    
    print("\n🔑 Step 2: Generate App Password")
    print("1. Go to https://myaccount.google.com/apppasswords")
    print("2. Select 'Mail' from the dropdown menu")
    print("3. Click 'Generate'")
    print("4. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)")
    print("5. Save this password - you'll need it for configuration")
    
    print("\n⚙️  Step 3: Configure Gmail SMTP")
    print("1. Run: python gmail_config.py")
    print("2. Choose option 1: Setup Gmail SMTP configuration")
    print("3. Enter your Gmail address")
    print("4. Enter the App Password (not your regular password)")
    
    print("\n🧪 Step 4: Test the Setup")
    print("1. Run: python gmail_email_sender.py")
    print("2. Choose option 3: Test Gmail SMTP connection")
    print("3. If successful, choose option 1 to send a test email")
    
    print("\n Step 5: Send Email to mywork461@gmail.com")
    print("1. Run: python gmail_email_sender.py")
    print("2. Choose option 1: Send test email")
    print("3. The email will be sent to mywork461@gmail.com")
    
    print("\n⚠️  Troubleshooting:")
    print("- Make sure 2-Factor Authentication is enabled")
    print("- Use App Password, not your regular Gmail password")
    print("- Check that Gmail SMTP is not blocked by firewall")
    print("- Verify the email and password are correct")
    print("- Make sure you're using the App Password, not the regular password")
    
    print("\n📞 Need Help?")
    print("- Check Gmail's security settings")
    print("- Verify App Password was generated correctly")
    print("- Test connection before sending emails")

if __name__ == "__main__":
    print_setup_guide()