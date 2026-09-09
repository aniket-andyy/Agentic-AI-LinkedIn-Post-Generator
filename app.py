import os
import time
import html
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Agentic AI LinkedIn Post Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Premium Custom CSS ---
st.markdown("""
<style>
    /* Base Theme */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1 {
        background: linear-gradient(90deg, #00D2FF, #3A7BD5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0;
    }
    h3 { color: #E0E6ED; font-weight: 600; }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .glass-card h3 { color: #00D2FF; margin-top: 0; font-size: 16px; }
    .glass-card p { color: #B0B8C4; font-size: 15px; margin-bottom: 0;}
    
    /* Premium Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 12px 24px; border-radius: 8px;
        font-weight: 600; transition: all 0.3s ease; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    
    /* Workflow Diagram */
    .workflow-container { display: flex; align-items: center; justify-content: center; margin: 40px 0; flex-wrap: wrap; }
    .workflow-node { display: flex; flex-direction: column; align-items: center; gap: 12px; flex: 0 0 auto; }
    .node-circle { width: 24px; height: 24px; border-radius: 50%; background: #2C2F36; border: 2px solid #4A4E58; transition: all 0.3s ease; }
    .node-label { font-size: 13px; color: #A0AAB5; font-weight: 500; text-align: center; font-family: monospace; }
    .workflow-node.completed .node-circle { background: #00D2FF; border-color: #00D2FF; box-shadow: 0 0 10px rgba(0, 210, 255, 0.5); }
    .workflow-node.completed .node-label { color: #00D2FF; }
    .workflow-node.active .node-circle { background: #FFB800; border-color: #FFB800; box-shadow: 0 0 15px rgba(255, 184, 0, 0.6); animation: pulse 1.5s infinite; }
    .workflow-node.active .node-label { color: #FFB800; font-weight: 700; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
    .workflow-connector { flex: 1; height: 2px; background: #4A4E58; min-width: 20px; margin-bottom: 30px; }
    
    /* Output Area */
    .final-post-box {
        background: rgba(0, 210, 255, 0.05); border: 1px solid rgba(0, 210, 255, 0.2);
        border-radius: 12px; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 16px; line-height: 1.6; white-space: pre-wrap; color: #E0E6ED;
    }
    
    /* Badges */
    .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-right: 8px; text-transform: uppercase; }
    .badge-success { background: rgba(46, 204, 113, 0.2); color: #2ECC71; border: 1px solid rgba(46, 204, 113, 0.4); }
    .badge-error { background: rgba(231, 76, 60, 0.2); color: #E74C3C; border: 1px solid rgba(231, 76, 60, 0.4); }
    
    /* Footer */
    .footer { text-align: center; padding: 40px 0 20px; color: #666; font-size: 14px; }
    .footer a { color: #00D2FF; text-decoration: none; margin: 0 10px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- Helper UI Components ---
def render_workflow_diagram(active_node, completed_nodes):
    nodes = ["START", "Writer", "Search", "Draft", "Reviewer", "Approval", "Final Post"]
    node_map = {"writer": "Writer", "tools": "Search", "extract_draft": "Draft", "reviewer": "Reviewer"}
    html_code = '<div class="workflow-container">'
    
    for node in nodes:
        status = "pending"
        if node == "START": status = "completed" if active_node != "START" else "active"
        elif node == "Final Post": status = "completed" if "Final Post" in completed_nodes else ("active" if active_node == "Final Post" else "pending")
        elif node == "Approval": status = "completed" if "reviewer" in completed_nodes else ("active" if active_node == "reviewer" else "pending")
        else:
            mapped = [k for k, v in node_map.items() if v == node]
            status = "completed" if any(m in completed_nodes for m in mapped) else ("active" if active_node in mapped else "pending")
        
        html_code += f'<div class="workflow-node {status}"><div class="node-circle"></div><div class="node-label">{node}</div></div>'
        if node != "Final Post": html_code += '<div class="workflow-connector"></div>'
            
    st.markdown(html_code + '</div>', unsafe_allow_html=True)

def render_system_architecture():
    st.markdown("### System Architecture")
    cols = st.columns(4)
    cards = [
        {"name": "Gemini Writer Agent", "desc": "Generates and rewrites the LinkedIn post."},
        {"name": "Tavily Web Search", "desc": "Provides fresh web context when current information is required."},
        {"name": "Groq Reviewer Agent", "desc": "Critically evaluates the generated post against quality criteria."},
        {"name": "LangGraph", "desc": "Orchestrates the iterative writer-reviewer workflow."}
    ]
    for i, card in enumerate(cards):
        with cols[i]:
            st.markdown(f'<div class="glass-card" style="min-height: 140px;"><h3>{card["name"]}</h3><p>{card["desc"]}</p></div>', unsafe_allow_html=True)

# --- Security & Backend Check ---
required_keys = ["GOOGLE_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY"]
missing = [k for k in required_keys if not os.environ.get(k)]

if missing:
    st.error(f"Missing API Keys: {', '.join(missing)}. Please configure them in `.streamlit/secrets.toml`.")
    st.code("GOOGLE_API_KEY = '...'\nGROQ_API_KEY = '...'\nTAVILY_API_KEY = '...'")
    st.stop()

try:
    from main import app as graph_app
except Exception as e:
    st.error(f"Failed to load LangGraph backend: {e}")
    st.stop()

# --- Session State Initialization ---
if "generating" not in st.session_state: st.session_state.generating = False
if "final_state" not in st.session_state: st.session_state.final_state = None
if "topic" not in st.session_state: st.session_state.topic = ""
if "events_log" not in st.session_state: st.session_state.events_log = []

# --- Header ---
st.markdown('<h1>Agentic AI LinkedIn Post Generator</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 20px; color: #A0AAB5; margin-top: -10px;">(Using LangGraph Iterative Workflow)</p>', unsafe_allow_html=True)
st.markdown('<p style="color: #B0B8C4; font-size: 16px;">An autonomous writer-reviewer system that generates, evaluates, and iteratively improves LinkedIn posts.</p>', unsafe_allow_html=True)

st.markdown("""
<div class="glass-card" style="padding: 16px; display: flex; justify-content: space-between; align-items: center;">
    <span style="font-family: monospace; font-weight: 600; color: #00D2FF;">Developer — ANIKET SHARMA</span>
    <div>
        <a href="https://www.linkedin.com/in/aniket-sharma-42a700418" target="_blank" style="color: #FAFAFA; text-decoration: none; margin-right: 15px; font-weight: 500;">LinkedIn</a>
        <a href="https://github.com/aniket-andyy" target="_blank" style="color: #FAFAFA; text-decoration: none; font-weight: 500;">GitHub</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Main Input ---
st.markdown("### What do you want to write about?")
st.markdown('<p style="color: #B0B8C4; margin-bottom: 20px;">The agent will research when necessary, write a draft, review it, and iteratively improve it.</p>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    topic_input = st.text_input("Topic", placeholder="Enter a topic, technology, idea, trend, or concept...", label_visibility="collapsed", value=st.session_state.topic)
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_clicked = st.button("Generate LinkedIn Post", use_container_width=True)

if generate_clicked:
    if not topic_input.strip():
        st.warning("Please enter a topic before generating.")
    else:
        st.session_state.topic = topic_input
        st.session_state.generating = True
        st.session_state.final_state = None
        st.session_state.events_log = []
        st.rerun()

# --- Real-Time Generation Workflow ---
if st.session_state.generating and not st.session_state.final_state:
    st.markdown("### Agentic Workflow Progress")
    progress_container = st.empty()
    status_container = st.empty()
    
    initial_state = {"topic": st.session_state.topic, "messages": [], "draft": "", "review_feedback": "", "is_approved": False, "attempt": 0}
    current_state = initial_state.copy()
    completed_nodes = ["START"]
    active_node = "writer"
    
    try:
        # Stream updates from LangGraph in real-time
        for chunk in graph_app.stream(initial_state):
            node_name = list(chunk.keys())[0]
            state_update = chunk[node_name]
            active_node = node_name
            
            # Update local state tracker
            for k, v in state_update.items():
                if k == "messages": current_state["messages"].extend(v)
                else: current_state[k] = v
            
            # Update Workflow Diagram
            with progress_container.container():
                render_workflow_diagram(active_node, completed_nodes)
                
            # Update Status Terminal
            with status_container.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                if node_name == "writer":
                    attempt = current_state.get("attempt", 1)
                    st.write(f"✍️ **Gemini Writer** is generating draft (Attempt {attempt})...")
                    st.session_state.events_log.append(f"Attempt {attempt}: Gemini Writer generated a draft.")
                elif node_name == "tools":
                    st.write("🔍 **Tavily Search** is finding fresh context...")
                    st.session_state.events_log.append("Tavily Search executed to gather fresh context.")
                elif node_name == "extract_draft":
                    st.write("📝 Extracting the final draft from writer messages...")
                elif node_name == "reviewer":
                    st.write("🧐 **Groq Reviewer** is evaluating the draft...")
                    if "is_approved" in state_update and state_update["is_approved"]:
                        st.success("✅ Draft approved by Reviewer!")
                        completed_nodes.append("Final Post")
                        st.session_state.events_log.append("Draft approved by Reviewer.")
                    else:
                        st.error("❌ Draft rejected. Preparing for revision...")
                        if "review_feedback" in state_update: st.info(f"**Reviewer Feedback:** {state_update['review_feedback']}")
                        st.session_state.events_log.append(f"Draft rejected. Feedback: {state_update.get('review_feedback', '')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            if node_name not in completed_nodes: completed_nodes.append(node_name)
            time.sleep(0.1) # UI breathing room
            
        # Finalize Diagram
        with progress_container.container():
            render_workflow_diagram("Final Post", completed_nodes)
            
        st.session_state.final_state = current_state
        st.session_state.generating = False
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred during generation: {str(e)}")
        st.session_state.generating = False

# --- Display Final Output ---
if st.session_state.final_state:
    final_state = st.session_state.final_state
    st.markdown("### Generated LinkedIn Post")
    
    col_out, col_meta = st.columns([3, 1])
    with col_out:
        st.markdown(f'<div class="final-post-box">{final_state.get("draft", "No draft generated.")}</div>', unsafe_allow_html=True)
        
    with col_meta:
        status_badge = "<span class='badge badge-success'>APPROVED</span>" if final_state.get("is_approved") else "<span class='badge badge-error'>REJECTED (Max Attempts)</span>"
        st.markdown(f"""
        <div class="glass-card">
            <p><strong>Status:</strong> {status_badge}</p>
            <p><strong>Attempts:</strong> {final_state.get("attempt", 0)}</p>
            <p style="margin-top: 15px; font-size: 13px; color: #B0B8C4;"><strong>Feedback:</strong> {final_state.get("review_feedback", "None")}</p>
        </div>
        """, unsafe_allow_html=True)
        
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📋 Copy Post", use_container_width=True, key="copy_btn"):
            st.toast("Post copied to clipboard!")
            safe_draft = final_state.get("draft", "").replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
            st.components.v1.html(f"<script>navigator.clipboard.writeText(`{safe_draft}`);</script>", height=0)
    with c2:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.final_state = None
            st.session_state.generating = True
            st.session_state.events_log = []
            st.rerun()
    with c3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.final_state = None
            st.session_state.topic = ""
            st.rerun()

    with st.expander("🔍 View Agentic Workflow Log"):
        for log in st.session_state.events_log:
            st.write(f"- {log}")

# --- Architecture & Footer ---
st.markdown("---")
render_system_architecture()

st.markdown("""
<div class="footer">
    Built by <strong>ANIKET SHARMA</strong><br>
    <a href="https://www.linkedin.com/in/aniket-sharma-42a700418" target="_blank">LinkedIn</a> | 
    <a href="https://github.com/aniket-andyy" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
