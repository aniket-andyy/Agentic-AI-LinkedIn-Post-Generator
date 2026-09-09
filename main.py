import os
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

# --- API Keys (Streamlit automatically injects secrets into os.environ) ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# --- Tools ---
search_tool = TavilySearch(max_results=3, api_key=TAVILY_API_KEY)
tools = [search_tool]

# --- LLMs ---
writer_llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, google_api_key=GOOGLE_API_KEY)
writer_llm_with_tools = writer_llm.bind_tools(tools)

reviewer_llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.2, api_key=GROQ_API_KEY)

# --- State Definition ---
class State(TypedDict):
    topic: str 
    messages: Annotated[list, add_messages]
    draft: str 
    review_feedback: str
    is_approved: bool 
    attempt: int

# --- System Prompts ---
WRITER_SYSTEM_PROMPT = (
    "You are an expert LinkedIn content writer. Your job is to write "
    "engaging, professional LinkedIn posts about the given topic. "
    "If the topic requires up-to-date information, statistics, or "
    "current trends, use the web search tool to gather fresh context "
    "before writing. If you have already received feedback on a "
    "previous draft, carefully address every point in the new draft. "
    "Rules for good LinkedIn posts: strong hook in the first line, "
    "1 clear takeaway, easy to skim (short paragraphs), around "
    "150–200 words, ends with a question or call-to-action to invite "
    "engagement. Do not use hashtags."
)

REVIEWER_SYSTEM_PROMPT = (
    "You are a strict LinkedIn content reviewer. You judge whether a "
    "post is publish-ready. Evaluate against these criteria:\n"
    "1. Strong hook in the first line\n2. One clear, valuable takeaway\n"
    "3. Easy to skim — uses short paragraphs\n4. Roughly 150-200 words\n"
    "5. Ends with an engaging question or CTA\n6. Professional but human tone\n"
    "7. No hashtags\n\nRespond in exactly this format:\n"
    "VERDICT: APPROVED or REJECTED\nFEEDBACK: <one short paragraph explaining why>"
)

# --- Nodes ---
def writer_node(state: State) -> dict:
    attempt = state.get("attempt", 0) + 1 
    topic = state["topic"]
    previous_feedback = state.get('review_feedback', '')

    messages = list(state.get("messages", []))
    add_prompt = False
    
    if not messages:
        add_prompt = True
    elif messages and isinstance(messages[-1], type(messages[0])) and not getattr(messages[-1], 'tool_calls', None):
        # Check if we returned from a text-only message (Reviewer rejection loop)
        add_prompt = True

    state_update_messages = []

    if add_prompt:
        if attempt == 1:
            user_message = f"Write a LinkedIn post on this topic: {topic}. If you need current info, search the web first."
        else:
            user_message = (
                f"Your previous draft on '{topic}' was rejected. "
                f"Here is the reviewer's feedback:\n\n{previous_feedback}\n\n"
                f"Write a new, improved draft that fixes every issue mentioned. Do not repeat the same mistake."
            )
        
        new_messages = [
            ("system", WRITER_SYSTEM_PROMPT), 
            ("human", user_message)
        ]
        messages.extend(new_messages)
        state_update_messages.extend(new_messages)

    # Invoke LLM with the fully constructed message history
    response = writer_llm_with_tools.invoke(messages)
    state_update_messages.append(response)

    return {
        "messages": state_update_messages,
        "attempt": attempt
    }

tool_node = ToolNode(tools)

def extract_draft_node(state: State) -> dict:
    """Extracts the final text draft from the last AI message."""
    last_message = state['messages'][-1]
    draft = ""
    
    # Robustly extract text from LangChain message content
    content = getattr(last_message, 'content', "")
    
    if isinstance(content, str):
        draft = content
    elif isinstance(content, list):
        # FIX: Gemini returns content as a list of dicts when tool-calling is enabled.
        # e.g., [{'type': 'text', 'text': 'actual post...', 'extras': {...}}]
        text_parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
            elif isinstance(block, str):
                text_parts.append(block)
        draft = "\n".join(text_parts)
        
    return {"draft": draft.strip()}

def reviewer_node(state: State) -> dict:
    draft = state['draft']
    prompt = f"Review this LinkedIn post draft:\n{draft}\nGive your review."
    
    response = reviewer_llm.invoke([("system", REVIEWER_SYSTEM_PROMPT), ("human", prompt)])
    review_text = response.content.strip()
    
    is_approved = "APPROVED" in review_text.upper().split("FEEDBACK")[0]
    feedback = review_text.split("FEEDBACK:", 1)[1].strip() if "FEEDBACK:" in review_text else review_text

    return {"review_feedback": feedback, "is_approved": is_approved}

# --- Routing Logic ---
def should_use_tool(state: State):
    last_message = state['messages'][-1]
    return "tools" if getattr(last_message, 'tool_calls', None) else "extract_draft"

def should_stop_looping(state: State):
    if state['is_approved'] or state['attempt'] >= 3:
        return END 
    return "writer"

# --- Build Graph ---
graph = StateGraph(State)
graph.add_node("writer", writer_node)
graph.add_node("tools", tool_node)
graph.add_node("extract_draft", extract_draft_node)
graph.add_node("reviewer", reviewer_node)

graph.add_edge(START, "writer")
graph.add_conditional_edges("writer", should_use_tool, {"tools": "tools", "extract_draft": "extract_draft"})

graph.add_edge("tools", "writer") 
graph.add_edge("extract_draft", "reviewer")
graph.add_conditional_edges("reviewer", should_stop_looping)

app = graph.compile()
