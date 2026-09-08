import os
from typing import TypedDict, Annotated

from dotenv import load_dotenv

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch


load_dotenv()


# ============================================================
# OPTIONAL TAVILY TOOL
# ============================================================

tavily_api_key = os.getenv("TAVILY_API_KEY")

tools = []

if tavily_api_key:
    search_tool = TavilySearch(
        max_results=3,
        tavily_api_key=tavily_api_key
    )

    tools = [search_tool]


# ============================================================
# WRITER AGENT - MISTRAL
# ============================================================

writer_llm = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0.7,
)

# Only bind tools if Tavily is available
if tools:
    writer_llm_with_tools = writer_llm.bind_tools(tools)
else:
    writer_llm_with_tools = writer_llm


# ============================================================
# REVIEWER AGENT - GROQ
# ============================================================

reviewer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)


# ============================================================
# STATE
# ============================================================

class State(TypedDict):
    topic: str
    messages: Annotated[list, add_messages]
    draft: str
    review_feedback: str
    is_approved: bool
    attempt: int


# ============================================================
# WRITER NODE
# ============================================================

def writer(state: State):

    attempt = state.get("attempt", 0) + 1

    topic = state["topic"]
    feedback = state.get("review_feedback", "")

    if feedback:

        prompt = f"""
You are an expert LinkedIn content writer.

Topic:
{topic}

Previous reviewer feedback:
{feedback}

Rewrite the LinkedIn post based on the reviewer feedback.

Requirements:
- Strong opening hook
- One clear takeaway
- Short paragraphs
- Easy to scan
- 150-200 words
- Professional but human
- End with a question or CTA
- Do not use hashtags
"""

    else:

        prompt = f"""
You are an expert LinkedIn content writer.

Create a high-quality LinkedIn post about:

{topic}

Requirements:
- Strong opening hook
- One clear takeaway
- Short paragraphs
- Easy to scan
- 150-200 words
- Professional but human
- End with a question or CTA
- Do not use hashtags
"""

        # Tell the model that web search is available only
        # when Tavily API is configured.
        if tools:
            prompt += """
- Use the web search tool when current information,
  statistics, trends, or recent facts are required.
"""

    response = writer_llm_with_tools.invoke(
        state["messages"] + [("user", prompt)]
    )

    return {
        "messages": [response],
        "attempt": attempt
    }


# ============================================================
# WRITER ROUTER
# ============================================================

def should_use_tool(state: State):

    last_message = state["messages"][-1]

    # If Tavily isn't configured, there cannot be a tool call.
    if not tools:
        return "extract_draft"

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "extract_draft"


# ============================================================
# TAVILY TOOL NODE
# ============================================================

if tools:

    tool_node = ToolNode(tools)


# ============================================================
# EXTRACT DRAFT
# ============================================================

def extract_draft(state: State):

    last_message = state["messages"][-1]

    return {
        "draft": last_message.content
    }


# ============================================================
# REVIEWER NODE
# ============================================================

def reviewer(state: State):

    draft = state["draft"]

    prompt = f"""
You are a strict LinkedIn post reviewer.

Review this LinkedIn post:

{draft}

Check:

1. Strong opening hook
2. Clear takeaway
3. Easy to read and scan
4. 150-200 words
5. Strong CTA/question
6. Human and professional tone
7. No hashtags

Return EXACTLY this format:

VERDICT: APPROVED or REJECTED
FEEDBACK: <one short paragraph explaining your decision>
"""

    response = reviewer_llm.invoke(prompt)

    content = response.content

    approved = "VERDICT: APPROVED" in content

    feedback = content

    if "FEEDBACK:" in content:
        feedback = content.split("FEEDBACK:", 1)[1].strip()

    return {
        "is_approved": approved,
        "review_feedback": feedback
    }


# ============================================================
# REVIEWER ROUTER
# ============================================================

def should_stop_looping(state: State):

    if state["is_approved"]:
        return END

    if state["attempt"] >= 3:
        return END

    return "writer"


# ============================================================
# BUILD LANGGRAPH
# ============================================================

graph = StateGraph(State)

graph.add_node("writer", writer)
graph.add_node("extract_draft", extract_draft)
graph.add_node("reviewer", reviewer)

# Add Tavily node only when API key exists
if tools:
    graph.add_node("tools", tool_node)


graph.add_edge(START, "writer")

graph.add_conditional_edges(
    "writer",
    should_use_tool
)

if tools:
    graph.add_edge(
        "tools",
        "extract_draft"
    )

graph.add_edge(
    "extract_draft",
    "reviewer"
)

graph.add_conditional_edges(
    "reviewer",
    should_stop_looping
)


# ============================================================
# COMPILE
# ============================================================

app = graph.compile()
