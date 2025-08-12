#!/usr/bin/env python3
"""
Test script for Secrets Detection Tool
Run this to verify the tool is working correctly
"""

import os
import sys
import json
from secrets_detection import secrets_detector

def test_tool_availability():
    """Test if Gitleaks and TruffleHog are available"""
    print("🔍 Testing tool availability...")
    
    gitleaks_available = secrets_detector._check_tool_availability("gitleaks")
    trufflehog_available = secrets_detector._check_tool_availability("trufflehog")
    
    print(f"✅ Gitleaks: {'Available' if gitleaks_available else 'Not found'}")
    print(f"✅ TruffleHog: {'Available' if trufflehog_available else 'Not found'}")
    
    return gitleaks_available, trufflehog_available

def test_configuration():
    """Test configuration functionality"""
    print("\n⚙️ Testing configuration...")
    
    # Get current config
    config = secrets_detector.get_scan_config()
    print(f"✅ Current config retrieved: {len(config)} sections")
    
    # Test config update
    test_update = {
        "gitleaks": {
            "timeout": 600,
            "verbose": True
        }
    }
    
    result = secrets_detector.configure_scan_rules(test_update)
    if result["success"]:
        print("✅ Configuration updated successfully")
        print(f"   New Gitleaks timeout: {result['config']['gitleaks']['timeout']}")
    else:
        print(f"❌ Configuration update failed: {result['error']}")
    
    return result["success"]

def test_scan_functionality():
    """Test basic scan functionality"""
    print("\n🔍 Testing scan functionality...")
    
    # Test scanning current directory
    current_dir = os.getcwd()
    print(f"📁 Scanning current directory: {current_dir}")
    
    try:
        result = secrets_detector.scan_directory(current_dir, recursive=False)
        
        if result.get("success") is not False:  # Handle both success=True and missing success key
            print("✅ Directory scan completed")
            print(f"   Tools used: {result.get('tools_used', [])}")
            print(f"   Total findings: {result.get('total_findings', 0)}")
            print(f"   Duration: {result.get('duration', 0):.2f} seconds")
        else:
            print(f"❌ Directory scan failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Directory scan error: {str(e)}")

def test_scan_history():
    """Test scan history functionality"""
    print("\n📚 Testing scan history...")
    
    # Get scan history
    history = secrets_detector.get_scan_history(5)
    print(f"✅ Scan history retrieved: {len(history)} scans")
    
    if history:
        latest_scan = history[-1]
        print(f"   Latest scan: {latest_scan.get('target', 'Unknown')}")
        print(f"   Scan type: {latest_scan.get('scan_type', 'Unknown')}")
        print(f"   Total findings: {latest_scan.get('total_findings', 0)}")

def main():
    """Main test function"""
    print("🚀 Starting Secrets Detection Tool Tests")
    print("=" * 50)
    
    # Test 1: Tool availability
    gitleaks_available, trufflehog_available = test_tool_availability()
    
    # Test 2: Configuration
    config_success = test_configuration()
    
    # Test 3: Scan functionality (only if tools are available)
    if gitleaks_available or trufflehog_available:
        test_scan_functionality()
    else:
        print("\n⚠️ Skipping scan tests - no tools available")
        print("   Please install Gitleaks and/or TruffleHog to test scanning")
    
    # Test 4: Scan history
    test_scan_history()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Gitleaks: {'✅ Available' if gitleaks_available else '❌ Not found'}")
    print(f"   TruffleHog: {'✅ Available' if trufflehog_available else '❌ Not found'}")
    print(f"   Configuration: {'✅ Working' if config_success else '❌ Failed'}")
    
    if gitleaks_available or trufflehog_available:
        print("   Scanning: ✅ Tested")
    else:
        print("   Scanning: ⚠️ Skipped (tools not available)")
    
    print("   History: ✅ Tested")
    
    print("\n🎯 Next Steps:")
    if not gitleaks_available:
        print("   - Install Gitleaks: brew install gitleaks (macOS) or follow README")
    if not trufflehog_available:
        print("   - Install TruffleHog: brew install trufflesecurity/trufflehog/trufflehog (macOS) or follow README")
    
    print("   - Check SECRETS_DETECTION_README.md for detailed installation instructions")
    print("   - Restart your MCP server to use the new tools")

if __name__ == "__main__":
    main()
