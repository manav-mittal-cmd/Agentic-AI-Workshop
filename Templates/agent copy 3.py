"""
Part 2 — Live Demo Version
Agentic AI Workshop: Claude Haiku + Native Tool Use + Skills

This file is intentionally incomplete — for the presenter to fill in live.

Before running:
  1. Copy .env.example to .env and add your ANTHROPIC_API_KEY
  2. uv run python part2/live/agent.py
"""

import json
import os

import anthropic
from dotenv import load_dotenv

from skills.summarize import summarize
from skills.save_report import save_report

load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"


# ── Tool Definitions ──────────────────────────────────────────────────────────
# TODO: Define the tools list with 3 entries:
#   1. Native web search (type: "web_search_20250305")
#   2. summarize — describe what it does and its input schema
#   3. save_report — describe what it does and its input schema

tools = []  # TODO


# ── Tool Dispatcher ───────────────────────────────────────────────────────────

def dispatch_tool(tool_name: str, tool_input: dict) -> str:
    # TODO: Route tool_name to the correct skill function
    pass


# ── Agent Loop ────────────────────────────────────────────────────────────────

def run_agent(topic: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"Research the topic '{topic}'. "
                f"Search the web for recent developments, summarize the findings "
                f"into 5 bullet points, and save the report to a file. "
                f"Then tell me the summary."
            ),
        }
    ]

    # TODO: Implement the agentic loop
    # Hint: loop until response.stop_reason == "end_turn"
    # On each iteration:
    #   1. Call client.messages.create()
    #   2. Append response to messages
    #   3. If stop_reason == "tool_use", dispatch tools and append results
    #   4. If stop_reason == "end_turn", break

    pass


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_agent("agentic AI developments 2025")
