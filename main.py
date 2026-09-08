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


# =========================
# Tavily Search Tool
# =========================

tavily_api_key = os.getenv("TAVILY_API_KEY")

search_tool = TavilySearch(
    max_results=3,
    tavily_api_key=tavily_api_key
)

tools = [search_tool]


# =========================
# Writer Agent - Mistral
# =========================

writer_llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.7,
)

writer_llm_with_tools = writer_llm.bind_tools(tools)


# =========================
# Reviewer Agent - Groq
# =========================

reviewer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)


# =========================
# State
# =========================

class State(TypedDict):
    topic: str
    messages: Annotated[list, add_messages]
    draft: str
    review_feedback: str
    is_approved: bool
    attempt: int


# =========================
# Writer
# =========================

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

Rewrite the LinkedIn post based on the feedback.

Requirements:
- Strong opening hook
- One clear takeaway
- Short paragraphs
- Easy to scan
- 150-200 words
- Professional but human
- End with a question or CTA
- Do not use hashtags
- Use web search when current information, statistics,
  trends, or recent facts are required.
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
- Use web search when current information, statistics,
  trends, or recent facts are required.
"""

    response = writer_llm_with_tools.invoke(
        state["messages"] + [("user", prompt)]
    )

    return {
        "messages": [response],
        "attempt": attempt
    }


# =========================
# Tool Decision
# =========================

def should_use_tool(state: State):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "extract_draft"


# =========================
# Extract Draft
# =========================

def extract_draft(state: State):

    last_message = state["messages"][-1]

    draft = last_message.content

    return {
        "draft": draft
    }


# =========================
# Reviewer
# =========================

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


# =========================
# Reviewer Decision
# =========================

def should_stop_looping(state: State):

    if state["is_approved"]:
        return END

    if state["attempt"] >= 3:
        return END

    return "writer"


# =========================
# Graph
# =========================

graph = StateGraph(State)

graph.add_node("writer", writer)
graph.add_node("tools", ToolNode(tools))
graph.add_node("extract_draft", extract_draft)
graph.add_node("reviewer", reviewer)

graph.add_edge(START, "writer")

graph.add_conditional_edges(
    "writer",
    should_use_tool
)

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

app = graph.compile()
