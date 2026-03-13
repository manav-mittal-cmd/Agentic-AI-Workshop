# Agentic AI Workshop

> CS Club Workshop — *Understanding the Data Flow In Agentic Systems*

A workshop that builds intuition for agentic AI from the ground up. Utilizes LangGraph + a local model + LangSmith

---

## Setup

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.11+ | Runtime | [python.org](https://python.org) |
| uv | Package manager | [docs.astral.sh/uv/getting-started](https://docs.astral.sh/uv/getting-started/installation/) |
| Ollama | Local LLM | [ollama.com](https://ollama.com) |
| LangSmith account | Observability | [smith.langchain.com](https://smith.langchain.com) |

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd agentic-ai-workshop

# Create virtual environment
uv venv <venv-name>
source <venv-name>/bin/activate

# Install dependencies
uv sync

# Pull the local model
# NOTE: have ollama running on your device in the background before pulling a specific version
ollama pull llama3.2:3b

# Set up environment variables [OPTIONAL]
# go into your project directory
touch .env
```

Add the following to your .env file. 
```Python
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY="<your-environment-key>"
LANGCHAIN_PROJECT="<project-name>"
```

---

## Repository Structure

```
agentic-ai-workshop/
├── pyproject.toml          # All dependencies
├── uv.lock                 # All dependencies
├── .env                    # Environment variables (NOT pushed to repo)
├── .gitignore
├── README.md
│
├── agent.py                # Simple agent framework for summarizing a search result
├── news-agent.py           # News Digest Agent
├── Sources.txt             # List of websites to search through
```

---

## News Agent: LangGraph + LangSmith + Ollama

**The project:** An agent that searches a list of news sites, ranks important news findings, summarizes findings, and saves a report.

**The point:** Understand how your data flows from one task to another.

### Concepts introduced in order

| Layer | Concept | Code |
|-------|---------|------|
| 1 | `AgentState` — the entire pipeline as a typed dict | `class AgentState(TypedDict)` |
| 2 | Local model + free search tool | `ChatOllama` + `DuckDuckGoSearchRun` |
| 3 | Nodes — one job each, read state | `def search_node(state)` |
| 4 | Graph — connects the nodes | `workflow.add_edge(...)` |
| 5 | Conditional logic — where pipeline becomes agent | `add_conditional_edges` |
| 6 | Observability — see every token, every tool call | LangSmith dashboard |


### Run the complete version
```bash
uv run python news_agent_refined.py
```

---

## Going Further

- **LangGraph persistence** — swap in-memory state for Redis or PostgreSQL checkpointing
- **LangSmith evals** — set up automated quality checks on agent outputs
- **Multi-agent** — add a "planner" agent that breaks tasks into subtasks for a "worker" agent
- **Prompt Engineering** — play around with what prompts work best for different Ollama models

---
