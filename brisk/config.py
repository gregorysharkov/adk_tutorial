"""
Configuration settings for the Multi-Agent ADK Application
"""

import os

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = "gemini-1.5-flash"
AVAILABLE_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

# Streamlit Configuration
PAGE_TITLE = "Multi-Agent ADK App"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# Agent Configuration
MAX_AGENTS = 10
DEFAULT_AGENT_ROLES = [
    "Research Agent - Expert in market analysis and competitive intelligence",
    "Data Analyst - Specialized in statistical analysis and data visualization",
    "Content Writer - Professional content creation and copywriting",
    "Technical Expert - Software development and technical documentation",
    "Business Analyst - Strategic planning and business process optimization",
]

# UI Configuration
COLUMN_RATIOS = [1, 2, 1]  # Left, Middle, Right column widths
REPORT_HEIGHT = 400  # Height of report text area in pixels

# Task Configuration
MAX_TASK_LENGTH = 1000  # Maximum characters for task description
MAX_CONTEXT_LENGTH = 2000  # Maximum characters for context

# Threading Configuration
MAX_CONCURRENT_TASKS = 5  # Maximum number of concurrent agent tasks
TASK_TIMEOUT = 300  # Timeout for agent tasks in seconds
