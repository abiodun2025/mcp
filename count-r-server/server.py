import sys
import os
import time
import signal

# ✅ Add the parent directory of the script to sys.path before importing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Now import works correctly
from mcp.server.fastmcp import FastMCP

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

if __name__ == "__main__":
    try:
        print("Starting MCP server on 127.0.0.1......")
        mcp.run()
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        time.sleep(5)
        sys.exit(1)


     

