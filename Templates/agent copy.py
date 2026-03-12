"""
Part 1 — Live Demo Version
Agentic AI Workshop: Data Flow with LangGraph + LangSmith + Ollama

This file is intentionally incomplete — it's for the presenter to fill in live.
Each TODO corresponds to a "layer" in the workshop explanation.

Before running:
  1. Install Ollama → https://ollama.com
  2. Run: ollama pull llama3.2:3b
  3. Copy .env.example to .env and add your LangSmith key
  4. uv run python part1/live/agent.py
"""

import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

load_dotenv()


# ── Layer 1: State ────────────────────────────────────────────────────────────
# TODO: Define AgentState as a TypedDict
# Fields needed:
#   - topic: str
#   - search_results: str
#   - summary: str
#   - retry_count: int
#   - messages: list that accumulates (hint: Annotated + operator.add)

class AgentState(TypedDict):
    pass  # TODO


# ── Layer 2: Model + Tools ────────────────────────────────────────────────────
# TODO: Initialize the local Ollama model (llama3.2:3b)
# TODO: Initialize DuckDuckGoSearchRun

llm = None   # TODO
search = None  # TODO


# ── Layer 3: Nodes ────────────────────────────────────────────────────────────

def search_node(state: AgentState) -> dict:
    # TODO: Use search.run() with state["topic"]
    # Return dict with "search_results" and a "messages" entry
    pass


def summarize_node(state: AgentState) -> dict:
    # TODO: Build a prompt, call llm.invoke(), return "summary"
    # Prompt should ask for 5 bullet points about state["topic"]
    pass


def save_node(state: AgentState) -> dict:
    # TODO: Write state["summary"] to a .txt file
    # Return empty dict (nothing new to add to state)
    pass


# ── Layer 4: Conditional Logic ────────────────────────────────────────────────

def should_retry(state: AgentState) -> str:
    # TODO: If search_results < 200 chars AND retry_count < 2, return "search"
    # Otherwise return "summarize"
    pass


# ── Layer 5: Graph ────────────────────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(AgentState)

    # TODO: Add nodes — search, summarize, save
    # TODO: Set entry point
    # TODO: Add conditional edges from search using should_retry
    # TODO: Add edges: summarize → save → END

    return workflow.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    graph = build_graph()

    initial_state = {
        "topic": "agentic AI developments 2025",
        "search_results": "",
        "summary": "",
        "retry_count": 0,
        "messages": [],
    }

    result = graph.invoke(initial_state)
    print(result["summary"])
