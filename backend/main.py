from dotenv import load_dotenv
import os

# ✅ LOAD ENV FIRST — BEFORE ANY BACKEND IMPORT
load_dotenv(dotenv_path="backend/.env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import create_tables, engine
from error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from logging_config import setup_logging
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from contextlib import asynccontextmanager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app
    Handles startup and shutdown events
    """
    # Startup: Initialize database and MCP server
    logger.info("Starting up Todo Backend API...")
    create_tables()

    # Configure MCP server with database engine
    from app.mcp.server import set_engine
    set_engine(engine)
    logger.info("MCP server configured with database engine")

    logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down Todo Backend API...")


app = FastAPI(
    title="Todo Backend API",
    version="1.0.0",
    description="Secure Todo Backend API with JWT authentication and user isolation",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anooshaqasim-phase3-chatbit-backend.hf.space",
    "https://phase3-todo-chatbot.vercel.app"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Todo Backend API is running!",
        "version": "1.0.0",
        "documentation": "/docs for API documentation"
    }

# Include routes
from routes import tasks, auth, chat, conversations
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])