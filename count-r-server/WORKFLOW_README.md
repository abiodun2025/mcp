# Workflow Orchestration System

This MCP server provides a comprehensive workflow orchestration system that allows you to define and execute multi-step workflows with dependencies, validation, and conditional execution.

## 🚀 Quick Start

1. **Start the MCP server:**
   ```bash
   cd count-r-server
   source .venv/bin/activate
   python server.py
   ```

2. **Test the workflow system:**
   ```bash
   python test_workflow_tools.py
   ```

## 🔧 Available Workflow Tools

The server provides the following workflow orchestration tools:

### Core Workflow Tools

- **`list_workflows`** - List all available workflows
- **`execute_workflow`** - Execute a workflow by name
- **`get_workflow_status`** - Get status of a workflow execution
- **`list_executions`** - List all workflow executions
- **`cancel_workflow`** - Cancel a running workflow
- **`register_workflow`** - Register a new workflow with custom steps
- **`create_custom_workflow`** - Create a simple custom workflow

### Predefined Workflows

1. **`data_processing`** - Fetch data → Validate → Summarize → Notify user
2. **`email_campaign`** - Prepare recipients → Validate → Send emails → Confirm delivery
3. **`file_analysis`** - Scan directory → Analyze files → Generate report → Save report

## 📋 How to Use from External Agent

Your external agent can call these workflow tools using HTTP POST requests to the MCP server:

### Example: List Available Workflows
```python
import requests

response = requests.post("http://127.0.0.1:5000/tools/list_workflows")
workflows = response.json()
print(workflows)
```

### Example: Execute a Workflow
```python
import requests

# Execute data processing workflow
response = requests.post("http://127.0.0.1:5000/tools/execute_workflow", 
                        json={"workflow_name": "data_processing"})
result = response.json()
execution_id = result.split(": ")[1].strip()
print(f"Started execution: {execution_id}")
```

### Example: Monitor Workflow Status
```python
import requests
import time

execution_id = "data_processing_1234567890"

while True:
    response = requests.post("http://127.0.0.1:5000/tools/get_workflow_status", 
                           json={"execution_id": execution_id})
    status_data = response.json()
    
    if status_data["status"] in ["completed", "failed", "cancelled"]:
        print(f"Workflow {status_data['status']}!")
        break
    
    time.sleep(2)
```

### Example: Register Custom Workflow
```python
import requests
import json

# Define workflow steps
steps = [
    {
        "name": "step1",
        "description": "Get desktop path",
        "tool_name": "get_desktop_path",
        "parameters": {},
        "validation_rules": {"required_fields": ["status"]}
    },
    {
        "name": "step2", 
        "description": "Count letters in word",
        "tool_name": "count_r",
        "parameters": {"word": "hello"},
        "depends_on": ["step1"]
    }
]

# Register workflow
response = requests.post("http://127.0.0.1:5000/tools/register_workflow",
                        json={"name": "my_workflow", "steps_json": json.dumps(steps)})
print(response.json())
```

## 🔄 Workflow Features

### Dependencies
Steps can depend on other steps using the `depends_on` parameter:
```json
{
    "name": "step2",
    "depends_on": ["step1"],
    "tool_name": "count_r"
}
```

### Conditional Execution
Steps can have conditions for execution:
```json
{
    "name": "notify_user",
    "condition": "results.get('validate_data', {}).get('status') == 'success'",
    "tool_name": "open_gmail"
}
```

### Parameter Substitution
Use `{{step_name}}` to reference results from previous steps:
```json
{
    "name": "validate_data",
    "parameters": {"word": "{{fetch_data.result}}"},
    "tool_name": "count_r"
}
```

### Validation Rules
Define validation rules for step results:
```json
{
    "name": "fetch_data",
    "validation_rules": {
        "required_fields": ["status"],
        "expected_status": "success"
    }
}
```

## 📊 Workflow Execution States

- **`pending`** - Workflow is queued for execution
- **`running`** - Workflow is currently executing
- **`completed`** - Workflow finished successfully
- **`failed`** - Workflow encountered an error
- **`cancelled`** - Workflow was cancelled

## 🛠️ Available Tools for Workflows

The following MCP tools can be used in workflow steps:

- `count_r` - Count 'r' letters in a word
- `list_desktop_contents` - List desktop files
- `get_desktop_path` - Get desktop path
- `open_gmail` - Open Gmail in browser
- `open_gmail_compose` - Open Gmail compose
- `sendmail` - Send email using sendmail
- `sendmail_simple` - Send simple email

## 🔍 Testing

Run the test suite to see all features in action:
```bash
python test_workflow_tools.py
```

This will demonstrate:
- Listing workflows
- Executing predefined workflows
- Monitoring execution status
- Creating custom workflows
- Registering workflows with custom steps

## 📝 Example Workflow Definitions

### Data Processing Workflow
```json
[
    {
        "name": "fetch_data",
        "description": "Fetch data from source",
        "tool_name": "list_desktop_contents"
    },
    {
        "name": "validate_data", 
        "description": "Validate fetched data",
        "tool_name": "count_r",
        "parameters": {"word": "{{fetch_data.result}}"},
        "depends_on": ["fetch_data"]
    },
    {
        "name": "summarize_data",
        "description": "Create summary",
        "tool_name": "get_desktop_path",
        "depends_on": ["validate_data"]
    },
    {
        "name": "notify_user",
        "description": "Send notification",
        "tool_name": "open_gmail",
        "depends_on": ["summarize_data"],
        "condition": "results.get('summarize_data', {}).get('status') == 'success'"
    }
]
```

This workflow orchestration system provides a powerful foundation for building complex multi-step processes with your MCP server! 