#!/usr/bin/env python3
"""
Dynamic Email Sender - Send emails to multiple recipients
"""

import smtplib
import ssl
import json
import os
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import certifi

class DynamicEmailSender:
    def __init__(self):
        self.config_file = "gmail_config.json"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def load_config(self):
        """Load Gmail configuration"""
        try:
            # Try multiple possible locations
            possible_paths = [
                self.config_file,  # Current directory
                os.path.join(os.path.dirname(__file__), self.config_file),  # Same directory as this file
                os.path.join(os.path.dirname(__file__), "..", self.config_file),  # Parent directory
                os.path.join(os.path.dirname(__file__), "..", "count-r-server", self.config_file)  # From root
            ]
            
            for config_file in possible_paths:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        return json.load(f)
            return None
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return None
    
    def create_ssl_context(self):
        """Create SSL context with proper certificate handling"""
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            return context
        except ImportError:
            context = ssl.create_default_context()
            return context
        except Exception:
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
            return f"❌ Error sending email to {to_email}: {str(e)}"
    
    def send_to_multiple_recipients(self, recipients, subject, body, from_email=None):
        """Send the same email to multiple recipients"""
        results = []
        total = len(recipients)
        
        print(f" Sending email to {total} recipients...")
        
        for i, recipient in enumerate(recipients, 1):
            print(f" [{i}/{total}] Sending to {recipient}...")
            result = self.send_email(recipient.strip(), subject, body, from_email)
            results.append((recipient, result))
            print(f"    {result}")
        
        return results
    
    def send_personalized_emails(self, recipients_data, subject_template, body_template, from_email=None):
        """Send personalized emails to multiple recipients"""
        results = []
        total = len(recipients_data)
        
        print(f" Sending personalized emails to {total} recipients...")
        
        for i, recipient_data in enumerate(recipients_data, 1):
            email = recipient_data['email']
            name = recipient_data.get('name', 'there')
            
            # Personalize subject and body
            personalized_subject = subject_template.replace('{name}', name)
            personalized_body = body_template.replace('{name}', name)
            
            print(f" [{i}/{total}] Sending personalized email to {email} (Dear {name})...")
            result = self.send_email(email.strip(), personalized_subject, personalized_body, from_email)
            results.append((email, result))
            print(f"    {result}")
        
        return results
    
    def load_recipients_from_csv(self, csv_file):
        """Load recipients from CSV file"""
        recipients = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    recipients.append(row)
            print(f"✅ Loaded {len(recipients)} recipients from {csv_file}")
            return recipients
        except Exception as e:
            print(f"❌ Error loading CSV file: {e}")
            return []
    
    def create_sample_csv(self, filename="recipients.csv"):
        """Create a sample CSV file for recipients"""
        sample_data = [
            {'email': 'recipient1@example.com', 'name': 'John Doe'},
            {'email': 'recipient2@example.com', 'name': 'Jane Smith'},
            {'email': 'recipient3@example.com', 'name': 'Bob Johnson'},
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['email', 'name'])
                writer.writeheader()
                writer.writerows(sample_data)
            print(f"✅ Created sample CSV file: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error creating CSV file: {e}")
            return False

def main():
    """Main function"""
    sender = DynamicEmailSender()
    
    print("📧 Dynamic Email Sender")
    print("=" * 40)
    
    print("Choose an option:")
    print("1. Send to multiple recipients (manual input)")
    print("2. Send personalized emails (manual input)")
    print("3. Send to recipients from CSV file")
    print("4. Send personalized emails from CSV file")
    print("5. Create sample CSV file")
    print("6. Test single email")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        # Send to multiple recipients
        print("\nEnter email addresses (one per line, press Enter twice to finish):")
        recipients = []
        while True:
            email = input().strip()
            if email == "":
                break
            recipients.append(email)
        
        if recipients:
            subject = input("Subject: ").strip()
            print("Message (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    lines.pop()
                    break
                lines.append(line)
            body = "\n".join(lines)
            
            if subject and body:
                sender.send_to_multiple_recipients(recipients, subject, body)
            else:
                print("❌ Subject and message are required")
        else:
            print("❌ No recipients provided")
    
    elif choice == "2":
        # Send personalized emails
        print("\nEnter recipient data (email:name format, one per line, press Enter twice to finish):")
        recipients_data = []
        while True:
            line = input().strip()
            if line == "":
                break
            if ':' in line:
                email, name = line.split(':', 1)
                recipients_data.append({'email': email.strip(), 'name': name.strip()})
            else:
                recipients_data.append({'email': line.strip(), 'name': 'there'})
        
        if recipients_data:
            subject_template = input("Subject template (use {name} for personalization): ").strip()
            print("Message template (use {name} for personalization, press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    lines.pop()
                    break
                lines.append(line)
            body_template = "\n".join(lines)
            
            if subject_template and body_template:
                sender.send_personalized_emails(recipients_data, subject_template, body_template)
            else:
                print("❌ Subject and message templates are required")
        else:
            print("❌ No recipients provided")
    
    elif choice == "3":
        # Send to recipients from CSV
        csv_file = input("CSV file path: ").strip()
        if not csv_file:
            csv_file = "recipients.csv"
        
        recipients_data = sender.load_recipients_from_csv(csv_file)
        if recipients_data:
            recipients = [r['email'] for r in recipients_data]
            subject = input("Subject: ").strip()
            print("Message (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    lines.pop()
                    break
                lines.append(line)
            body = "\n".join(lines)
            
            if subject and body:
                sender.send_to_multiple_recipients(recipients, subject, body)
            else:
                print("❌ Subject and message are required")
    
    elif choice == "4":
        # Send personalized emails from CSV
        csv_file = input("CSV file path: ").strip()
        if not csv_file:
            csv_file = "recipients.csv"
        
        recipients_data = sender.load_recipients_from_csv(csv_file)
        if recipients_data:
            subject_template = input("Subject template (use {name} for personalization): ").strip()
            print("Message template (use {name} for personalization, press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    lines.pop()
                    break
                lines.append(line)
            body_template = "\n".join(lines)
            
            if subject_template and body_template:
                sender.send_personalized_emails(recipients_data, subject_template, body_template)
            else:
                print("❌ Subject and message templates are required")
    
    elif choice == "5":
        # Create sample CSV
        filename = input("CSV filename (default: recipients.csv): ").strip()
        if not filename:
            filename = "recipients.csv"
        sender.create_sample_csv(filename)
    
    elif choice == "6":
        # Test single email
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
        body = "\n".join(lines)
        
        if to_email and subject and body:
            result = sender.send_email(to_email, subject, body)
            print(result)
        else:
            print("❌ All fields are required")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 