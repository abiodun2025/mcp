import sys
import os
import time
import signal
import asyncio
import json

# ✅ Add the parent directory of the script to sys.path before importing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Now import works correctly
from mcp.server.fastmcp import FastMCP

# Import workflow orchestrator
from workflow_orchestrator import WorkflowOrchestrator, WorkflowStep, WorkflowTemplates
from google_voice_caller import GoogleVoiceCaller
from slack_teams_tools import slack_tools, teams_tools
from github_tools import github_tools

def signal_handler(sig, frame):
    print("Shutting down Server......")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#Here is where we define the instance of the MCP server
mcp = FastMCP(
    name="count-r",
    version="1.0.0",
    host="127.0.0.1",
    port=5000,
    timeout=30,
)

# Initialize workflow orchestrator
workflow_orchestrator = WorkflowOrchestrator()

# Register default workflows
def register_default_workflows():
    """Register default workflow templates"""
    workflow_orchestrator.register_workflow("data_processing", WorkflowTemplates.data_processing_workflow())
    workflow_orchestrator.register_workflow("email_campaign", WorkflowTemplates.email_campaign_workflow())
    workflow_orchestrator.register_workflow("file_analysis", WorkflowTemplates.file_analysis_workflow())
    print("✅ Registered default workflow templates")

register_default_workflows()
#Here is where we define the tools that the server will provide

@mcp.tool()
def count_r(word:str) -> int:
     """
     Count the number of 'r' in a given word
     """
     try:
        if not isinstance(word, str):
            return 0
        return word.lower().count("r")
     except Exception as e:
        return 0

@mcp.tool(name="list_desktop_contents")
def list_desktop_contents() -> list[str]:
    """
    Returns a list of files and folders on the user's Desktop.
    """
    try:
        desktop_path = os.path.expanduser("~/Desktop")
        return os.listdir(desktop_path)
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool(name="get_desktop_path")
def get_desktop_path() -> str:
    """
    Returns the path to the user's Desktop.
    """
    return os.path.expanduser("~/Desktop")

@mcp.tool(name="open_gmail")
def open_gmail() -> str:
    """
    Opens Gmail in the default web browser.
    """
    try:
        import webbrowser
        webbrowser.open("https://mail.google.com")
        return "Gmail opened successfully in your default browser"
    except Exception as e:
        return f"Error opening Gmail: {str(e)}"

@mcp.tool(name="open_gmail_compose")
def open_gmail_compose() -> str:
    """
    Opens Gmail compose window in the default web browser.
    """
    try:
        import webbrowser
        webbrowser.open("https://mail.google.com/mail/u/0/#compose")
        return "Gmail compose window opened successfully"
    except Exception as e:
        return f"Error opening Gmail compose: {str(e)}"

