# /// script
# dependencies = ["mcp[cli]", "httpx"]
# ///

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import fitbit
import gdrive
import withings
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("diet")


@mcp.tool()
def get_fitbit_data(date: str) -> dict:
    """Fetch FitBit activity and sleep data for a given date (YYYY-MM-DD).
    Returns steps, calories burned, activity minutes, sleep minutes, and weight if logged."""
    return fitbit.fetch(date)


@mcp.tool()
def get_withings_data(date: str) -> dict:
    """Fetch Withings scale and sleep data for a given date (YYYY-MM-DD).
    Returns weight, BMI, body composition (fat/muscle/water/bone), and sleep breakdown."""
    return withings.fetch(date)


@mcp.tool()
def gdrive_search(query: str) -> list:
    """Search the personal Google Drive with a raw Drive v3 query string
    (e.g. "name contains 'report' and trashed=false"). Returns file/folder metadata."""
    return gdrive.search(query)


@mcp.tool()
def gdrive_list_folder(folder: str) -> list:
    """List the contents of a folder on the personal Google Drive, by folder name or ID.
    Returns id, name, mimeType, size, and modifiedTime for each item."""
    return gdrive.list_folder(folder)


@mcp.tool()
def gdrive_read_file(ref: str) -> str:
    """Read a file from the personal Google Drive by ID or unique name.
    Google Docs export as plain text and Sheets as CSV; other files return raw text."""
    return gdrive.read(ref)


mcp.run()
