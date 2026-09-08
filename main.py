import os
from typing import TypedDict, Annotated

from dotenv import load_dotenv

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch


load_dotenv()


# ============================================================
# TAVILY - OPTIONAL
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
# GEMINI - WRITER
# ============================================================

writer_llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
)


# Bind Tavily only when the API key exists
if tools:
    writer_llm_with_tools = writer_llm.bind_tools(tools)
else:
    writer_llm_with_tools = writer_llm


# ============================================================
# GROQ - REVIEWER
# ============================================================

reviewer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY")
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
# WRITER PROMPT
# ============================================================

writer_system_prompt = """
You are an expert LinkedIn content writer.

Your task is to create a high-quality LinkedIn post.

Requirements:

- Start with a strong hook.
- Make the post engaging and human.
- Focus on ONE clear main takeaway.
- Use short paragraphs.
- Keep the post between 150 and 200 words.
- End with a meaningful question or call-to-action.
- Do NOT use hashtags.
- Avoid unnecessary emojis.
- Avoid generic AI-sounding language.
- Make the writing professional but natural.

If the topic requires current information, statistics,
recent developments, or facts, use the available web
search tool.

If reviewer feedback is provided, improve the previous
draft according to that feedback.
"""


# ============================================================
# WRITER NODE
# ============================================================

def writer_node(state: State):

    topic = state["topic"]
    feedback = state.get("review_feedback", "")
    attempt = state.get("attempt", 0)

    attempt += 1

    if feedback:
        user_message = f"""
Create an improved LinkedIn post about:

{topic}

This is revision attempt {attempt}.

Previous reviewer feedback:
{feedback}

Fix the problems identified by the reviewer.
Return ONLY the LinkedIn post.
"""
    else:
        user_message = f"""
Create a LinkedIn post about:

{topic}

This is the first draft.

Return ONLY the LinkedIn post.
"""

    messages = [
        ("system", writer_system_prompt),
        ("human", user_message)
    ]

    response = writer_llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "attempt": attempt
    }


# ============================================================
# TOOL NODE
# ============================================================

if tools:
    tool_node = ToolNode(tools)


# ============================================================
# EXTRACT DRAFT
# ============================================================

def extract_draft_node(state: State):

    last_message = state["messages"][-1]

    content = last_message.content

    # Gemini can sometimes return structured content
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

            elif isinstance(item, str):
                text_parts.append(item)

        content = "".join(text_parts)

    return {
        "draft": content
    }


# ============================================================
# REVIEWER
# ============================================================

reviewer_system_prompt = """
You are a strict LinkedIn post reviewer.

Review the provided LinkedIn post.

Check:

1. Strong opening hook
2. One clear takeaway
3. Good readability and skimmability
4. Between 150 and 200 words
5. Professional but human tone
6. Meaningful CTA or question at the end
7. No hashtags
8. No unnecessary repetition
9. No generic AI-sounding language

Return EXACTLY this format:

VERDICT: APPROVED

or

VERDICT: REJECTED

FEEDBACK: <one short paragraph explaining why>
"""


def reviewer_node(state: State):

    draft = state["draft"]

    review_prompt = f"""
Review this LinkedIn post:

--- POST START ---

{draft}

--- POST END ---
"""

    response = reviewer_llm.invoke([
        ("system", reviewer_system_prompt),
        ("human", review_prompt)
    ])

    content = response.content

    verdict = "APPROVED" in content.upper()

    feedback = ""

    if "FEEDBACK:" in content:
        feedback = content.split("FEEDBACK:", 1)[1].strip()
    else:
        feedback = content

    return {
        "review_feedback": feedback,
        "is_approved": verdict
    }


# ============================================================
# ROUTERS
# ============================================================

def writer_router(state: State):

    last_message = state["messages"][-1]

    # If Gemini requested a tool
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "extract_draft"


def reviewer_router(state: State):

    if state["is_approved"]:
        return END

    if state["attempt"] >= 3:
        return END

    return "writer"


# ============================================================
# BUILD GRAPH
# ============================================================

graph = StateGraph(State)


graph.add_node("writer", writer_node)
graph.add_node("extract_draft", extract_draft_node)
graph.add_node("reviewer", reviewer_node)


if tools:
    graph.add_node("tools", tool_node)


graph.add_edge(START, "writer")


# Writer decides whether to use Tavily
if tools:

    graph.add_conditional_edges(
        "writer",
        writer_router,
        {
            "tools": "tools",
            "extract_draft": "extract_draft"
        }
    )

    # After Tavily, go back to writer so Gemini
    # can use the search results to create the post.
    graph.add_edge("tools", "writer")

else:

    graph.add_edge("writer", "extract_draft")


graph.add_edge(
    "extract_draft",
    "reviewer"
)


graph.add_conditional_edges(
    "reviewer",
    reviewer_router,
    {
        "writer": "writer",
        END: END
    }
)


# ============================================================
# COMPILE
# ============================================================

app = graph.compile()
