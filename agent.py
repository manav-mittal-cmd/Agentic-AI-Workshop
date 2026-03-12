"""
Part 1
Agentic AI Workshop: Data Flow with LangGraph + LangSmith + Ollama

Stack:
  - Ollama (llama3.2:3b) — local, no API key required
  - DuckDuckGo — free web search, no API key required
  - LangGraph  — explicit workflow orchestration
  - LangSmith  — observability dashboard

Before running:
  1. Install Ollama → https://ollama.com
  2. Run: ollama pull llama3.2:3b
  3. Copy .env.example to .env and add your LangSmith key
  4. uv run python part1/complete/agent.py
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
# This is the entire data pipeline written as a typed dict.
# Every node reads from here. Every node writes back here.
# Nothing else is passed between steps.

class AgentState(TypedDict):
    topic: str                              # input — the research topic
    search_results: str                     # populated by search_node
    summary: str                            # populated by summarize_node
    retry_count: int                        # tracks how many times we retried
    messages: Annotated[list, operator.add] # accumulates — never overwrites


# ── Layer 2: Model + Tools ────────────────────────────────────────────────────
# Weak local model — needs all the scaffolding we're about to build.

llm = ChatOllama(model="llama3.2:3b")
search = DuckDuckGoSearchRun()


# ── Layer 3: Nodes ────────────────────────────────────────────────────────────
# Each node does exactly ONE thing.
# Input: full state. Output: only the keys it changed.

def search_node(state: AgentState) -> dict:
    """Search the web for the topic."""
    print(f"\n[search_node] Searching for: {state['topic']}")
    results = search.run(state["topic"])
    print(f"[search_node] Got {len(results)} characters of results")
    return {
        "search_results": results,
        "messages": [{"role": "tool", "content": f"Search results: {results[:200]}..."}],
    }


def summarize_node(state: AgentState) -> dict:
    """Ask the LLM to summarize search results into 5 bullet points."""
    print(f"\n[summarize_node] Summarizing results...")
    prompt = (
        f"You are a research assistant. Summarize the following search results "
        f"about '{state['topic']}' into exactly 5 clear bullet points.\n\n"
        f"Search results:\n{state['search_results']}\n\n"
        f"Respond with only the 5 bullet points, nothing else."
    )
    response = llm.invoke(prompt)
    print(f"[summarize_node] Summary generated")
    return {
        "summary": response.content,
        "messages": [{"role": "assistant", "content": response.content}],
    }


def save_node(state: AgentState) -> dict:
    """Save the summary to a file."""
    filename = f"brief_{state['topic'].replace(' ', '_')[:30]}.txt"
    print(f"\n[save_node] Saving to {filename}")
    with open(filename, "w") as f:
        f.write(f"Topic: {state['topic']}\n")
        f.write("=" * 40 + "\n\n")
        f.write(state["summary"])
    print(f"[save_node] Saved successfully")
    return {}


# ── Layer 4: Conditional Logic ────────────────────────────────────────────────
# This is where "pipeline" becomes "agent."
# The graph can loop — it reacts to what it finds.

def should_retry(state: AgentState) -> str:
    """
    If search results are too thin, retry search (up to 2 times).
    Otherwise proceed to summarize.
    """
    retry_count = state.get("retry_count", 0)
    results_too_short = len(state.get("search_results", "")) < 200

    if results_too_short and retry_count < 2:
        print(f"\n[router] Results too thin (retry {retry_count + 1}/2) — searching again")
        state["retry_count"] = retry_count + 1
        return "search"

    print(f"\n[router] Results sufficient — proceeding to summarize")
    return "summarize"


# ── Layer 5: Graph ────────────────────────────────────────────────────────────
# The code IS the diagram. Each add_edge is an arrow on the whiteboard.

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("search", search_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("save", save_node)

    # Define flow
    workflow.set_entry_point("search")
    workflow.add_conditional_edges(
        "search",
        should_retry,
        {
            "search": "search",       # loop back if results too thin
            "summarize": "summarize", # proceed if results are good
        },
    )
    workflow.add_edge("summarize", "save")
    workflow.add_edge("save", END)

    return workflow.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    graph = build_graph()

    topic = "agentic AI developments 2026"
    print(f"\n{'='*50}")
    print(f"Starting agent for topic: '{topic}'")
    print(f"{'='*50}")

    initial_state = {
        "topic": topic,
        "search_results": "",
        "summary": "",
        "retry_count": 0,
        "messages": [],
    }

    result = graph.invoke(initial_state)

    print(f"\n{'='*50}")
    print("FINAL SUMMARY:")
    print(f"{'='*50}")
    print(result["summary"])
    print(f"\nFull message history: {len(result['messages'])} messages")
    print("Check LangSmith dashboard for the full trace →  https://smith.langchain.com")
