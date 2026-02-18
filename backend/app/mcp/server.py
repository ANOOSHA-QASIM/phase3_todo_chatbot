"""
MCP Server for Phase III AI Chatbot
Uses FastMCP to expose task management tools to Cohere AI
"""

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session
from typing import Optional
from datetime import date

# Initialize FastMCP server
mcp = FastMCP("todo-chatbot-mcp")

# Database engine will be shared via lifespan configuration
_engine = None

def set_engine(engine):
    """Set the database engine for MCP tools to use"""
    global _engine
    _engine = engine

def get_session():
    """Get a database session"""
    if _engine is None:
        raise RuntimeError("Database engine not configured")
    return Session(_engine)
