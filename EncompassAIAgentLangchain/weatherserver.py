# from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP

mcp_weather=FastMCP("Weather")

# @mcp.tool()
# (name: str | None = None, title: str | None = None, description: str | None = None, annotations: ToolAnnotations | None = None, structured_output: bool | None = None) -> ((AnyFunction) -> AnyFunction)
# name
# Optional name for the tool (defaults to function name)
# Decorator to register a tool.
# Tools can optionally request a Context object by adding a parameter with the Context type annotation. The context provides access to MCP capabilities like logging, progress reporting, and resource access.
# Args
# name
# Optional name for the tool (defaults to function name)
# title
# Optional human-readable title for the tool
# description
# Optional description of what the tool does
# annotations
# Optional ToolAnnotations providing additional tool information
# structured_output
# Controls whether the tool's output is structured or unstructured
# If None, auto-detects based on the function's return type annotation
# If True, unconditionally creates a structured tool (return type annotation permitting)
# If False, unconditionally creates an unstructured tool
# Examples
# @server.tool() def my_tool(x: int) -> str: return str(x)
# @server.tool() def tool_with_context(x: int, ctx: Context) -> str: ctx.info(f"Processing {x}") return str(x)
# @server.tool() async def async_tool(x: int, context: Context) -> str: await context.report_progress(50, 100) return str(x)
@mcp_weather.tool()
async def get_weather(location:str)->str:
    """
    Get waether for a given location
    """
    return "I do not know"


# if __name__=="__main__":
#     mcp.run(transport="streamable-http")

# fastmcp cli
# fastmcp run server.py --transport http --host 0.0.0.0 --port 8080 --endpoint /mcp

# In this example:
# transport="http": Specifies that FastMCP should use the Streamable HTTP transport.
# host="<your_url_or_ip>": This should be replaced with the actual IP address or hostname you want your server to listen on. If you're running it locally, 127.0.0.1 or localhost is typically used. To make the server accessible from external machines, you may need to use 0.0.0.0 or the machine's specific IP address.
# port=8000: Defines the port number on which the FastMCP server will listen for connections. 
# Important notes:
# FastMCP will automatically create a /mcp endpoint for clients to connect to when using Streamable HTTP transport. For example, if you run the server on http://localhost:8000, the endpoint would be http://localhost:8000/mcp/.
# Streamable HTTP is the recommended transport for web-based deployments due to its efficiency and bidirectional communication support.
# You can also customize the endpoint path using the httpStream.endpoint option, which defaults to /mcp.
# To connect to your server from other applications or clients, you'll need a FastMCP client that supports the Streamable HTTP transport. 

if __name__ == "__main__":
    mcp_weather.run(
        transport="streamable-http",  # Use "http" for Streamable HTTP
        host="127.0.0.1",  # Listen on all available interfaces
        port=8000,         # Specify your desired port
        # endpoint="/mcp"    # Optional: Customize the endpoint path
    )


# export FASTMCP_HOST="127.0.0.1"
# export FASTMCP_PORT=8000

# if __name__=="__main__":
#     mcp_weather.run(transport="streamable-http")

