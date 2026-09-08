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
# OPTIONAL TAVILY SEARCH TOOL
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
# LLMs
# ============================================================

# -------------------------
# Writer - Mistral
# -------------------------

writer_llm = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0.7
)

# Bind Tavily only when the API key exists
if tools:
    writer_llm_with_tools = writer_llm.bind_tools(tools)
else:
    writer_llm_with_tools = writer_llm


# -------------------------
# Reviewer - Groq
# -------------------------

reviewer_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
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
# WRITER SYSTEM PROMPT
# ============================================================

WRITER_SYSTEM_PROMPT = """
You are an expert LinkedIn content writer.

Your job is to write engaging, professional LinkedIn posts
about the given topic.

If current information, statistics, recent events, or trends
are required and a web search tool is available, use the web
search tool before writing.

If web search is not available, write the post using your
existing knowledge. Do not mention that web search is
unavailable.

If you have received feedback on a previous draft, carefully
address every point in the feedback.

Rules:

1. Strong hook in the first line
2. One clear and valuable takeaway
3. Easy to skim
4. Short paragraphs
5. Around 150-200 words
6. Professional but human tone
7. End with a question or call-to-action
8. Do not use hashtags
"""


# ============================================================
# WRITER NODE
# ============================================================

def writer_node(state: State) -> dict:

    attempt = state.get("attempt", 0) + 1

    topic = state["topic"]
    previous_feedback = state.get("review_feedback", "")

    # -------------------------
    # First attempt
    # -------------------------

    if attempt == 1:

        user_message = f"""
Write a LinkedIn post about:

{topic}

Create the best possible post following all the rules.

If the topic requires current information and the web search
tool is available, search the web first.
"""

    # -------------------------
    # Rewrite
    # -------------------------

    else:

        user_message = f"""
Your previous LinkedIn post about:

{topic}

was rejected by the reviewer.

Here is the reviewer's feedback:

{previous_feedback}

Write a completely improved version of the post.

Fix every issue mentioned in the feedback.
Do not repeat the same mistakes.

Follow all LinkedIn writing requirements.
"""

    messages = [
        ("system", WRITER_SYSTEM_PROMPT),
        ("human", user_message)
    ]

    response = writer_llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "attempt": attempt
    }


# ============================================================
# TAVILY TOOL NODE
# ============================================================

if tools:
    tool_node = ToolNode(tools)


# ============================================================
# EXTRACT DRAFT
# ============================================================

def extract_draft_node(state: State) -> dict:

    last_message = state["messages"][-1]

    draft = last_message.content

    return {
        "draft": draft
    }


# ============================================================
# REVIEWER SYSTEM PROMPT
# ============================================================

REVIEWER_SYSTEM_PROMPT = """
You are a strict LinkedIn content reviewer.

You judge whether a LinkedIn post is publish-ready.

Evaluate the post against these criteria:

1. Strong hook in the first line
2. One clear and valuable takeaway
3. Easy to skim
4. Short paragraphs
5. Roughly 150-200 words
6. Ends with an engaging question or CTA
7. Professional but human tone
8. Not corporate-robotic
9. No hashtags

Respond in exactly this format:

VERDICT: APPROVED or REJECTED
FEEDBACK: <one short paragraph explaining why>

Be strict but fair.

Approve only if the post genuinely meets the criteria.
Reject if one or more important criteria are clearly missing.
"""


# ============================================================
# REVIEWER NODE
# ============================================================

def reviewer_node(state: State) -> dict:

    draft = state["draft"]

    prompt = f"""
Review this LinkedIn post draft:

-------------------------
{draft}
-------------------------

Give your review using the exact required format.
"""

    response = reviewer_llm.invoke(
        [
            ("system", REVIEWER_SYSTEM_PROMPT),
            ("human", prompt)
        ]
    )

    review_text = response.content.strip()

    # Determine verdict
    first_part = review_text.upper().split("FEEDBACK", 1)[0]

    is_approved = "VERDICT: APPROVED" in first_part

    # Extract feedback
    if "FEEDBACK:" in review_text:
        feedback = review_text.split(
            "FEEDBACK:", 1
        )[1].strip()
    else:
        feedback = review_text

    return {
        "review_feedback": feedback,
        "is_approved": is_approved
    }


# ============================================================
# WRITER ROUTER
# ============================================================

def should_use_tool(state: State):

    last_message = state["messages"][-1]

    # Tavily is not configured
    if not tools:
        return "extract_draft"

    # Writer requested a tool
    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "extract_draft"


# ============================================================
# REVIEWER ROUTER
# ============================================================

def should_stop_looping(state: State):

    if state["is_approved"]:
        return END

    # Maximum 3 writer attempts
    if state["attempt"] >= 3:
        return END

    return "writer"


# ============================================================
# BUILD GRAPH
# ============================================================

graph = StateGraph(State)

graph.add_node(
    "writer",
    writer_node
)

graph.add_node(
    "extract_draft",
    extract_draft_node
)

graph.add_node(
    "reviewer",
    reviewer_node
)

# Add Tavily node only if API key exists
if tools:

    graph.add_node(
        "tools",
        tool_node
    )


# ============================================================
# EDGES
# ============================================================

graph.add_edge(
    START,
    "writer"
)

graph.add_conditional_edges(
    "writer",
    should_use_tool
)

# If Tavily exists
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
