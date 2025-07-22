#!/usr/bin/env python3
"""
MCP Agent - A comprehensive agent to interact with the MCP server
"""

import sys
import os
import time
import requests
import json
from typing import Dict, Any, List

class MCPAgent:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """Initialize the MCP agent with connection to the server"""
        self.host = host
        self.port = port
        self.client = None
        self.available_tools = []
        
    def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            # Test connection by trying to call a simple tool
            result = self.call_tool("get_desktop_path")
            if result is not None:
                print(f"✅ Connected to MCP server at {self.host}:{self.port}")
                return True
            else:
                print(f"❌ Could not connect to server at {self.host}:{self.port}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools from the server"""
        if not self.client:
            return []
        
        try:
            # This would typically come from the server's tool registry
            # For now, we'll hardcode the known tools
            return [
                "count_r",
                "list_desktop_contents", 
                "get_desktop_path",
                "open_gmail",
                "open_gmail_compose",
                "sendmail",
                "sendmail_simple"
            ]
        except Exception as e:
            print(f"Error getting tools: {e}")
            return []
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a specific tool on the MCP server"""
        try:
            url = f"http://{self.host}:{self.port}/tools/{tool_name}"
            response = requests.post(url, json=kwargs)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error calling tool {tool_name}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            return None
    
    def count_letter_r(self, word: str) -> int:
        """Count the number of 'r' letters in a word"""
        result = self.call_tool("count_r", word=word)
        if result is not None:
            print(f"📊 The word '{word}' contains {result} 'r' letters")
        return result
    
    def list_desktop_files(self) -> List[str]:
        """List files on the desktop"""
        result = self.call_tool("list_desktop_contents")
        if result is not None:
            print("📁 Desktop contents:")
            for item in result:
                print(f"  - {item}")
        return result
    
    def get_desktop_location(self) -> str:
        """Get the desktop path"""
        result = self.call_tool("get_desktop_path")
        if result is not None:
            print(f"📍 Desktop location: {result}")
        return result
    
    def open_gmail(self) -> str:
        """Open Gmail in browser"""
        result = self.call_tool("open_gmail")
        if result is not None:
            print(f"📧 {result}")
        return result
    
    def open_gmail_compose(self) -> str:
        """Open Gmail compose window"""
        result = self.call_tool("open_gmail_compose")
        if result is not None:
            print(f"✉️ {result}")
        return result
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: str = None) -> str:
        """Send an email using sendmail"""
        result = self.call_tool("sendmail", to_email=to_email, subject=subject, body=body, from_email=from_email)
        if result is not None:
            print(f"📧 {result}")
        return result
    
    def send_simple_email(self, to_email: str, subject: str, message: str) -> str:
        """Send a simple email using sendmail"""
        result = self.call_tool("sendmail_simple", to_email=to_email, subject=subject, message=message)
        if result is not None:
            print(f"📧 {result}")
        return result
    
    def interactive_mode(self):
        """Run the agent in interactive mode"""
        print("\n🤖 MCP Agent Interactive Mode")
        print("=" * 40)
        print("Available commands:")
        print("  1. count <word>     - Count 'r' letters in a word")
        print("  2. desktop          - List desktop contents")
        print("  3. path             - Get desktop path")
        print("  4. gmail            - Open Gmail")
        print("  5. compose          - Open Gmail compose")
        print("  6. sendmail         - Send email using sendmail")
        print("  7. tools            - List available tools")
        print("  8. help             - Show this help")
        print("  9. quit             - Exit")
        print("=" * 40)
        
        while True:
            try:
                command = input("\n🤖 Enter command: ").strip().lower()
                
                if command == "quit" or command == "exit":
                    print("👋 Goodbye!")
                    break
                elif command == "help":
                    print("Available commands:")
                    print("  1. count <word>     - Count 'r' letters in a word")
                    print("  2. desktop          - List desktop contents")
                    print("  3. path             - Get desktop path")
                    print("  4. gmail            - Open Gmail")
                    print("  5. compose          - Open Gmail compose")
                    print("  6. sendmail         - Send email using sendmail")
                    print("  7. tools            - List available tools")
                    print("  8. help             - Show this help")
                    print("  9. quit             - Exit")
                elif command == "tools":
                    tools = self.get_available_tools()
                    print("🔧 Available tools:")
                    for tool in tools:
                        print(f"  - {tool}")
                elif command.startswith("count "):
                    word = command[6:].strip()
                    if word:
                        self.count_letter_r(word)
                    else:
                        print("❌ Please provide a word to count")
                elif command == "desktop":
                    self.list_desktop_files()
                elif command == "path":
                    self.get_desktop_location()
                elif command == "gmail":
                    self.open_gmail()
                elif command == "compose":
                    self.open_gmail_compose()
                elif command == "sendmail":
                    print("📧 Send Email Interface")
                    to_email = input("To: ").strip()
                    subject = input("Subject: ").strip()
                    print("Message (press Enter twice to finish):")
                    lines = []
                    while True:
                        line = input()
                        if line == "":
                            break
                        lines.append(line)
                    message = "\n".join(lines)
                    
                    if to_email and subject and message:
                        self.send_simple_email(to_email, subject, message)
                    else:
                        print("❌ Please provide all required fields")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function to run the MCP agent"""
    print("🚀 Starting MCP Agent...")
    
    # Create and connect the agent
    agent = MCPAgent()
    
    if not agent.connect():
        print("❌ Could not connect to MCP server. Make sure the server is running.")
        print("💡 Start the server with: cd count-r-server && source .venv/bin/activate && python server.py")
        return
    
    # Show available tools
    tools = agent.get_available_tools()
    print(f"🔧 Connected! Available tools: {', '.join(tools)}")
    
    # Run interactive mode
    agent.interactive_mode()

if __name__ == "__main__":
    main() 