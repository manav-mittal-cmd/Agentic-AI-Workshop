# Agentic AI Workshop

> CS Club Workshop — *From Data Flow to High-Level Abstraction*

A two-part workshop that builds intuition for agentic AI from the ground up.
Part 1 makes data flow explicit using LangGraph + a local model.
Part 2 shows how a capable model (Claude) internalizes that same flow.

---

## The Thesis

```
Part 1:  You define the graph  →  the model fills in the steps
Part 2:  You define the tools  →  the model defines the graph
```

Same task. Same output. Radically different amounts of scaffolding.

---

## Setup

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.11+ | Runtime | [python.org](https://python.org) |
| uv | Package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Ollama | Local LLM (Part 1) | [ollama.com](https://ollama.com) |
| LangSmith account | Observability (Part 1) | [smith.langchain.com](https://smith.langchain.com) |
| Anthropic API key | Claude (Part 2) | [console.anthropic.com](https://console.anthropic.com) |

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd agentic-ai-workshop

# Install dependencies
uv sync

# Pull the local model for Part 1
ollama pull llama3.2:3b

# Set up environment variables
cp .env.example .env
# Edit .env and add your LangSmith and Anthropic keys
```

---

## Repository Structure

```
agentic-ai-workshop/
├── pyproject.toml          # All dependencies
├── .env.example            # Environment variable template
├── .gitignore
│
├── part1/                  # LangGraph + LangSmith + Ollama
│   ├── complete/
│   │   └── agent.py        # ✅ Fully working — reference for follow-along laptop
│   └── live/
│       └── agent.py        # 🔲 Scaffolded — for live coding on presenter laptop
│
└── part2/                  # Claude Haiku + Native Tool Use + Skills
    ├── complete/
    │   ├── agent.py        # ✅ Fully working
    │   └── skills/
    │       ├── summarize.py
    │       └── save_report.py
    └── live/
        ├── agent.py        # 🔲 Scaffolded
        └── skills/
            ├── summarize.py  # 🔲 Scaffolded
            └── save_report.py  # 🔲 Scaffolded
```

---

## Part 1 — LangGraph + LangSmith + Ollama (~60 min)

**The project:** A "Topic Brief" agent that searches the web, summarizes findings, and saves a report.

**The point:** Every byte of data is visible. You write the graph. The model just fills in the text.

### Concepts introduced in order

| Layer | Concept | Code |
|-------|---------|------|
| 1 | `AgentState` — the entire pipeline as a typed dict | `class AgentState(TypedDict)` |
| 2 | Local model + free search tool | `ChatOllama` + `DuckDuckGoSearchRun` |
| 3 | Nodes — one job each, read state, return only changed keys | `def search_node(state)` |
| 4 | Graph — the code IS the diagram | `workflow.add_edge(...)` |
| 5 | Observability — see every token, every tool call | LangSmith dashboard |
| 6 | Conditional logic — where pipeline becomes agent | `add_conditional_edges` |

### Run the complete version
```bash
uv run python part1/complete/agent.py
```

### Run the live scaffold (presenter laptop)
```bash
uv run python part1/live/agent.py
```

---

## Part 2 — Claude Haiku + Native Tool Use + Skills (~45 min)

**The project:** The exact same task — but now Claude manages the data flow itself.

**The point:** Watch how many layers disappear when the model is capable enough to handle orchestration.

### What changes vs Part 1

| Part 1 (LangGraph) | Part 2 (Claude) |
|-------------------|-----------------|
| `AgentState` TypedDict | Context window (implicit) |
| `search_node` function | Native `web_search` tool (built-in) |
| `should_retry` router | Claude decides (no code) |
| `workflow.add_edge()` graph | Claude decides (no code) |
| LangSmith traces | `print` + Anthropic dashboard |

### The skills

Claude Code generates two skills during the demo:

**`summarize.py`** — wraps a Claude API call to distill raw search results into bullet points

**`save_report.py`** — saves the final brief to a `.txt` file

These are the *only* custom code Claude can't handle natively. Everything else — searching, routing, retrying, knowing when it's done — happens inside the model.

### Run the complete version
```bash
uv run python part2/complete/agent.py
```

### Run the live scaffold (presenter laptop)
```bash
uv run python part2/live/agent.py
```

---

## Workshop Flow

```
[Presenter]  Part 1 intro — what is data flow in an agentic system?    (10 min)
[Live code]  Build Part 1 layer by layer                               (40 min)
[Demo]       Run it — show LangSmith trace                             (10 min)
             ── break / discussion ──
[Presenter]  The contrast — what does a capable model change?          (10 min)
[Live code]  Build skills with Claude Code, then wire agent.py         (25 min)
[Demo]       Run it — count how many layers disappeared                (10 min)
[Discussion] When do you reach for LangGraph vs raw Claude?            (15 min)
```

---

## Key Discussion Points

**After Part 1:**
- What would break if the model returned garbage? Who catches it?
- Could you swap Ollama for GPT-4 without changing any agent code?

**After Part 2:**
- The context window is the pipeline. What happens when it fills up?
- We only wrote 2 skills. What's a 3rd one you'd add?

**The big question:**
> When does it make sense to use LangGraph vs just using Claude with tools?

| Reach for LangGraph when... | Stick with Claude when... |
|----------------------------|--------------------------|
| Multiple specialized agents with handoffs | Single agent, well-scoped task |
| You need human-in-the-loop approval steps | You trust the model's routing |
| Workflow must survive server restarts | Ephemeral, session-based tasks |
| Using weak or local models | Using a capable frontier model |
| You need deterministic, auditable control flow | Flexibility matters more than auditability |

---

## Going Further

- **LangGraph persistence** — swap in-memory state for Redis or PostgreSQL checkpointing
- **LangSmith evals** — set up automated quality checks on agent outputs
- **Multi-agent** — add a "planner" agent that breaks tasks into subtasks for a "worker" agent
- **Claude Code** — use it to generate new skills on the fly, then register them as tools

---

## Tech Stack

| Tool | Role | Cost |
|------|------|------|
| `llama3.2:3b` via Ollama | Part 1 LLM | Free (local) |
| DuckDuckGo Search | Part 1 web search | Free |
| LangGraph | Workflow orchestration | Free (OSS) |
| LangSmith | Observability | Free tier available |
| Claude Haiku (`claude-haiku-4-5`) | Part 2 LLM | ~$0.001 per demo run |
| Anthropic native web search | Part 2 web search | Included with API |
