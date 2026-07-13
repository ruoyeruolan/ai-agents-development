# AI Agent Development — Your 14-Week Roadmap

**Built for:** Python basics · 10–20 hrs/week · Goal: career-ready skills
**Outcome:** You can design, build, evaluate, and deploy LLM agents — backed by a GitHub portfolio of 5+ projects and the fundamentals to handle AI-engineer interviews.
*Prepared July 2026. The field moves fast — if you're reading this months later, re-verify tools and links.*

## Why this plan is shaped the way it is

1. **Fundamentals before frameworks.** Anthropic's guidance for builders is to start with direct LLM API calls — most agent patterns are a few lines of code, and frameworks add abstraction that hides what's actually happening. Interviews probe fundamentals, so you'll build the agent loop from scratch before touching LangGraph.
2. **One shipped project per phase.** Employers hire on evidence, not certificates. Everything goes on GitHub.
3. **Evaluation is the career differentiator.** Anyone can demo an agent; few people can make one reliable. Phases 5–6 are where you separate from the crowd.
4. **Simplest thing that works.** A large share of real-world "agent" tasks are actually solved by a single well-prompted LLM call with structured output. Knowing when *not* to build an agent is itself a job skill.

## The map

| Weeks | Phase | Theme | You ship |
|---|---|---|---|
| 1 | 0 | Toolkit & Python leveling | "Hello, LLM" repo |
| 2–3 | 1 | LLM & API foundations | CLI chat assistant |
| 4–5 | 2 | Tool use & the agent loop (no framework) | Research agent from scratch |
| 6 | 3 | RAG, memory & context engineering | "Chat with your docs" agent |
| 7–9 | 4 | Frameworks (LangGraph) + MCP | Agent rebuilt with human-in-the-loop + custom MCP server |
| 10–11 | 5 | Evals, observability, guardrails | Eval suite + fully traced agent |
| 12–14 | 6 | Capstone & career packaging | Deployed capstone + portfolio |

Weekly rhythm: ~60% building, ~30% courses/docs, ~10% reading and community. The phases matter more than the week numbers — at a steady 10 hrs/week this stretches to ~17 weeks, at 20 hrs/week some phases compress. Don't skip Phase 2 or 5 no matter what.

---

## Phase 0 — Week 1: Toolkit & Python leveling

**Goal:** a professional dev setup and the specific Python you'll use constantly.

**Learn / set up:**
- Git + GitHub: init, commit, branch, push, write a README
- Environments: `uv` (modern, fast) or `venv` + pip; VS Code; a `.env` file with `python-dotenv` for API keys (never commit keys)
- Python essentials for agent work: functions and type hints, dicts/JSON handling, error handling with try/except, classes and dataclasses, Pydantic models, `async/await` basics, HTTP calls with `httpx`
- Get an API key (Anthropic Console and/or OpenAI) and understand tokens and pricing so costs never surprise you — use the cheapest model tier while learning

**Resources:**
- Official Python tutorial for any gaps: https://docs.python.org/3/tutorial/
- GitHub getting started: https://docs.github.com/en/get-started
- Anthropic API getting started: https://docs.claude.com
- Pydantic docs (just the "Models" page for now): https://docs.pydantic.dev

**Ship:** a repo `hello-agent` containing a script that sends a prompt to an LLM API, streams the reply to the terminal, and prints tokens used + estimated cost. README explains setup.

**Checkpoint — you can explain:** what a token is · why API keys live in `.env` · what `async` buys you · the difference between a system and a user message.

---

## Phase 1 — Weeks 2–3: LLM & API foundations

**Goal:** total comfort with the raw ingredients every agent is made of.

**Learn:**
- Chat structure: system vs user vs assistant messages; the API is stateless, *you* manage conversation history
- Sampling controls: temperature, max tokens; when to use temperature 0
- Streaming responses
- Prompt engineering: clear instructions, few-shot examples, structured/XML prompts, giving the model room to reason
- Structured output: requesting JSON, validating with Pydantic, retrying on invalid output — this pattern alone powers a huge share of production systems
- The model landscape: capability tiers vs price; develop on cheap models, test on strong ones
- Intuition for what's under the hood (pick one): 3Blue1Brown's neural networks/Transformer series or Andrej Karpathy's "Intro to Large Language Models" on YouTube

