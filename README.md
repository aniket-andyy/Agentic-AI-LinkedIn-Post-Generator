⚡ Agentic AI LinkedIn Post Generator

«An autonomous Writer → Reviewer → Improver pipeline powered by LangGraph, Gemini, Groq & Tavily.»

<p align="center">Generate → Research → Review → Improve → Publish

</p>---

🧠 What is this?

This project is an Agentic AI workflow that generates high-quality LinkedIn posts and iteratively improves them using an AI-powered review loop.

Unlike a traditional:

Prompt → LLM → Output

pipeline, this system works more like:

                  ┌──────────────────┐
                  │    User Topic    │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │   ✍️ Writer Agent │
                  │      Gemini      │
                  └────────┬─────────┘
                           │
                     Need fresh info?
                       ↙          ↘
                    YES            NO
                     ↓              │
             ┌──────────────┐       │
             │ Tavily Search│       │
             └──────┬───────┘       │
                    └───────┬───────┘
                            ↓
                  ┌──────────────────┐
                  │   📝 Draft       │
                  └────────┬─────────┘
                           ↓
                  ┌──────────────────┐
                  │ 🔍 Reviewer Agent│
                  │      Groq        │
                  └────────┬─────────┘
                           ↓
                    ┌─────────────┐
                    │  Approved?  │
                    └──────┬──────┘
                       YES │ NO
                           │  ↘
                           ↓   ┌──────────────────┐
                       ┌───────┤ Feedback Loop    │
                       │       └────────┬─────────┘
                       │                ↓
                       │        Writer improves
                       │                │
                       │                └───→ Review
                       ↓
                    🚀 FINAL
                     POST

---

✨ Core Idea

The goal isn't simply to make an LLM write.

The goal is to make the system reason through a workflow.

The Writer creates.

The Reviewer critiques.

The Writer learns from the feedback.

The graph decides what happens next.

That creates an iterative agentic loop:

┌──────────┐
│  WRITER  │
└────┬─────┘
     ↓
┌──────────┐
│  DRAFT   │
└────┬─────┘
     ↓
┌──────────┐
│ REVIEWER │
└────┬─────┘
     ↓
   ┌───────────────┐
   │               │
APPROVED        REJECTED
   │               │
   ↓               ↓
 FINAL         FEEDBACK
 POST              │
                   ↓
                WRITER
                   │
                   └──────→ REVIEWER

---

🏗️ Architecture

AI Layer

Component| Role
Gemini| Writer Agent
Groq| Reviewer Agent
Tavily| Real-time web research
LangGraph| Agent orchestration

Workflow Nodes

START
  │
  ▼
Writer
  │
  ├──── Tool Call ────► Tavily
  │                       │
  │                       └────► Writer
  │
  ▼
Extract Draft
  │
  ▼
Reviewer
  │
  ├──── APPROVED ────► END
  │
  └──── REJECTED ────► Writer
                         │
                         └──── Improve Draft

---

⚙️ Tech Stack

<p align="center">"Python" · "LangGraph" · "LangChain" · "Gemini" · "Groq" · "Tavily" · "Streamlit"

</p>🔹 LangGraph

Controls the stateful agent workflow and conditional routing.

🔹 Gemini

Acts as the primary Writer Agent.

It generates the LinkedIn post and can call the web search tool when current information is required.

🔹 Groq

Acts as the Reviewer Agent.

It evaluates the generated post against predefined quality criteria.

🔹 Tavily

Provides web search capabilities when the Writer needs current information, statistics, or trends.

🔹 Streamlit

Provides the interactive frontend for entering topics and viewing generated posts.

---

🔄 Agentic Workflow

01 — User Input

The user provides a topic:

"RAG vs Fine-Tuning"

↓

02 — Writer Agent

Gemini receives the topic and generates the first draft.

If current information is required, it can invoke:

Tavily Search

↓

03 — Draft Extraction

The generated response is converted into a clean text draft.

↓

04 — Reviewer Agent

Groq evaluates the draft using predefined criteria:

✓ Strong hook
✓ Clear takeaway
✓ Easy to skim
✓ 150–200 words
✓ Engaging CTA
✓ Professional tone
✓ No hashtags

↓

05 — Decision

The reviewer returns:

VERDICT: APPROVED

or:

VERDICT: REJECTED
FEEDBACK: ...

↓

06 — Feedback Loop

If rejected, the feedback is passed back to the Writer.

The Writer generates an improved version.

The process repeats until:

APPROVED

or:

MAX ATTEMPTS = 3

---

🧩 LangGraph State