@mcp.tool(name="sendmail")
def sendmail(to_email: str, subject: str, body: str, from_email: str = None) -> str:
    """
    Send an email using the system's sendmail command.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        from_email: Sender email address (optional)
    """
    try:
        import subprocess
        import tempfile
        
        # Create email content
        email_content = f"""From: {from_email or 'noreply@localhost'}
To: {to_email}
Subject: {subject}

{body}
"""
        
        # Write email to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(email_content)
            temp_file_path = temp_file.name
        
        # Send email using sendmail
        result = subprocess.run(
            ['sendmail', '-t'],
            input=email_content,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if result.returncode == 0:
            return f"Email sent successfully to {to_email}"
        else:
            return f"Failed to send email: {result.stderr.decode()}"
            
    except subprocess.TimeoutExpired:
        return "Email sending timed out"
    except FileNotFoundError:
        return "Sendmail command not found. Please install sendmail or configure your system's mail service."
    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.tool(name="sendmail_simple")
def sendmail_simple(to_email: str, subject: str, message: str) -> str:
    """
    Send a simple email using sendmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Email message
    """
    return sendmail(to_email, subject, message)

# Workflow Orchestration Tools

@mcp.tool(name="register_workflow")
def register_workflow(name: str, steps_json: str) -> str:
    """
    Register a new workflow with the orchestrator.
    
    Args:
        name: Name of the workflow
        steps_json: JSON string containing workflow steps
    """
    try:
        steps_data = json.loads(steps_json)
        steps = []
        
        for step_data in steps_data:
            step = WorkflowStep(
                name=step_data["name"],
                description=step_data["description"],
                tool_name=step_data["tool_name"],
                parameters=step_data.get("parameters", {}),
                validation_rules=step_data.get("validation_rules", {}),
                depends_on=step_data.get("depends_on", []),
                condition=step_data.get("condition")
            )
            steps.append(step)
        
        if workflow_orchestrator.register_workflow(name, steps):
            return f"✅ Workflow '{name}' registered successfully with {len(steps)} steps"
        else:
            return f"❌ Failed to register workflow '{name}'"
            
    except Exception as e:
        return f"❌ Error registering workflow: {str(e)}"

@mcp.tool(name="execute_workflow")
def execute_workflow(workflow_name: str, initial_data: str = "{}") -> str:
    """
    Execute a workflow by name.
    
    Args:
        workflow_name: Name of the workflow to execute
        initial_data: JSON string with initial data for the workflow
    """
    try:
        data = json.loads(initial_data) if initial_data else {}
        execution_id = workflow_orchestrator.execute_workflow(workflow_name, data)
        return f"🚀 Started workflow execution: {execution_id}"
    except Exception as e:
        return f"❌ Error executing workflow: {str(e)}"

@mcp.tool(name="get_workflow_status")
def get_workflow_status(execution_id: str) -> str:
    """
    Get the status of a workflow execution.
    
    Args:
        execution_id: The execution ID returned by execute_workflow
    """
    try:
        status = workflow_orchestrator.get_execution_status(execution_id)
        if status:
            return json.dumps(status, indent=2)
        else:
            return f"❌ Execution '{execution_id}' not found"
    except Exception as e:
        return f"❌ Error getting workflow status: {str(e)}"

@mcp.tool(name="list_workflows")
def list_workflows() -> str:
    """
    List all available workflows.
    """
    try:
        workflows = list(workflow_orchestrator.workflows.keys())
        return json.dumps({
            "workflows": workflows,
            "count": len(workflows)
        }, indent=2)
    except Exception as e:
        return f"❌ Error listing workflows: {str(e)}"

@mcp.tool(name="list_executions")
def list_executions() -> str:
    """
    List all workflow executions.
    """
    try:
        executions = workflow_orchestrator.get_all_executions()
        return json.dumps({
            "executions": executions,
            "count": len(executions)
        }, indent=2)
    except Exception as e:
        return f"❌ Error listing executions: {str(e)}"

@mcp.tool(name="cancel_workflow")
def cancel_workflow(execution_id: str) -> str:
    """
    Cancel a running workflow execution.
    
    Args:
        execution_id: The execution ID to cancel
    """
    try:
        if workflow_orchestrator.cancel_execution(execution_id):
            return f"🛑 Cancelled workflow execution: {execution_id}"
        else:
            return f"❌ Could not cancel execution '{execution_id}'"
    except Exception as e:
        return f"❌ Error cancelling workflow: {str(e)}"

@mcp.tool(name="create_custom_workflow")
def create_custom_workflow(name: str, description: str, steps_description: str) -> str:
    """
    Create a custom workflow from a description.
    
    Args:
        name: Name of the workflow
        description: Description of what the workflow does
        steps_description: Description of the workflow steps
    """
    try:
        # This is a simplified version - in a real implementation, you might use AI to parse the description
        # For now, we'll create a basic workflow template
        steps = [
            WorkflowStep(
                name="step_1",
                description="First step of custom workflow",
                tool_name="list_desktop_contents",
                parameters={}
            ),
            WorkflowStep(
                name="step_2", 
                description="Second step of custom workflow",
                tool_name="count_r",
                parameters={"word": "test"},
                depends_on=["step_1"]
            )
        ]
        
        if workflow_orchestrator.register_workflow(name, steps):
            return f"✅ Custom workflow '{name}' created successfully"
        else:
            return f"❌ Failed to create custom workflow '{name}'"
            
    except Exception as e:
        return f"❌ Error creating custom workflow: {str(e)}"

@mcp.tool(name="call_phone", description="Place a phone call using Google Voice")
def call_phone(phone_number: str) -> dict:
    """
    Place a phone call using Google Voice via browser automation.
    Args:
        phone_number: string in E.164 format (e.g., +1234567890)
    Returns:
        JSON dict with status and phone_number, or error message.
    Example JSON-RPC request:
    {
      "jsonrpc": "2.0",
      "id": "1",
      "method": "tools/call",
      "params": {
        "name": "call_phone",
        "arguments": {
          "phone_number": "+123456789"
        }
      }
    }
    """
    try:
        caller = GoogleVoiceCaller()
        result = caller.call(phone_number)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Slack Tools

@mcp.tool(name="slack_post_message")
def slack_post_message(channel: str, message: str, thread_ts: str = None) -> dict:
    """
    Post a message to a Slack channel.
    
    Args:
        channel: Channel name or ID (e.g., "#general" or "C1234567890")
        message: Message text to post
        thread_ts: Optional timestamp to reply in a thread
        
    Returns:
        Dict with status and response details
    """
    return slack_tools.post_message(channel, message, thread_ts)

@mcp.tool(name="slack_post_alert")
def slack_post_alert(channel: str, title: str, message: str, severity: str = "info") -> dict:
    """
    Post an alert message with formatting to Slack.
    
    Args:
        channel: Channel name or ID
        title: Alert title
        message: Alert message
        severity: Alert severity (info, warning, error, success)
        
    Returns:
        Dict with status and response details
    """
    return slack_tools.post_alert(channel, title, message, severity)

@mcp.tool(name="slack_post_rich_message")
def slack_post_rich_message(channel: str, blocks_json: str) -> dict:
    """
    Post a rich message with Slack blocks.
    
    Args:
        channel: Channel name or ID
        blocks_json: JSON string containing Slack block objects
        
    Returns:
        Dict with status and response details
    """
    try:
        blocks = json.loads(blocks_json)
        return slack_tools.post_rich_message(channel, blocks)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON format: {str(e)}"}

@mcp.tool(name="slack_list_channels")
def slack_list_channels() -> dict:
    """
    List all accessible Slack channels.
    
    Returns:
        Dict with list of channels
    """
    return slack_tools.list_channels()

# Teams Tools

@mcp.tool(name="teams_post_message")
def teams_post_message(channel: str, message: str) -> dict:
    """
    Post a message to a Microsoft Teams channel.
    
    Args:
        channel: Channel name (must have webhook configured)
        message: Message text to post
        
    Returns:
        Dict with status and response details
    """
    return teams_tools.post_message(channel, message)

@mcp.tool(name="teams_post_alert")
def teams_post_alert(channel: str, title: str, message: str, severity: str = "info") -> dict:
    """
    Post an alert message with formatting to Microsoft Teams.
    
    Args:
        channel: Channel name
        title: Alert title
        message: Alert message
        severity: Alert severity (info, warning, error, success)
        
    Returns:
        Dict with status and response details
    """
    return teams_tools.post_alert(channel, title, message, severity)

@mcp.tool(name="teams_post_rich_message")
def teams_post_rich_message(channel: str, title: str, text: str, facts_json: str = "[]") -> dict:
    """
    Post a rich message with facts to Microsoft Teams.
    
    Args:
        channel: Channel name
        title: Message title
        text: Message text
        facts_json: JSON string containing list of fact objects with name and value
        
    Returns:
        Dict with status and response details
    """
    try:
        facts = json.loads(facts_json) if facts_json else []
        return teams_tools.post_rich_message(channel, title, text, facts)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON format: {str(e)}"}

@mcp.tool(name="teams_list_channels")
def teams_list_channels() -> dict:
    """
    List all configured Microsoft Teams channels.
    
    Returns:
        Dict with list of configured channels
    """
    return teams_tools.list_channels()

# GitHub Tools

@mcp.tool(name="github_create_pull_request")
def github_create_pull_request(owner: str, repo: str, title: str, body: str, 
                              head: str, base: str = "main") -> dict:
    """
    Create a new pull request on GitHub.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        title: Pull request title
        body: Pull request description
        head: Source branch name
        base: Target branch name (default: main)
        
    Returns:
        Dict with pull request details or error message
    """
    return github_tools.create_pull_request(owner, repo, title, body, head, base)

@mcp.tool(name="github_list_pull_requests")
def github_list_pull_requests(owner: str, repo: str, state: str = "open") -> dict:
    """
    List pull requests in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        state: PR state filter (open, closed, all)
        
    Returns:
        Dict with list of pull requests
    """
    return github_tools.list_pull_requests(owner, repo, state)

@mcp.tool(name="github_get_pull_request")
def github_get_pull_request(owner: str, repo: str, pr_number: int) -> dict:
    """
    Get details of a specific pull request.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pr_number: Pull request number
        
    Returns:
        Dict with pull request details
    """
    return github_tools.get_pull_request(owner, repo, pr_number)

@mcp.tool(name="github_review_pull_request")
def github_review_pull_request(owner: str, repo: str, pr_number: int, 
                              event: str, body: str = "") -> dict:
    """
    Review a pull request (approve, request changes, or comment).
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pr_number: Pull request number
        event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
        body: Review comment
        
    Returns:
        Dict with review details
    """
    return github_tools.review_pull_request(owner, repo, pr_number, event, body)

@mcp.tool(name="github_add_comment_to_pr")
def github_add_comment_to_pr(owner: str, repo: str, pr_number: int, 
                            body: str, commit_id: str = None, path: str = None, 
                            line: int = None) -> dict:
    """
    Add a comment to a pull request.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pr_number: Pull request number
        body: Comment text
        commit_id: Optional commit SHA for line-specific comment
        path: Optional file path for line-specific comment
        line: Optional line number for line-specific comment
        
    Returns:
        Dict with comment details
    """
    return github_tools.add_comment_to_pr(owner, repo, pr_number, body, commit_id, path, line)

@mcp.tool(name="github_merge_pull_request")
def github_merge_pull_request(owner: str, repo: str, pr_number: int, 
                             merge_method: str = "merge") -> dict:
    """
    Merge a pull request.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pr_number: Pull request number
        merge_method: Merge method (merge, squash, rebase)
        
    Returns:
        Dict with merge result
    """
    return github_tools.merge_pull_request(owner, repo, pr_number, merge_method)

@mcp.tool(name="github_get_repository_status")
def github_get_repository_status(owner: str, repo: str) -> dict:
    """
    Get repository status and information.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        
    Returns:
        Dict with repository details
    """
    return github_tools.get_repository_status(owner, repo)

@mcp.tool(name="github_list_branches")
def github_list_branches(owner: str, repo: str) -> dict:
    """
    List branches in a repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        
    Returns:
        Dict with list of branches
    """
    return github_tools.list_branches(owner, repo)

@mcp.tool(name="github_create_branch")
def github_create_branch(owner: str, repo: str, branch_name: str, 
                        source_sha: str) -> dict:
    """
    Create a new branch in a repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        branch_name: Name of the new branch
        source_sha: SHA of the commit to branch from
        
    Returns:
        Dict with branch creation result
    """
    return github_tools.create_branch(owner, repo, branch_name, source_sha)

@mcp.tool(name="github_get_commit_details")
def github_get_commit_details(owner: str, repo: str, commit_sha: str) -> dict:
    """
    Get details of a specific commit.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        commit_sha: SHA of the commit
        
    Returns:
        Dict with commit details
    """
    return github_tools.get_commit_details(owner, repo, commit_sha)

@mcp.tool(name="github_get_file_contents")
def github_get_file_contents(owner: str, repo: str, path: str, 
                            ref: str = "main") -> dict:
    """
    Get contents of a file in the repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: File path in the repository
        ref: Branch or commit reference (default: main)
        
    Returns:
        Dict with file contents
    """
    return github_tools.get_file_contents(owner, repo, path, ref)

@mcp.tool(name="github_analyze_code_changes")
def github_analyze_code_changes(owner: str, repo: str, pr_number: int) -> dict:
    """
    Analyze code changes in a pull request.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        pr_number: Pull request number
        
    Returns:
        Dict with analysis of code changes
    """
    return github_tools.analyze_code_changes(owner, repo, pr_number)

if __name__ == "__main__":
    try:
        print("Starting MCP server on 127.0.0.1......")
        mcp.run()
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        time.sleep(5)
        sys.exit(1)


     

