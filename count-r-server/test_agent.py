#!/usr/bin/env python3
"""
Test script for the MCP agent and Gmail functionality
"""

from mcp_agent import MCPAgent
import time

def test_agent():
    """Test the MCP agent functionality"""
    print("🧪 Testing MCP Agent...")
    
    # Create agent
    agent = MCPAgent()
    
    # Test connection
    if not agent.connect():
        print("❌ Failed to connect to server")
        return False
    
    print("✅ Connection successful!")
    
    # Test count_r tool
    print("\n📊 Testing count_r tool...")
    result = agent.count_letter_r("mirror")
    if result == 2:
        print("✅ count_r tool working correctly")
    else:
        print(f"❌ count_r tool failed, expected 2, got {result}")
    
    # Test desktop tools
    print("\n📁 Testing desktop tools...")
    agent.get_desktop_location()
    agent.list_desktop_files()
    
    # Test Gmail tools
    print("\n📧 Testing Gmail tools...")
    print("Opening Gmail in 3 seconds...")
    time.sleep(3)
    agent.open_gmail()
    
    print("\nOpening Gmail compose in 3 seconds...")
    time.sleep(3)
    agent.open_gmail_compose()
    
    # Test sendmail tools
    print("\n📧 Testing sendmail tools...")
    print("Testing sendmail functionality...")
    result = agent.send_simple_email(
        "test@example.com", 
        "Test Email from MCP Server", 
        "This is a test email sent from the MCP server."
    )
    print(f"Sendmail result: {result}")
    
    print("\n✅ All tests completed!")
    return True

if __name__ == "__main__":
    test_agent() 