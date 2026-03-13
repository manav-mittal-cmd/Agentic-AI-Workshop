"""
Agent: News Digest

Goal: Showcase Data Flow with LangGraph + LangSmith + Ollama

Tech Stack:
  - feedparser + httpx — RSS fetching (pure Python, no model needed)
  - Ollama (mistral:7b) — ranking + summaries
  - LangGraph — explicit node-by-node data flow
  - LangSmith — full trace observability

LLM: 
  - If RAM = 8 gb --> llama3.2:3b
  - If RAM > 8 gb --> mistral:7b

Graph:
  load_sources → fetch_feeds → fetch_articles → rank → summarize → save
                                     ↓ (if < 5 items)
                                    END

Before running:
  1. Install Ollama → https://ollama.com
  2. Run: ollama pull llama3.2:3b
  3. Create .env file and add your LangSmith key (OPTIONAL)
  4. uv run python news-agent.py
"""

from datetime import datetime
from pathlib import Path
from typing import TypedDict

import feedparser
import httpx
import trafilatura
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

# import prompts
from agent_prompts import RANK_PROMPT, SUMMARIZE_PROMPT

load_dotenv()

# llm = ChatOllama(model="llama3.2:3b")
llm = ChatOllama(model="mistral:7b", num_ctx=32768) # 8 * 4096 (max token count)

# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    sources:   list[str]                      # RSS URLs from sources.txt
    raw_items: list[dict]                     # headlines + metadata from feeds
    ranked:    list[dict]                     # top 10 selected by model
    digest:    list[dict]                     # ranked + model summaries
    failed:    list[str]                      # feeds/articles that errored


# ── Helpers ───────────────────────────────────────────────────────────────────

# get sources from file
def load_sources(path="sources.txt") -> list[str]:
    return [l.strip() for l in Path(path).read_text().splitlines()
            if l.strip() and not l.startswith("#")]

# get feed from a given url
def fetch_feed(url: str, max_items=5) -> tuple[list[dict], str | None]:
    try:
        r = httpx.get(url, headers={"User-Agent": "digest-bot/1.0"},
                      timeout=8, follow_redirects=True)
        feed = feedparser.parse(r.text)
        if not feed.entries:
            return [], "No entries"
        source = feed.feed.get("title", url.split("/")[2])
        return [
            {"title": e.get("title", "").strip(), "url": e.get("link", ""),
             "source": source, "content": "", "summary": ""}
            for e in feed.entries[:max_items]
        ], None
    except Exception as e:
        return [], str(e)

# get a specific article from news site
def fetch_article(url: str) -> str:
    """Fetch a URL and extract the main article text using trafilatura."""
    try:
        r = httpx.get(url, headers={"User-Agent": "digest-bot/1.0"},
                      timeout=10, follow_redirects=True)
        text = trafilatura.extract(r.text, include_comments=False,
                                   include_tables=False, no_fallback=False)
        # Truncate — model only needs the gist, not the full article
        return (text or "")[:10000]
    except Exception:
        return ""


# ── Nodes ─────────────────────────────────────────────────────────────────────

# 1st node --> provide a the agent a starting point
def load_sources_node(state: AgentState) -> dict:
    sources = load_sources()
    print(f"\n[load_sources] {len(sources)} feeds")
    return {"sources": sources}


# 2nd node --> provide the agent ability to search the web
def fetch_feeds_node(state: AgentState) -> dict:
    all_items, failed = [], []
    for url in state["sources"]:
        items, err = fetch_feed(url)
        if err:
            print(f"  ✗ {url.split('/')[2]} — {err}")
            failed.append(url)
        else:
            print(f"  ✓ {url.split('/')[2]} — {len(items)} items")
            all_items.extend(items)
    print(f"\n[fetch_feeds] {len(all_items)} total headlines")
    return {"raw_items": all_items, "failed": failed}

# 3rd node --> provide agent ability to read articles
def fetch_articles_node(state: AgentState) -> dict:
    """Visit each article URL and extract the full text. Gives the model real content."""
    print(f"\n[fetch_articles] Fetching {len(state['raw_items'])} articles...")
    enriched = []
    for item in state["raw_items"]:
        content = fetch_article(item["url"])
        status = f"{len(content)} chars" if content else "failed"
        print(f"  {'✓' if content else '✗'} {item['title'][:50]}... ({status})")
        enriched.append({**item, "content": content})
    return {"raw_items": enriched}