**Resources:**
- Anthropic Academy — "Building with the Claude API" (free, ~8 hrs of video, certificate): https://anthropic.skilljar.com
- Anthropic prompt engineering docs: https://docs.claude.com
- `anthropics/courses` Jupyter notebooks (code along): https://github.com/anthropics/courses
- DeepLearning.AI short courses, free to audit — pick one on prompting or structured output: https://www.deeplearning.ai/short-courses/

**Ship — Project 1: CLI chat assistant.** Multi-turn memory, streaming, switchable system-prompt personas, `/save` command for transcripts, and a running token/cost meter. Stretch goal: when history gets long, summarize older turns and keep the summary in context.

**Checkpoint — you can:** manage conversation history by hand · reliably get valid JSON from a model · estimate what 1,000 user queries would cost.

---

## Phase 2 — Weeks 4–5: Tool use & the agent loop (from scratch)

**This is the heart of the entire plan.** An agent is just an LLM in a loop, with tools, working toward a goal. Build that loop yourself once and no framework will ever be magic to you.

**Learn:**
- Tool use (function calling): defining tool schemas, letting the model request a call, executing it in your code, returning the result to the model
- The agent loop: call model → if it requests a tool, run it → append result → call model again → stop when the task is done or max iterations hit
- Read **"Building Effective Agents"** (Anthropic) — twice. Internalize the core distinction: *workflows* (prompt chaining, routing, parallelization, orchestrator–workers, evaluator–optimizer) vs *agents*, and the advice to use the simplest pattern that works
- ReAct — the 2022 paper that named the reason-then-act pattern; skim for grounding
- Failure handling: malformed tool calls, tool errors, runaway loops, timeouts, max-iteration guards

**Resources:**
- Building Effective Agents: https://www.anthropic.com/research/building-effective-agents
- Tool use guide + cookbook examples: https://docs.claude.com and https://github.com/anthropics/anthropic-cookbook
- OpenAI, "A Practical Guide to Building Agents" (free PDF): https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- ReAct paper: https://arxiv.org/abs/2210.03629

**Ship — Project 2: research agent, zero frameworks.** Tools: web search (Tavily or Brave Search API have free tiers), calculator, and file read/write. It should handle questions like "Compare the populations of Japan's three largest cities and save a summary to a file." Include a max-iteration guard and print a readable trace of every step it takes.

**Checkpoint — you can:** whiteboard the agent loop from memory · explain when a workflow beats an agent · name the five workflow patterns with a use case for each. (This checkpoint is interview gold.)

---

## Phase 3 — Week 6: RAG, memory & context engineering

**Goal:** give agents knowledge they weren't trained on, and manage their limited attention.

**Learn:**
- Embeddings and similarity search; chunking strategies; a local vector store (Chroma is the easiest start)
- The RAG pipeline: ingest → embed → retrieve → insert into prompt → answer with citations
- Agentic RAG: retrieval as a *tool* the agent decides when to call
- Memory patterns: rolling summaries for short-term; files or a small database for long-term
- Context engineering: deciding what goes into the context window and what stays out — read Anthropic's engineering posts on effective context engineering and on writing effective tools for agents

**Resources:**
- Anthropic engineering blog (context engineering, tool-writing posts): https://www.anthropic.com/engineering
- Chroma getting started: https://docs.trychroma.com
- A DeepLearning.AI RAG short course (audit free): https://www.deeplearning.ai/short-courses/

**Ship — Project 3: "chat with your docs."** Ingest a folder of PDFs/markdown in a domain you know well, answer questions with citations to source chunks, then plug retrieval in as a tool on your Phase 2 agent.

**Checkpoint — you can:** explain chunk-size tradeoffs · describe two ways RAG fails and why.

---

