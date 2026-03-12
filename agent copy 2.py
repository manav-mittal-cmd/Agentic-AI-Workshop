"""
Part 2 — Complete Version
Agentic AI Workshop: Claude Haiku + Native Tool Use + Skills

Stack:
  - Claude Haiku (claude-haiku-4-5) — cheap, fast, capable
  - Native web search — built into the Anthropic API, no extra key
  - Custom skills — summarize.py and save_report.py

Key contrast with Part 1:
  - No StateGraph. Claude manages the data flow via its context window.
  - No conditional logic. Claude decides when to retry.
  - No orchestration framework. The model IS the orchestrator.
  - Web search is native — we didn't write search_node.

Before running:
  1. Copy .env.example to .env and add your ANTHROPIC_API_KEY
  2. uv run python part2/complete/agent.py
"""

import json
import os

import anthropic
from dotenv import load_dotenv

from skills.summarize import summarize
from skills.save_report import save_report

load_dotenv()

# ── Model ─────────────────────────────────────────────────────────────────────

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"


# ── Tool Definitions ──────────────────────────────────────────────────────────
# Claude reads these descriptions to decide when and how to call each tool.
# The descriptions are the "prompt" for tool use — write them carefully.

tools = [
    # Native web search — no implementation needed, Claude handles it
    {
        "type": "web_search_20250305",
        "name": "web_search",
    },
    # Custom skill — summarize
    {
        "name": "summarize",
        "description": (
            "Summarize a body of raw text into 5 clear bullet points. "
            "Use this after retrieving search results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text":  {"type": "string", "description": "Raw text to summarize"},
                "topic": {"type": "string", "description": "The research topic"},
            },
            "required": ["text", "topic"],
        },
    },
    # Custom skill — save_report
    {
        "name": "save_report",
        "description": "Save the final summary to a text file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The summary to save"},
                "topic":   {"type": "string", "description": "Used for the filename"},
            },
            "required": ["content", "topic"],
        },
    },
]


# ── Tool Dispatcher ───────────────────────────────────────────────────────────
# Routes Claude's tool calls to the actual Python functions.
# This is the only "orchestration" code we write — everything else is Claude.

def dispatch_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "summarize":
        return summarize(**tool_input)
    elif tool_name == "save_report":
        return save_report(**tool_input)
    return f"Unknown tool: {tool_name}"


# ── Agent Loop ────────────────────────────────────────────────────────────────
# The agentic loop:
#   1. Send messages + tools to Claude
#   2. Claude responds with text and/or tool calls
#   3. Execute tool calls, append results to message history
#   4. Repeat until Claude stops calling tools

def run_agent(topic: str) -> str:
    print(f"\n{'='*50}")
    print(f"Starting agent for topic: '{topic}'")
    print(f"{'='*50}\n")

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

    # The agentic loop
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            tools=tools,
            messages=messages,
        )

        print(f"[agent] stop_reason: {response.stop_reason}")

        # Append Claude's response to history (this is the "context window pipeline")
        messages.append({"role": "assistant", "content": response.content})

        # If Claude is done, break
        if response.stop_reason == "end_turn":
            break

        # If Claude wants to use tools, execute them and feed results back
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"[tool_use] {block.name}({json.dumps(block.input)[:80]}...)")
                    result = dispatch_tool(block.name, block.input)
                    print(f"[tool_result] {str(result)[:80]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            # Append tool results — Claude reads these on the next iteration
            messages.append({"role": "user", "content": tool_results})

    # Extract final text response
    final_text = next(
        (block.text for block in response.content if hasattr(block, "text")),
        "No summary generated."
    )

    print(f"\n{'='*50}")
    print("FINAL RESPONSE:")
    print(f"{'='*50}")
    print(final_text)
    print(f"\nTotal turns: {len([m for m in messages if m['role'] == 'assistant'])}")

    return final_text


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_agent("agentic AI developments 2025")
