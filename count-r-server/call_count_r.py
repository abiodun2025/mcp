from mcp.client import MCPClient

client = MCPClient("127.0.0.1", 5000)
result = client.call_tool("count_r", word="mirror")
print(result)  # Output should be 2 