## Phase 4 — Weeks 7–9: Frameworks & MCP

Now that you know what frameworks abstract away, learn the ones the job market actually uses.

**Learn:**
- **LangGraph** (weeks 7–8) — the current production standard for stateful agent orchestration: graphs, nodes and edges, state, checkpointing/persistence, human-in-the-loop interrupts, streaming. Do LangChain Academy's free "Introduction to LangGraph."
- **MCP — Model Context Protocol** (week 9) — the open standard for connecting agents to tools and data; think USB-C for AI integrations. Every major framework now supports it. Build a server exposing 2–3 custom tools and connect it to Claude. Anthropic Academy's MCP courses walk this end-to-end in Python, including the three primitives: tools, resources, prompts.
- **Survey the landscape** (a half-day each, breadth for interviews): OpenAI Agents SDK, Claude Agent SDK, CrewAI, Pydantic AI. Know each one's sweet spot; you don't need mastery.
- Multi-agent patterns: orchestrator–workers, subagents for context isolation

**Resources:**
- LangChain Academy (free): https://academy.langchain.com
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- MCP spec and tutorials: https://modelcontextprotocol.io
- Anthropic Academy MCP courses: https://anthropic.skilljar.com
- Hugging Face AI Agents Course — free, beginner-to-expert, covers smolagents/LlamaIndex/LangGraph, optional certificate; good parallel track: https://huggingface.co/learn/agents-course

**Ship — Project 4a:** rebuild your research agent in LangGraph with persistent checkpoints and a human-approval interrupt before any file write. **Project 4b:** a custom MCP server for something personal — your notes, a hobby API, your work domain. MCP servers make excellent portfolio pieces because other people can actually plug them into their own agents.

**Checkpoint — you can:** explain what LangGraph checkpointing gives you over your hand-rolled loop · describe MCP's client–server architecture and its three primitives.

---

## Phase 5 — Weeks 10–11: Evaluation, observability & guardrails

**The career differentiator.** Demos are easy; reliability is what gets hired.

**Learn:**
- Tracing: instrument your agent with LangSmith (free tier, deepest LangGraph integration) or Langfuse (open-source, self-hostable) so you can see every step, token, and dollar
- Building an eval set: 25–50 real test cases with expected outcomes, graded by exact match, rubric, or LLM-as-judge
- Regression testing: re-run evals on every prompt or model change; track pass rates over time
- Agent-specific metrics: task success rate, tool-selection accuracy, steps-to-completion, cost per task
- Guardrails: prompt injection (treat untrusted content as data, never instructions), tool permissioning, sandboxing, human approval for irreversible actions
- Cost and latency: prompt caching, model routing (cheap model for easy steps)

**Resources:**
- LangSmith: https://docs.langchain.com/langsmith · Langfuse: https://langfuse.com/docs — both have solid evaluation guides
- A DeepLearning.AI agent-evaluation short course (audit free)
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/

**Ship — Project 5:** add tracing plus a ~30-case eval suite to your Phase 4 agent. Deliberately break it — ambiguous requests, adversarial inputs, failing tools — measure, fix, re-measure. Write an `EVALS.md` documenting the before/after numbers. This document impresses interviewers more than the agent itself.

**Checkpoint — you can:** explain LLM-as-judge and its pitfalls · describe a prompt-injection attack against your own agent and how you mitigated it.

---

## Phase 6 — Weeks 12–14: Capstone & career packaging

**Goal:** one substantial, deployed, documented project plus a portfolio that gets interviews.

**Pick ONE capstone, ideally in a domain you already know** (domain knowledge + agents is your edge over CS grads):
1. Customer-support agent over a product's docs, with escalation/handoff logic
2. Personal ops agent: email triage → drafted replies, calendar-aware
3. Data-analysis agent: CSV in → cleaned data, charts, and a written report out
4. Code-review or documentation agent for a GitHub repository

**The bar that reads as "professional":**
- Deployed: FastAPI backend + minimal web UI, or a Slack/Discord bot
- README with an architecture diagram and a "why these design choices" section
- Eval results table and example traces
- A 2–3 minute demo video
- Costs documented: what do 1,000 requests cost?

