# MCP Server with Gmail Integration

This project provides an MCP (Model Context Protocol) server with various tools including Gmail integration.

## Features

- **Count 'r' letters**: Count occurrences of 'r' in any word
- **Desktop operations**: List desktop contents and get desktop path
- **Gmail integration**: Open Gmail and Gmail compose window in browser
- **Email sending**: Send emails using system sendmail command
- **Interactive agent**: User-friendly command-line interface

## Setup

### 1. Start the MCP Server

```bash
cd count-r-server
source .venv/bin/activate
python server.py
```

The server will start on `127.0.0.1:5000`

### 2. Run the Interactive Agent

In a new terminal:

```bash
cd count-r-server
source .venv/bin/activate
python mcp_agent.py
```

## Available Commands

Once the agent is running, you can use these commands:

- `count <word>` - Count 'r' letters in a word
- `desktop` - List desktop contents
- `path` - Get desktop path
- `gmail` - Open Gmail in browser
- `compose` - Open Gmail compose window
- `sendmail` - Send email using sendmail
- `tools` - List available tools
- `help` - Show help
- `quit` - Exit

## Examples

```
🤖 Enter command: count mirror
📊 The word 'mirror' contains 2 'r' letters

🤖 Enter command: gmail
📧 Gmail opened successfully in your default browser

🤖 Enter command: desktop
📁 Desktop contents:
  - working-mcp-server
  - other-files.txt

🤖 Enter command: sendmail
📧 Send Email Interface
To: user@example.com
Subject: Test Email
Message (press Enter twice to finish):
Hello from MCP server!
This is a test email.

📧 Email sent successfully to user@example.com

## Testing

Run the test script to verify everything works:

```bash
cd count-r-server
source .venv/bin/activate
python test_agent.py
```

## Architecture

- **server.py**: MCP server with tool definitions
- **mcp_agent.py**: Interactive agent client
- **test_agent.py**: Test script for verification

## Email Configuration

The sendmail functionality requires:
- A properly configured sendmail service on your system
- Or an alternative mail service (Postfix, Exim, etc.)
- Proper DNS and mail server configuration

To test if sendmail is available:
```bash
which sendmail
```

## Adding New Tools

To add new tools to the server:

1. Add the tool function in `server.py` with the `@mcp.tool()` decorator
2. Update the `get_available_tools()` method in `mcp_agent.py`
3. Add corresponding methods in the `MCPAgent` class

Example:
```python
@mcp.tool(name="my_new_tool")
def my_new_tool(param: str) -> str:
    """
    Description of what this tool does
    """
    return f"Result: {param}"
```

## Troubleshooting

- **Connection failed**: Make sure the server is running on port 5000
- **Import errors**: Ensure you're in the virtual environment
- **Gmail not opening**: Check if your default browser is set correctly 