The workflow maintains shared state between agents:

class State(TypedDict):
    topic: str
    messages: Annotated[list, add_messages]
    draft: str
    review_feedback: str
    is_approved: bool
    attempt: int

This allows the agents to communicate through a centralized workflow state.

---

🧠 Conditional Routing

One of the important parts of the project is that the graph isn't completely linear.

Tool Routing

def should_use_tool(state):
    last_message = state["messages"][-1]

    return (
        "tools"
        if getattr(last_message, "tool_calls", None)
        else "extract_draft"
    )

The Writer can dynamically decide whether it needs external information.

Review Routing

def should_stop_looping(state):

    if state["is_approved"] or state["attempt"] >= 3:
        return END

    return "writer"

This creates the iterative improvement loop.

---

🚀 Features

- 🤖 Multi-agent workflow
- 🔄 Iterative self-improvement
- 🧠 Stateful LangGraph architecture
- 🌐 Real-time web research
- 🔍 Dedicated AI reviewer
- ⚡ Fast inference with Groq
- ✍️ AI-powered content generation
- 🛑 Maximum retry protection
- 🔀 Conditional graph routing
- 🖥️ Streamlit interface
- 🧩 Tool-calling support

---

📂 Project Structure

agentic-ai-linkedin-post-generator/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
├── README.md
└── .gitignore

---

🔐 Environment Variables

Create a ".env" file:

GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

For Streamlit Cloud, add the same credentials through:

Streamlit
   ↓
Settings
   ↓
Secrets

Never commit API keys to GitHub.

---

📦 Installation

1. Clone the repository

git clone https://github.com/YOUR_USERNAME/agentic-ai-linkedin-post-generator.git

2. Enter the project

cd agentic-ai-linkedin-post-generator

3. Create a virtual environment

python -m venv venv

4. Activate it

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate

5. Install dependencies

pip install -r requirements.txt

6. Add API keys

Create:

.env

and add:

GOOGLE_API_KEY=...
GROQ_API_KEY=...
TAVILY_API_KEY=...

7. Run

streamlit run app.py

---

🎯 Example

Input

RAG vs Fine-Tuning

Agent

Gemini
   ↓
Research if required
   ↓
Draft
   ↓
Groq Reviewer
   ↓
Rejected
   ↓
Feedback
   ↓
Gemini
   ↓
Improved Draft
   ↓
Groq Reviewer
   ↓
Approved

Output

A polished LinkedIn post ready for editing and publishing.

---

🧪 Why this project?

Most LLM applications follow:

INPUT → LLM → OUTPUT

This project explores a different approach:

INPUT
  ↓
AGENT
  ↓
TOOL
  ↓
OUTPUT
  ↓
EVALUATOR
  ↓
FEEDBACK
  ↓
AGENT
  ↓
IMPROVED OUTPUT

The focus is therefore not only LLM generation, but agent orchestration, tool use, state management, evaluation, and iterative refinement.

---

🔮 Future Improvements

Potential upgrades include:

              ┌───────────────────┐
              │ Current System    │
              └─────────┬─────────┘
                        ↓
                 ┌──────────────┐
                 │ RAG Memory   │
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │ User Profile │
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │ Style Agent  │
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │ Fact Checker │
                 └──────┬───────┘
                        ↓
                 ┌──────────────┐
                 │ Final Agent  │
                 └──────────────┘

Possible additions:

- 🧠 Persistent user memory
- 📚 RAG-based knowledge retrieval
- 🎯 Personalized writing styles
- 🔎 Dedicated fact-checking agent
- 📊 Content quality scoring
- 🧪 A/B testing for hooks
- 🧵 Multiple content formats
- 📈 LinkedIn engagement optimization
- 🗃️ Conversation history
- 👥 Multiple specialized agents

---

🏆 What I Learned

Building this project helped me understand that Agentic AI is more than simply connecting an LLM to a tool.

The real engineering challenge is designing:

STATE
 ↓
TOOLS
 ↓
DECISIONS
 ↓
FEEDBACK
 ↓
ITERATION
 ↓
CONTROL

LangGraph makes it possible to explicitly model these interactions as a controllable workflow instead of hiding everything inside a single prompt.

---

👨‍💻 Developer

ANIKET SHARMA

AI & Machine Learning Developer
Generative AI • Agentic AI • Machine Learning • Robotics

«Building intelligent systems that don't just generate —
they reason, evaluate, and improve.»

---

⭐ If you find this project useful

Consider giving the repository a ⭐ on GitHub.

Built with curiosity. Engineered with AI. ⚡
