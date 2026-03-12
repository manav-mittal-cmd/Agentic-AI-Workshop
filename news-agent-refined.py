"""
Agent: News Digest

Goal: Showcase Data Flow with LangGraph + LangSmith + Ollama

Tech Stack:
  - feedparser + httpx — RSS fetching (pure Python, no model needed)
  - Ollama (mistral:7b) — ranking + summaries
  - LangGraph — explicit node-by-node data flow
  - LangSmith — full trace observability

Graph:
  load_sources → fetch_feeds → fetch_articles → rank → summarize → save
                                     ↓ (if < 5 items)
                                    END

Before running:
  1. Install Ollama → https://ollama.com
  2. Run: ollama pull llama3.2:3b
  3. Create .env file and add your LangSmith key
  4. uv run python news-agent.py
"""

import operator
from datetime import datetime
from pathlib import Path
from typing import Annotated, TypedDict

import feedparser
import httpx
import trafilatura
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

load_dotenv()

# llm = ChatOllama(model="llama3.2:3b")
llm = ChatOllama(model="mistral:7b", num_ctx=32768)


# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    sources:   list[str]                      # RSS URLs from sources.txt
    raw_items: list[dict]                     # headlines + metadata from feeds
    ranked:    list[dict]                     # top 10 selected by model
    digest:    list[dict]                     # ranked + model summaries
    failed:    list[str]                      # feeds/articles that errored
    messages:  Annotated[list, operator.add]  # accumulates for LangSmith


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_sources(path="sources.txt") -> list[str]:
    return [l.strip() for l in Path(path).read_text().splitlines()
            if l.strip() and not l.startswith("#")]


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

def load_sources_node(state: AgentState) -> dict:
    sources = load_sources()
    print(f"\n[load_sources] {len(sources)} feeds")
    return {"sources": sources,
            "messages": [{"role": "system", "content": f"Loaded {len(sources)} sources"}]}


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
    return {"raw_items": all_items, "failed": failed,
            "messages": [{"role": "tool", "content": f"{len(all_items)} headlines fetched"}]}


def fetch_articles_node(state: AgentState) -> dict:
    """Visit each article URL and extract the full text. Gives the model real content."""
    print(f"\n[fetch_articles] Fetching {len(state['raw_items'])} articles...")
    enriched = []
    for item in state["raw_items"]:
        content = fetch_article(item["url"])
        status = f"{len(content)} chars" if content else "failed"
        print(f"  {'✓' if content else '✗'} {item['title'][:50]}... ({status})")
        enriched.append({**item, "content": content})
    return {"raw_items": enriched,
            "messages": [{"role": "tool", "content": "Articles fetched"}]}


RANK_PROMPT = """You are a senior tech editor curating a daily digest for software engineers and AI researchers.

Your audience writes code, builds systems, and follows AI/ML developments closely.
They have zero interest in consumer deals, health news, or anything outside the tech industry.

SELECT articles about:
- AI/ML model releases, benchmarks, research breakthroughs
- Developer tools, APIs, or frameworks with new capabilities
- Security vulnerabilities or patches affecting widely-used software
- Significant open-source releases or major version updates
- Cloud, infrastructure, or hardware shifts with real technical impact
- Standards, protocols, or policy changes that affect how software is built

REJECT articles that are:
- Consumer deals, coupons, discounts, or product sales
- Health, science, politics, or any non-tech news
- Job postings or hiring announcements
- Podcast, video, or newsletter announcements
- Opinion or commentary with no new factual information
- Conference announcements without substantive technical content
- Listicles or roundups ("best of", "top 10 tools")
- Funding rounds unless the technical implications are clearly explained
- Duplicate coverage of the same event (keep only the most informative)

Articles:
{articles}

Return ONLY a comma-separated list of up to 10 numbers. No explanation. No preamble. Example: 3, 7, 11, 14, 18"""


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
    return {"ranked": ranked,
            "messages": [{"role": "assistant", "content": f"Ranked: {raw}"}]}


SUMMARIZE_PROMPT = """You are a senior tech editor writing for an audience of software engineers and AI researchers.

Write a substantive summary of the following article. Your summary should:
1. Open with what specifically happened or was announced (be concrete and factual)
2. Explain the technical substance — what changed, what was built, what was discovered
3. Describe why this matters to developers or researchers — practical implications, not hype
4. Note any important caveats, limitations, open questions, or context the reader should know
5. If relevant, mention what to watch for next

Write 4-6 sentences. Be direct and specific. Avoid filler phrases like "in conclusion" or "it's worth noting".
Do not editorialize or inflate the significance. If the content is thin, say so plainly.

Title: {title}
Source: {source}
Content:
{content}

Summary:"""


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
    return {"digest": digest,
            "messages": [{"role": "assistant", "content": f"Summarized {len(digest)} items"}]}


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
    return {"messages": [{"role": "system", "content": f"Saved {filename}"}]}


# ── Conditional ───────────────────────────────────────────────────────────────

def enough_items(state: AgentState) -> str:
    if len(state["raw_items"]) >= 5:
        return "rank"
    print("[router] Too few items — ending early")
    return "end"


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph():
    wf = StateGraph(AgentState)
    for name, fn in [
        ("load_sources",   load_sources_node),
        ("fetch_feeds",    fetch_feeds_node),
        ("fetch_articles", fetch_articles_node),
        ("rank",           rank_node),
        ("summarize",      summarize_node),
        ("save",           save_node),
    ]:
        wf.add_node(name, fn)

    wf.set_entry_point("load_sources")
    wf.add_edge("load_sources", "fetch_feeds")
    wf.add_conditional_edges("fetch_feeds", enough_items,
                             {"rank": "fetch_articles", "end": END})
    wf.add_edge("fetch_articles", "rank")
    wf.add_edge("rank", "summarize")
    wf.add_edge("summarize", "save")
    wf.add_edge("save", END)
    return wf.compile()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*50}\n  Tech & AI Digest | LangGraph + llama3.2:3b\n{'='*50}")
    result = build_graph().invoke({
        "sources": [], "raw_items": [], "ranked": [],
        "digest": [], "failed": [], "messages": [],
    })
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*50}")
    print(f"  ✓ digest_{date_str}.md — {len(result['digest'])} headlines")
    print(f"  Trace → https://smith.langchain.com")
    print(f"{'='*50}\n")