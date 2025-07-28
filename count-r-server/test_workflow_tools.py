#!/usr/bin/env python3
"""
Test Workflow Tools - Simple demonstration of workflow orchestration tools
"""

import requests
import json
import time

class WorkflowTester:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """Initialize the workflow tester"""
        self.base_url = f"http://{host}:{port}"
        
    def call_tool(self, tool_name: str, **kwargs):
        """Call a tool on the MCP server"""
        try:
            url = f"{self.base_url}/tools/{tool_name}"
            response = requests.post(url, json=kwargs, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error calling tool {tool_name}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            return None
    
    def test_list_workflows(self):
        """Test listing available workflows"""
        print("\n🔧 Testing: List Workflows")
        print("=" * 40)
        result = self.call_tool("list_workflows")
        if result:
            print("✅ Available workflows:")
            workflows = result.get("workflows", [])
            for workflow in workflows:
                print(f"  - {workflow}")
        else:
            print("❌ Failed to list workflows")
    
    def test_execute_data_processing_workflow(self):
        """Test executing the data processing workflow"""
        print("\n🔄 Testing: Data Processing Workflow")
        print("=" * 40)
        print("Steps: Fetch data → Validate → Summarize → Notify user")
        
        # Execute workflow
        result = self.call_tool("execute_workflow", workflow_name="data_processing")
        if result and "Started workflow execution:" in result:
            execution_id = result.split(": ")[1].strip()
            print(f"✅ Started execution: {execution_id}")
            
            # Monitor execution
            self.monitor_execution(execution_id)
        else:
            print("❌ Failed to start workflow")
    
    def test_execute_email_campaign_workflow(self):
        """Test executing the email campaign workflow"""
        print("\n📧 Testing: Email Campaign Workflow")
        print("=" * 40)
        print("Steps: Prepare recipients → Validate → Send emails → Confirm delivery")
        
        # Execute workflow
        result = self.call_tool("execute_workflow", workflow_name="email_campaign")
        if result and "Started workflow execution:" in result:
            execution_id = result.split(": ")[1].strip()
            print(f"✅ Started execution: {execution_id}")
            
            # Monitor execution
            self.monitor_execution(execution_id)
        else:
            print("❌ Failed to start workflow")
    
    def test_execute_file_analysis_workflow(self):
        """Test executing the file analysis workflow"""
        print("\n📁 Testing: File Analysis Workflow")
        print("=" * 40)
        print("Steps: Scan directory → Analyze files → Generate report → Save report")
        
        # Execute workflow
        result = self.call_tool("execute_workflow", workflow_name="file_analysis")
        if result and "Started workflow execution:" in result:
            execution_id = result.split(": ")[1].strip()
            print(f"✅ Started execution: {execution_id}")
            
            # Monitor execution
            self.monitor_execution(execution_id)
        else:
            print("❌ Failed to start workflow")
    
    def monitor_execution(self, execution_id: str, max_checks: int = 10):
        """Monitor a workflow execution"""
        print(f"👀 Monitoring execution: {execution_id}")
        
        for i in range(max_checks):
            result = self.call_tool("get_workflow_status", execution_id=execution_id)
            if result and not result.startswith("❌"):
                try:
                    status_data = json.loads(result)
                    status = status_data.get("status", "unknown")
                    current_step = status_data.get("current_step", 0)
                    
                    print(f"  📊 Status: {status.upper()}, Step: {current_step}")
                    
                    if status in ["completed", "failed", "cancelled"]:
                        print(f"  ✅ Workflow {status}!")
                        if status_data.get("results"):
                            print("  📋 Results:")
                            for step_name, step_result in status_data["results"].items():
                                print(f"    - {step_name}: {step_result.get('status', 'unknown')}")
                        if status_data.get("errors"):
                            print("  ❌ Errors:")
                            for error in status_data["errors"]:
                                print(f"    - {error}")
                        break
                    
                    time.sleep(2)  # Wait 2 seconds before next check
                    
                except json.JSONDecodeError:
                    print(f"  ❌ Invalid JSON response: {result}")
                    break
            else:
                print(f"  ❌ Failed to get status: {result}")
                break
        else:
            print(f"  ⏰ Monitoring timeout after {max_checks} checks")
    
    def test_list_executions(self):
        """Test listing all executions"""
        print("\n📋 Testing: List Executions")
        print("=" * 40)
        result = self.call_tool("list_executions")
        if result:
            executions = result.get("executions", [])
            print(f"✅ Found {len(executions)} executions:")
            for execution in executions:
                print(f"  - {execution['workflow_name']}: {execution['status']} (ID: {execution['workflow_id']})")
        else:
            print("❌ Failed to list executions")
    
    def test_create_custom_workflow(self):
        """Test creating a custom workflow"""
        print("\n🔨 Testing: Create Custom Workflow")
        print("=" * 40)
        
        # Create a simple custom workflow
        result = self.call_tool("create_custom_workflow", 
                               name="test_workflow",
                               description="A test workflow for demonstration",
                               steps_description="Step 1: List desktop, Step 2: Count letters")
        
        if result and "created successfully" in result:
            print("✅ Custom workflow created successfully")
            
            # Test executing the custom workflow
            print("🔄 Testing execution of custom workflow...")
            exec_result = self.call_tool("execute_workflow", workflow_name="test_workflow")
            if exec_result and "Started workflow execution:" in exec_result:
                execution_id = exec_result.split(": ")[1].strip()
                print(f"✅ Started custom workflow execution: {execution_id}")
                self.monitor_execution(execution_id)
            else:
                print("❌ Failed to execute custom workflow")
        else:
            print("❌ Failed to create custom workflow")
    
    def test_register_custom_workflow(self):
        """Test registering a workflow with custom steps"""
        print("\n📝 Testing: Register Custom Workflow")
        print("=" * 40)
        
        # Define custom workflow steps
        custom_steps = [
            {
                "name": "step1",
                "description": "First step - get desktop path",
                "tool_name": "get_desktop_path",
                "parameters": {},
                "validation_rules": {"required_fields": ["status"]}
            },
            {
                "name": "step2",
                "description": "Second step - count letters in a word",
                "tool_name": "count_r",
                "parameters": {"word": "hello"},
                "depends_on": ["step1"],
                "validation_rules": {"expected_status": "success"}
            },
            {
                "name": "step3",
                "description": "Third step - open Gmail",
                "tool_name": "open_gmail",
                "parameters": {},
                "depends_on": ["step2"],
                "condition": "results.get('step2', {}).get('status') == 'success'"
            }
        ]
        
        steps_json = json.dumps(custom_steps)
        result = self.call_tool("register_workflow", name="custom_demo", steps_json=steps_json)
        
        if result and "registered successfully" in result:
            print("✅ Custom workflow registered successfully")
            
            # Test executing the registered workflow
            print("🔄 Testing execution of registered workflow...")
            exec_result = self.call_tool("execute_workflow", workflow_name="custom_demo")
            if exec_result and "Started workflow execution:" in exec_result:
                execution_id = exec_result.split(": ")[1].strip()
                print(f"✅ Started registered workflow execution: {execution_id}")
                self.monitor_execution(execution_id)
            else:
                print("❌ Failed to execute registered workflow")
        else:
            print("❌ Failed to register custom workflow")
    
    def run_all_tests(self):
        """Run all workflow tests"""
        print("🚀 Starting Workflow Tools Test Suite")
        print("=" * 60)
        
        # Test 1: List workflows
        self.test_list_workflows()
        
        # Test 2: Execute data processing workflow
        self.test_execute_data_processing_workflow()
        
        # Test 3: Execute email campaign workflow
        self.test_execute_email_campaign_workflow()
        
        # Test 4: Execute file analysis workflow
        self.test_execute_file_analysis_workflow()
        
        # Test 5: List executions
        self.test_list_executions()
        
        # Test 6: Create custom workflow
        self.test_create_custom_workflow()
        
        # Test 7: Register custom workflow
        self.test_register_custom_workflow()
        
        print("\n✅ All tests completed!")

def main():
    """Main function to run the workflow tests"""
    print("🔧 Workflow Tools Test Suite")
    print("This script demonstrates how to use the workflow orchestration tools")
    print("Make sure the MCP server is running on 127.0.0.1:5000")
    print()
    
    tester = WorkflowTester()
    
    # Check if server is running
    try:
        result = tester.call_tool("list_workflows")
        if not result:
            print("❌ Could not connect to MCP server. Make sure it's running.")
            print("💡 Start the server with: cd count-r-server && python server.py")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the MCP server is running on 127.0.0.1:5000")
        return
    
    print("✅ Connected to MCP server successfully!")
    
    # Run all tests
    tester.run_all_tests()

if __name__ == "__main__":
    main() 