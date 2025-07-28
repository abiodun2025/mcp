#!/usr/bin/env python3
"""
Google Voice Caller - Automate phone calls via Google Voice using Playwright
"""

import os
import re
import json
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class GoogleVoiceCaller:
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, cookies_path: str = "google_voice_cookies.json", config_file: str = "gmail_config.json"):
        self.config_file = config_file
        self.cookies_path = cookies_path
        
        # Try to get credentials from parameters first, then config file, then environment
        self.email = email or self._load_credentials().get("email") or os.environ.get("GOOGLE_EMAIL")
        self.password = password or self._load_credentials().get("app_password") or os.environ.get("GOOGLE_PASSWORD")
        
        if not self.email or not self.password:
            raise ValueError("Google credentials must be set via config file (gmail_config.json), env vars, or passed to constructor.")
    
    def _load_credentials(self) -> dict:
        """Load credentials from gmail_config.json file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load credentials from {self.config_file}: {e}")
            return {}

    def _load_cookies(self):
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, "r") as f:
                return json.load(f)
        return None

    def _save_cookies(self, context):
        cookies = context.cookies()
        with open(self.cookies_path, "w") as f:
            json.dump(cookies, f)

    def call(self, phone_number: str) -> dict:
        # Validate phone number (E.164)
        if not re.match(r"^\+\d{10,15}$", phone_number):
            return {"status": "error", "message": "Invalid phone number format. Use E.164 (+1234567890)"}
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                # Try to load cookies for persistent session
                cookies = self._load_cookies()
                if cookies:
                    context.add_cookies(cookies)
                page = context.new_page()
                page.goto("https://voice.google.com/u/0/calls", timeout=60000)
                # If not logged in, perform login
                if "Sign in" in page.title():
                    page.goto("https://accounts.google.com/signin/v2/identifier?service=googlevoice")
                    page.fill('input[type="email"]', self.email)
                    page.click('button:has-text("Next")')
                    page.wait_for_timeout(2000)
                    page.fill('input[type="password"]', self.password)
                    page.click('button:has-text("Next")')
                    page.wait_for_load_state('networkidle')
                    # Save cookies after login
                    self._save_cookies(context)
                    page.goto("https://voice.google.com/u/0/calls")
                # Enter phone number and click Call
                page.wait_for_selector('button[aria-label="Make a call"]', timeout=15000)
                page.click('button[aria-label="Make a call"]')
                page.fill('input[aria-label="Phone number"]', phone_number)
                page.click('button[aria-label="Call"]')
                # Optionally, wait for call to start or check for errors
                page.wait_for_timeout(3000)
                browser.close()
                return {"status": "calling", "phone_number": phone_number}
        except PlaywrightTimeoutError as e:
            return {"status": "error", "message": f"Timeout: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Usage example (for testing):
# if __name__ == "__main__":
#     caller = GoogleVoiceCaller()
#     print(caller.call("+1234567890")) 