**Career moves (run in parallel):**
- Pin your 3 best repos; polish every README
- Write 2–3 posts (LinkedIn or a blog): "What I learned building X" — hiring managers genuinely read these
- Target titles: AI Engineer, Agent Engineer, Forward-Deployed Engineer, Solutions Engineer (AI), LLM Application Developer
- Interview prep themes: agent-vs-workflow design decisions, cost/latency tradeoffs, eval design, failure modes, RAG design, "how would you build X" system design
- Make one small open-source contribution to an agent tool (docs PRs count) — great interview conversation material

---

## Resource library (your organized materials)

**Official docs — bookmark all four:**
- Anthropic API: https://docs.claude.com
- OpenAI: https://platform.openai.com/docs
- LangGraph: https://langchain-ai.github.io/langgraph/
- MCP: https://modelcontextprotocol.io

**Free structured courses:**
- Anthropic Academy — free certificated courses on the Claude API, MCP, Claude Code, Skills, and subagents: https://anthropic.skilljar.com (hub: https://www.anthropic.com/learn)
- Hugging Face AI Agents Course: https://huggingface.co/learn/agents-course
- LangChain Academy — Introduction to LangGraph: https://academy.langchain.com
- DeepLearning.AI short courses (free to audit): https://www.deeplearning.ai/short-courses/
- Google/Kaggle 5-Day AI Agents Intensive — free, runs periodically; watch for the next cohort

**Essential reads, in this order:**
1. *Building Effective Agents* — Anthropic: https://www.anthropic.com/research/building-effective-agents
2. *A Practical Guide to Building Agents* — OpenAI (PDF)
3. Anthropic engineering blog: the context-engineering and tool-writing posts — https://www.anthropic.com/engineering
4. *12-Factor Agents* — principles for production-grade agents: https://github.com/humanlayer/12-factor-agents
5. Lilian Weng, *LLM Powered Autonomous Agents*: https://lilianweng.github.io/posts/2023-06-23-agent/
6. Book worth buying: *AI Engineering* by Chip Huyen (O'Reilly)

**Papers (optional, skim for interviews):** ReAct (arxiv 2210.03629) · Reflexion (2303.11366) · Toolformer (2302.04761)

**Staying current — 30 min/week, no more:**
- Simon Willison's blog: https://simonwillison.net
- Latent Space newsletter/podcast: https://www.latent.space
- Release notes of whatever framework you're using that week

**Tools you'll touch along the way:** Anthropic/OpenAI Python SDKs · Pydantic · httpx · Chroma · LangGraph · MCP Python SDK · LangSmith or Langfuse · FastAPI · uv · Git

---

## How we'll work together

Use me (Claude) as your always-available tutor. A cadence that works:

- **Start of each week:** "I'm on Week N of my agent roadmap — teach me [topic]." I'll explain it, check your understanding, and set the exercise.
- **Mid-week:** paste your code and ask for a review. I'll critique it like a senior engineer — bugs, design, style.
- **Stuck for more than ~30 minutes?** Bring me the error and what you've tried. (Struggle a little first; that's where the learning lives.)
- **End of each week:** "Quiz me on Week N's checkpoint" before moving on.

One honest warning from your tutor: let AI *explain* and *review*, but type the code yourself through at least Phase 3. If I write your agent loop for you, you'll freeze when an interviewer asks you to whiteboard it.

## Progress tracker

- [ ] Week 1 — `hello-agent` repo live on GitHub
- [ ] Week 3 — Project 1: CLI chat assistant
- [ ] Week 5 — Project 2: from-scratch research agent
- [ ] Week 6 — Project 3: chat-with-your-docs
- [ ] Week 9 — Project 4: LangGraph rebuild + custom MCP server
- [ ] Week 11 — Project 5: eval suite + tracing, `EVALS.md` written
- [ ] Week 14 — Capstone deployed, demo video recorded
- [ ] Portfolio — READMEs polished, 2+ posts published
