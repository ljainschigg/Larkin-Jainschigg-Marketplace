# /// script
# dependencies = [
#   "mcp",
#   "cowsay",
# ]
# ///

import cowsay
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-python")


@mcp.tool()
def hello_python(name: str) -> str:
    """Says hello using Python and cowsay."""
    return cowsay.get_output_string("cow", f"Hello, {name}! I am a Python MCP server.")


if __name__ == "__main__":
    mcp.run()
