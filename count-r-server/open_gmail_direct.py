#!/usr/bin/env python3
"""
Direct Gmail opener - opens Gmail without needing the MCP server
"""

import webbrowser
import time

def open_gmail():
    """Open Gmail in the default browser"""
    try:
        print("📧 Opening Gmail in your default browser...")
        webbrowser.open("https://mail.google.com")
        print("✅ Gmail opened successfully!")
        return True
    except Exception as e:
        print(f"❌ Error opening Gmail: {e}")
        return False

def open_gmail_compose():
    """Open Gmail compose window"""
    try:
        print("✉️ Opening Gmail compose window...")
        webbrowser.open("https://mail.google.com/mail/u/0/#compose")
        print("✅ Gmail compose window opened successfully!")
        return True
    except Exception as e:
        print(f"❌ Error opening Gmail compose: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Gmail Opener")
    print("=" * 30)
    print("1. Open Gmail")
    print("2. Open Gmail Compose")
    print("3. Both")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            open_gmail()
        elif choice == "2":
            open_gmail_compose()
        elif choice == "3":
            open_gmail()
            time.sleep(2)
            open_gmail_compose()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 