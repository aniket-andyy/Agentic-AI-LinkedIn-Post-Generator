import streamlit as st
import time
from main import app 

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Post Studio",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM CSS ---
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #09090b;
    --bg-card: #18181b;
    --bg-input: #09090b;
    --border-subtle: #27272a;
    --border-accent: #3f3f46;
    --text-main: #fafafa;
    --text-muted: #a1a1aa;
    --accent-violet: #8b5cf6;
    --accent-indigo: #6366f1;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}

/* Global Overrides */
.stApp {
    background-color: var(--bg-main);
    color: var(--text-main);
    font-family: var(--font-sans);
}

header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-sans);
    color: var(--text-main) !important;
    letter-spacing: -0.02em;
}
p, li, div {
    color: var(--text-muted);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #09090b !important;
    border-right: 1px solid var(--border-subtle) !important;
}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 1.5rem !important;
    font-family: var(--font-mono) !important;
}

/* Inputs */
.stTextArea textarea {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
    font-size: 1.1rem !important;
    padding: 1rem !important;
    transition: all 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent-violet) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}
.stTextArea label {
    color: #d4d4d8 !important;
    font-weight: 500 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.85rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(139, 92, 246, 0.1), 0 2px 4px -1px rgba(139, 92, 246, 0.06);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.2), 0 4px 6px -2px rgba(139, 92, 246, 0.1);
}

/* Alerts / Warnings */
.stAlert {
    background-color: rgba(39, 39, 42, 0.5) !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 8px !important;
}

/* Custom Classes */
.premium-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.gradient-text {
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

.eyebrow {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--accent-violet);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.tech-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background-color: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 9999px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: #d4d4d8;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}

.workflow-node {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 1.5rem;
    height: 100%;
    transition: all 0.2s ease;
}
.workflow-node:hover {
    border-color: #3f3f46;
    transform: translateY(-2px);
}
.workflow-node-num {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: #71717a;
    margin-bottom: 0.5rem;
}
.workflow-node-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #fafafa;
    margin-bottom: 0.25rem;
}
.workflow-node-sub {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: #a1a1aa;
}

.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 600;
}
.status-approved {
    background-color: rgba(34, 197, 94, 0.1);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.2);
}
.status-warning {
    background-color: rgba(234, 179, 8, 0.1);
    color: #facc15;
    border: 1px solid rgba(234, 179, 8, 0.2);
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    color: #fafafa !important;
    font-weight: 500 !important;
}
.streamlit-expanderHeader:hover {
    background-color: #27272a !important;
}
.streamlit-expanderContent {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1.5rem !important;
}

