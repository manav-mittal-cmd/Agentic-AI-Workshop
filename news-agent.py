"""
Part 1 — Complete Version: News Digest
Agentic AI Workshop: Data Flow with LangGraph + LangSmith + Ollama

Stack:
  - feedparser + httpx — RSS fetching (pure Python, no model needed)
  - Ollama (llama3.2:3b) — ranking + one-line summaries only
  - LangGraph — explicit node-by-node data flow
  - LangSmith — full trace observability

Key design decision:
  The model NEVER generates URLs. It only reads and ranks real ones.
  All structure comes from Python. This makes llama3.2:3b viable.

Graph:
  fetch_feeds → [enough feeds?] → rank → summarize → save
                      ↓ no
                  [end with error]

Before running:
  1. Install Ollama → https://ollama.com
  2. Run: ollama pull llama3.2:3b
  3. Copy .env.example to .env and add your LangSmith key
  4. uv run python part1/complete/agent.py
"""

import operator
from datetime import datetime
from pathlib import Path
from typing import Annotated, TypedDict

import feedparser
import httpx
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

load_dotenv()


# ── Layer 1: State ────────────────────────────────────────────────────────────
# The entire data pipeline as a typed dict.
# raw_items  — every headline pulled from every RSS feed (list of dicts)
# ranked     — top 10-15 after the model ranks them (list of dicts)
# digest     — final list with model-written summaries attached (list of dicts)
# failed     — sources that could not be fetched
# messages   — accumulates across all nodes for LangSmith visibility

class AgentState(TypedDict):
    sources: list[str]                      # loaded from sources.txt
    raw_items: list[dict]                   # all RSS items fetched
    ranked: list[dict]                      # top 10-15 after ranking
    digest: list[dict]                      # ranked + one-line summaries
    failed: list[str]                       # feeds that errored
    messages: Annotated[list, operator.add] # accumulates, never overwrites


# ── Layer 2: Model ────────────────────────────────────────────────────────────
# Model is only used for ranking and summarizing — never for generating URLs.

llm = ChatOllama(model="llama3.2:3b")


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_sources(path: str = "sources.txt") -> list[str]:
    """Read RSS URLs from config file, skip comments and blank lines."""
    lines = Path(path).read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def fetch_feed(url: str, max_items: int = 5) -> tuple[list[dict], str | None]:
    """
    Fetch and parse a single RSS feed.
    Returns (items, error_message). Items are dicts with title, url, source, published.
    """
    try:
        # Use httpx to fetch with a timeout and a browser-like User-Agent
        headers = {"User-Agent": "Mozilla/5.0 (compatible; digest-bot/1.0)"}
        response = httpx.get(url, headers=headers, timeout=8, follow_redirects=True)
        feed = feedparser.parse(response.text)

        if not feed.entries:
            return [], f"No entries found in feed: {url}"

        source_name = feed.feed.get("title", url.split("/")[2])
        items = []

        for entry in feed.entries[:max_items]:
            items.append({
                "title":     entry.get("title", "No title").strip(),
                "url":       entry.get("link", ""),
                "source":    source_name,
                "published": entry.get("published", ""),
                "summary":   "",  # filled in later by summarize_node
            })

        return items, None

    except Exception as e:
        return [], str(e)


# ── Layer 3: Nodes ────────────────────────────────────────────────────────────
# Each node does ONE thing. Input: full state. Output: only changed keys.

def load_sources_node(state: AgentState) -> dict:
    """Read sources.txt and populate state['sources']."""
    sources = load_sources("sources.txt")
    print(f"\n[load_sources] Loaded {len(sources)} RSS feeds from sources.txt")
    return {
        "sources": sources,
        "messages": [{"role": "system", "content": f"Loaded {len(sources)} sources"}],
    }


def fetch_feeds_node(state: AgentState) -> dict:
    """
    Fetch all RSS feeds in parallel-ish (sequential for simplicity).
    Collects all items into raw_items. Tracks failures.
    Model is not involved here — this is pure Python data extraction.
    """
    all_items: list[dict] = []
    failed: list[str] = []

    for url in state["sources"]:
        domain = url.split("/")[2]
        items, error = fetch_feed(url)
        if error:
            print(f"  ✗ {domain} — {error}")
            failed.append(url)
        else:
            print(f"  ✓ {domain} — {len(items)} items")
            all_items.extend(items)

    print(f"\n[fetch_feeds] {len(all_items)} total items from {len(state['sources']) - len(failed)} sources")
    return {
        "raw_items": all_items,
        "failed": failed,
        "messages": [{"role": "tool", "content": f"Fetched {len(all_items)} items, {len(failed)} failures"}],
    }