# 4th node --> return a list of articles that are relevant
def rank_node(state: AgentState) -> dict:
    """Model ranks by reading actual article content, not just titles."""
    print(f"\n[rank_node] Ranking {len(state['raw_items'])} articles...")

    numbered = "\n\n".join(
        f"{i+1}. {item['title']} [{item['source']}]\n"
        f"{item['content'][:800] or '(no content)'}"
        for i, item in enumerate(state["raw_items"])
    )
    
    response = llm.invoke(RANK_PROMPT.format(articles=numbered))
    raw = response.content.strip()
    print(f"[rank_node] Model chose: {raw}")

    indices = []
    for token in raw.replace(",", " ").split():
        try:
            idx = int(token.strip(".")) - 1
            if 0 <= idx < len(state["raw_items"]):
                indices.append(idx)
        except ValueError:
            continue

    if not indices:
        print("[rank_node] Unparseable — falling back to first 10")
        indices = list(range(min(10, len(state["raw_items"]))))

    ranked = [state["raw_items"][i] for i in indices[:10]]
    print(f"[rank_node] Kept {len(ranked)} articles")
    return {"ranked": ranked}


# 5th node --> summarize articles 
def summarize_node(state: AgentState) -> dict:
    """Summarize each article using its full content — not just the title."""
    print(f"\n[summarize_node] Summarizing {len(state['ranked'])} articles...")
    digest = []
    for item in state["ranked"]:
        prompt = SUMMARIZE_PROMPT.format(
            title=item["title"],
            source=item["source"],
            content=item["content"][:1500] or "Full article content was not retrievable.",
        )
        response = llm.invoke(prompt)
        digest.append({**item, "summary": response.content.strip()})
        print(f"  • {item['title'][:60]}...")
    return {"digest": digest}


# 6th node (final node) --> save the digest as a markdown file
def save_node(state: AgentState) -> dict:
    date = datetime.now()
    filename = f"digest_{date.strftime('%Y-%m-%d')}.md"
    lines = [
        f"# 🗞️ Tech & AI News Digest",
        f"*{date.strftime('%B %d, %Y')} — {len(state['digest'])} stories*\n",
        "---\n",
    ]
    for i, item in enumerate(state["digest"], 1):
        lines += [f"### {i}. [{item['title']}]({item['url']})",
                  f"*{item['source']}*\n",
                  item["summary"], "\n---\n"]
    if state["failed"]:
        lines += ["### ⚠️ Failed sources"] + [f"- {u}" for u in state["failed"]]
    Path(filename).write_text("\n".join(lines))
    print(f"\n[save_node] Saved → {filename}")
    return {}


# ── Conditional ───────────────────────────────────────────────────────────────

def enough_items(state: AgentState) -> str:
    if len(state["raw_items"]) >= 5:
        return "rank"
    print("[router] Too few items — ending early")
    return "end"


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("load_sources",   load_sources_node)
    workflow.add_node("fetch_feeds",    fetch_feeds_node)
    workflow.add_node("fetch_articles", fetch_articles_node)
    workflow.add_node("rank",           rank_node)    
    workflow.add_node("summarize",      summarize_node)
    workflow.add_node("save",           save_node)


    workflow.set_entry_point("load_sources")
    workflow.add_edge("load_sources", "fetch_feeds")
    
    workflow.add_conditional_edges(
        "fetch_feeds",
        enough_items,
        {
            "rank": "fetch_articles",       # true
            "end": END,                     # false
        },
    )

    workflow.add_edge("fetch_articles", "rank")
    workflow.add_edge("rank", "summarize")
    workflow.add_edge("summarize", "save")
    workflow.add_edge("save", END)
    
    return workflow.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*50}\n  Tech & AI Digest | LangGraph + llama3.2:3b\n{'='*50}")
    result = build_graph().invoke({
        "sources": [], "raw_items": [], "ranked": [],
        "digest": [], "failed": [],
    })
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*50}")
    print(f"  ✓ digest_{date_str}.md — {len(result['digest'])} headlines")
    print(f"  Trace → https://smith.langchain.com")
    print(f"{'='*50}\n")