/* Code Block (Used for Final Post with native copy button) */
.stCodeBlock {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.stCodeBlock code {
    font-family: var(--font-sans) !important;
    font-size: 1.05rem !important;
    line-height: 1.6 !important;
    color: var(--text-main) !important;
    white-space: pre-wrap !important;
}
.stCodeBlock [data-testid="stCodeBlockLanguage"] {
    display: none !important;
}
.stCodeBlock .stCopyButton {
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #d4d4d8 !important;
}

/* Navbar Links */
.nav-link {
    color: #a1a1aa;
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    transition: color 0.2s ease;
}
.nav-link:hover {
    color: #fafafa;
}

/* Status */
.stStatusRunning .stStatusIcon { color: var(--accent-violet) !important; }
.stStatusComplete .stStatusIcon { color: #4ade80 !important; }
.stStatusError .stStatusIcon { color: #ef4444 !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def render_navbar():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div style="padding-top: 1rem;"><span style="font-family: var(--font-mono); color: #8b5cf6; font-size: 1.2rem;">◈</span> <strong style="font-size: 1.2rem; letter-spacing: -0.02em; color: #fafafa;">AI POST STUDIO</strong></div>', unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style="text-align: right; padding-top: 1rem;">
                <span style="color: #a1a1aa; font-size: 0.875rem; margin-right: 1.5rem; font-weight: 500;">ANIKET SHARMA</span>
                <a href="https://www.linkedin.com/in/aniket-sharma-42a700418?utm_source=share_via&utm_content=profile&utm_medium=member_android" target="_blank" class="nav-link" style="margin-right: 1.5rem;">LinkedIn</a>
                <a href="https://github.com/aniket-andyy" target="_blank" class="nav-link">GitHub</a>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #27272a; margin: 1.5rem 0;'>", unsafe_allow_html=True)

def render_hero():
    st.markdown("""
        <div style="text-align: center; margin: 4rem 0;">
            <div class="eyebrow">AGENTIC AI · ITERATIVE CONTENT ENGINE</div>
            <h1 style="font-size: 3.5rem; margin-bottom: 1.5rem;">
                AGENTIC AI <br>
                <span class="gradient-text">LINKEDIN POST GENERATOR</span>
            </h1>
            <p style="font-size: 1.25rem; max-width: 600px; margin: 0 auto; margin-bottom: 2rem;">
                Research when necessary. Generate with Mistral Small.<br>
                Review with Llama 3.3 70B. Iterate until the post is ready.
            </p>
            <div>
                <span class="tech-badge">Mistral Small</span>
                <span class="tech-badge">Llama 3.3 70B</span>
                <span class="tech-badge">Tavily</span>
                <span class="tech-badge">LangGraph</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_workspace():
    st.markdown("""
        <div class="premium-card" style="padding-bottom: 1rem;">
            <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Create your post</h2>
            <p style="margin-bottom: 1.5rem; color: #a1a1aa;">Give the agent a topic. It will research, write, review and refine the result.</p>
        </div>
    """, unsafe_allow_html=True)

    topic = st.text_area(
        "LinkedIn topic",
        placeholder="The future of Agentic AI in software development",
        height=120
    )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("Generate LinkedIn Post", use_container_width=True)

    return topic, generate_btn

def render_workflow():
    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 3rem;">
            <h2 style="font-size: 2rem; margin-bottom: 0.5rem;">How the agent works</h2>
            <p style="color: #a1a1aa;">A multi-step iterative generation pipeline</p>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    nodes = [
        ("01", "WRITER", "Mistral Small"),
        ("02", "RESEARCH", "Tavily"),
        ("03", "REVIEW", "Llama 3.3 70B"),
        ("04", "ITERATE", "Max 3 Attempts")
    ]

    for i, col in enumerate(cols):
        with col:
            num, title, sub = nodes[i]
            st.markdown(f"""
                <div class="workflow-node">
                    <div class="workflow-node-num">{num}</div>
                    <div class="workflow-node-title">{title}</div>
                    <div class="workflow-node-sub">{sub}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem; color: #52525b; font-family: var(--font-mono); font-size: 0.85rem; line-height: 1.5;">
            WRITER → SEARCH → DRAFT → REVIEW → APPROVAL
            <br>
            ↖──────── REWRITE ────────┘
        </div>
    """, unsafe_allow_html=True)

def render_result(state):
    st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <h2 style="font-size: 2rem; margin-bottom: 0.5rem;">Final LinkedIn Post</h2>
            <span class="status-badge" style="background-color: rgba(139, 92, 246, 0.1); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.2);">Generated by Agentic Workflow</span>
        </div>
    """, unsafe_allow_html=True)

    # Using st.code provides a native, secure copy button without external JS dependencies
    # The CSS above overrides the code block to look like a premium sans-serif card
    st.code(state['draft'], language="text")

def render_review(state):
    st.markdown("<hr style='border: 1px solid #27272a; margin: 3rem 0;'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Review Status")
        if state.get("is_approved"):
            st.markdown("""
                <div class="status-badge status-approved">APPROVED</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="status-badge status-warning">MAXIMUM ATTEMPTS REACHED</div>
            """, unsafe_allow_html=True)
        st.markdown(f"<p style='font-family: var(--font-mono); margin-top: 1.5rem; font-size: 0.9rem;'>Attempts: <span style='color: #fafafa;'>{state.get('attempt', 0)}</span> / 3</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Reviewer Feedback")
        with st.expander("View Reviewer Feedback"):
            feedback = state.get("review_feedback", "No feedback provided.")
            st.markdown(f"<div style='white-space: pre-wrap; line-height: 1.6;'>{feedback}</div>", unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("<h3>Agent Configuration</h3>", unsafe_allow_html=True)
        st.markdown("""
            <div style="margin-bottom: 2rem;">
                <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;">WRITER</div>
                <div style="font-weight: 500; color: #fafafa;">Mistral Small</div>
            </div>
            <div style="margin-bottom: 2rem;">
                <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;">REVIEWER</div>
                <div style="font-weight: 500; color: #fafafa;">Llama 3.3 70B</div>
            </div>
            <div style="margin-bottom: 2rem;">
                <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;">WEB SEARCH</div>
                <div style="font-weight: 500; color: #fafafa;">Tavily</div>
            </div>
            <div style="margin-bottom: 2rem;">
                <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;">ORCHESTRATION</div>
                <div style="font-weight: 500; color: #fafafa;">LangGraph</div>
            </div>
            <div style="margin-bottom: 2rem;">
                <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #71717a; margin-bottom: 0.25rem;">MAX ATTEMPTS</div>
                <div style="font-weight: 500; color: #fafafa;">3</div>
            </div>
            <hr style="border: 1px solid #27272a; margin: 2rem 0;">
            <div style="font-size: 0.8rem; color: #71717a;">
                Agentic AI LinkedIn Generator<br>
                Built by <strong style="color: #d4d4d8;">ANIKET SHARMA</strong>
            </div>
        """, unsafe_allow_html=True)

def render_developer_footer():
    st.markdown("<div style='margin-top: 6rem;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #27272a;'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem;">ANIKET SHARMA</div>
            <div style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 1.5rem;">AI & Machine Learning Developer</div>
            <a href="https://www.linkedin.com/in/aniket-sharma-42a700418?utm_source=share_via&utm_content=profile&utm_medium=member_android" target="_blank" class="nav-link" style="margin-right: 1.5rem;">LinkedIn</a>
            <a href="https://github.com/aniket-andyy" target="_blank" class="nav-link">GitHub</a>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN APP FLOW ---
def main():
    render_sidebar()
    render_navbar()
    render_hero()

    topic, generate_btn = render_workspace()

    if generate_btn:
        if not topic.strip():
            st.warning("Please provide a topic for the agentic workflow to process.")
        else:
            with st.status("Agentic workflow running...", expanded=True) as status:
                st.write("Executing multi-step agentic pipeline...")
                st.write("Researching, drafting, and reviewing iteratively.")
                
                initial_state = {
                    "topic": topic,
                    "messages": [],
                    "draft": "",
                    "review_feedback": "",
                    "is_approved": False,
                    "attempt": 0,
                }
                
                try:
                    final_state = app.invoke(initial_state)
                    status.update(label="Generation complete!", state="complete", expanded=False)
                    st.session_state['final_state'] = final_state
                except Exception as e:
                    status.update(label="Generation failed", state="error", expanded=True)
                    st.error(f"An error occurred during the workflow: {str(e)}")

    render_workflow()

    if 'final_state' in st.session_state:
        state = st.session_state['final_state']
        render_result(state)
        render_review(state)

    render_developer_footer()

if __name__ == "__main__":
    main()
