from fastmcp import FastMCP
from fastapi import FastAPI

from encompass_api_documentation_server import mcp_documentation
from weatherserver import mcp_weather

# Create a FastAPI app
app = FastAPI()

# Mount each FastMCP server under a distinct path
app.mount("/weather/mcp", mcp_weather.streamable_http_app()) # Access at http://localhost:8000/weather/mcp
app.mount("/documentation/mcp", mcp_documentation.http_app()) # Access at http://localhost:8000/documentation/mcp

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


