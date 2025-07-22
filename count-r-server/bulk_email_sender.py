#!/usr/bin/env python3
"""
Bulk Email Sender - Command line tool for sending emails to multiple recipients
"""

import argparse
import sys
from dynamic_email_sender import DynamicEmailSender

def main():
    parser = argparse.ArgumentParser(description='Send emails to multiple recipients')
    parser.add_argument('--recipients', '-r', nargs='+', help='List of email addresses')
    parser.add_argument('--csv', '-c', help='CSV file with recipients (email,name format)')
    parser.add_argument('--subject', '-s', required=True, help='Email subject')
    parser.add_argument('--message', '-m', help='Email message (or use --file)')
    parser.add_argument('--file', '-f', help='File containing email message')
    parser.add_argument('--personalize', '-p', action='store_true', help='Personalize emails using {name} template')
    parser.add_argument('--test', '-t', action='store_true', help='Test mode (only show what would be sent)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.recipients and not args.csv:
        print("❌ Error: Must provide either --recipients or --csv")
        sys.exit(1)
    
    if not args.message and not args.file:
        print("❌ Error: Must provide either --message or --file")
        sys.exit(1)
    
    # Load message
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                message = f.read()
        except Exception as e:
            print(f"❌ Error reading file {args.file}: {e}")
            sys.exit(1)
    else:
        message = args.message
    
    # Initialize sender
    sender = DynamicEmailSender()
    
    # Check configuration
    config = sender.load_config()
    if not config:
        print("❌ Gmail configuration not found. Please run gmail_config.py first.")
        sys.exit(1)
    
    if args.test:
        print("🧪 TEST MODE - No emails will be sent")
        print(f"From: {config['email']}")
        print(f"Subject: {args.subject}")
        print(f"Message: {message[:100]}...")
        
        if args.recipients:
            print(f"Recipients: {', '.join(args.recipients)}")
        elif args.csv:
            recipients_data = sender.load_recipients_from_csv(args.csv)
            if recipients_data:
                recipients = [r['email'] for r in recipients_data]
                print(f"Recipients from CSV: {', '.join(recipients)}")
        
        print("\n✅ Test mode completed")
        return
    
    # Send emails
    if args.recipients:
        if args.personalize:
            print("❌ Personalization requires CSV file with name column")
            sys.exit(1)
        
        print(f"📧 Sending email to {len(args.recipients)} recipients...")
        results = sender.send_to_multiple_recipients(args.recipients, args.subject, message)
        
    elif args.csv:
        recipients_data = sender.load_recipients_from_csv(args.csv)
        if not recipients_data:
            print(f"❌ No recipients found in {args.csv}")
            sys.exit(1)
        
        if args.personalize:
            print(f"📧 Sending personalized emails to {len(recipients_data)} recipients...")
            results = sender.send_personalized_emails(recipients_data, args.subject, message)
        else:
            recipients = [r['email'] for r in recipients_data]
            print(f"📧 Sending email to {len(recipients)} recipients...")
            results = sender.send_to_multiple_recipients(recipients, args.subject, message)
    
    # Summary
    successful = sum(1 for _, result in results if "✅" in result)
    failed = len(results) - successful
    
    print(f"\n📊 Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📧 Total: {len(results)}")

if __name__ == "__main__":
    main() 