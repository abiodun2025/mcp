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

if __name__ == "__main__":
    try:
        print("Starting MCP server on 127.0.0.1......")
        mcp.run()
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        time.sleep(5)
        sys.exit(1)


     