def rank_node(state: AgentState) -> dict:
    """
    Ask the LLM to pick the top 10 most significant headlines.
    Model returns a list of numbers — we use those to index into raw_items.
    The model NEVER generates a URL. It only picks indices.
    """
    print(f"\n[rank_node] Asking model to rank {len(state['raw_items'])} headlines...")

    # Build a numbered list of titles for the model to rank
    numbered = "\n".join(
        f"{i+1}. [{item['source']}] {item['title']}"
        for i, item in enumerate(state["raw_items"])
    )

    prompt = (
        f"You are a tech news editor. Below is a numbered list of headlines from today.\n\n"
        f"{numbered}\n\n"
        f"Pick the 10 most significant stories for a tech/AI-focused audience. "
        f"Prioritize: AI/ML breakthroughs, major product launches, important research, industry shifts.\n\n"
        f"Respond with ONLY a comma-separated list of the numbers you selected. "
        f"Example: 2, 5, 7, 11, 14, 18, 21, 25, 28, 30\n"
        f"Nothing else."
    )

    response = llm.invoke(prompt)
    raw = response.content.strip()
    print(f"[rank_node] Model selected: {raw}")

    # Parse the indices safely — any non-number is ignored
    indices = []
    for token in raw.replace(",", " ").split():
        try:
            idx = int(token.strip(".")) - 1  # convert 1-based to 0-based
            if 0 <= idx < len(state["raw_items"]):
                indices.append(idx)
        except ValueError:
            continue

    # Fallback: if model output was unparseable, take first 10
    if not indices:
        print("[rank_node] Could not parse model output — falling back to first 10")
        indices = list(range(min(10, len(state["raw_items"]))))

    ranked = [state["raw_items"][i] for i in indices[:10]]
    print(f"[rank_node] Kept {len(ranked)} headlines")

    return {
        "ranked": ranked,
        "messages": [{"role": "assistant", "content": f"Ranked indices: {raw}"}],
    }


def summarize_node(state: AgentState) -> dict:
    """
    For each ranked headline, ask the model for one sentence on why it matters.
    Attaches the summary back to each item dict.
    """
    print(f"\n[summarize_node] Writing summaries for {len(state['ranked'])} headlines...")
    digest = []

    for item in state["ranked"]:
        prompt = (
            f"In one sentence, explain why this tech/AI headline matters to a developer:\n"
            f"'{item['title']}' — from {item['source']}\n\n"
            f"One sentence only. No preamble."
        )
        response = llm.invoke(prompt)
        enriched = {**item, "summary": response.content.strip()}
        digest.append(enriched)
        print(f"  • {item['title'][:60]}...")

    return {
        "digest": digest,
        "messages": [{"role": "assistant", "content": f"Summarized {len(digest)} items"}],
    }


def save_node(state: AgentState) -> dict:
    """Write the final digest to a markdown file with clickable links."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_display = datetime.now().strftime("%B %d, %Y")
    filename = f"digest_{date_str}.md"

    print(f"\n[save_node] Writing {filename}...")

    lines = [
        f"# 🗞️ Tech & AI News Digest",
        f"*{date_display} — {len(state['digest'])} stories from {len(state['sources'])} sources*",
        "",
        "---",
        "",
    ]

    for i, item in enumerate(state["digest"], 1):
        lines.append(f"### {i}. [{item['title']}]({item['url']})")
        lines.append(f"*{item['source']}*")
        lines.append("")
        lines.append(item["summary"])
        lines.append("")
        lines.append("---")
        lines.append("")

    if state["failed"]:
        lines.append("### ⚠️ Sources that failed to load")
        for url in state["failed"]:
            lines.append(f"- {url}")
        lines.append("")

    lines.append(f"*Generated by Agentic AI Workshop — Part 1 (LangGraph + llama3.2:3b)*")

    Path(filename).write_text("\n".join(lines))
    print(f"[save_node] Saved to {filename}")

    return {
        "messages": [{"role": "system", "content": f"Digest saved to {filename}"}],
    }


# ── Layer 4: Conditional Logic ────────────────────────────────────────────────

def enough_feeds(state: AgentState) -> str:
    """
    Only proceed to ranking if we got at least 5 items.
    Fewer than 5 likely means most feeds failed — not worth ranking.
    """
    if len(state["raw_items"]) >= 5:
        return "rank"
    print("\n[router] Too few items fetched — ending early")
    return "end"


# ── Layer 5: Graph ────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("load_sources", load_sources_node)
    workflow.add_node("fetch_feeds", fetch_feeds_node)
    workflow.add_node("rank", rank_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("save", save_node)

    workflow.set_entry_point("load_sources")
    workflow.add_edge("load_sources", "fetch_feeds")
    workflow.add_conditional_edges(
        "fetch_feeds",
        enough_feeds,
        {
            "rank": "rank",
            "end": END,
        },
    )
    workflow.add_edge("rank", "summarize")
    workflow.add_edge("summarize", "save")
    workflow.add_edge("save", END)

    return workflow.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    graph = build_graph()

    print(f"\n{'='*55}")
    print(f"  Tech & AI News Digest — Part 1")
    print(f"  LangGraph + LangSmith + llama3.2:3b")
    print(f"{'='*55}")

    initial_state: AgentState = {
        "sources": [],
        "raw_items": [],
        "ranked": [],
        "digest": [],
        "failed": [],
        "messages": [],
    }

    result = graph.invoke(initial_state)

    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*55}")
    print(f"  Done! Open digest_{date_str}.md")
    print(f"  {len(result['digest'])} headlines | {len(result['failed'])} failed feeds")
    print(f"  Full trace → https://smith.langchain.com")
    print(f"{'='*55}\n")