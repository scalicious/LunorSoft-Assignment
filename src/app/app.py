"""
src/app/app.py
==============
Main Streamlit application for Kuli AI.
Handles the chat interface, model selection, and displaying RAG sources.
"""

import os
import sys
import re
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rag.core_engine import is_ollama_available, get_available_ollama_models
from src.app.inference import stream_response

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kuli AI - Chat",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Premium IDE Styling ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    * { box-sizing: border-box; margin: 0; padding: 0; }

    .stApp {
        background-color: #050505;
        font-family: Söhne, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        color: #e2e8f0;
    }

    /* Ambient IDE grid */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image:
            linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }

    /* Glowing ambient orb */
    .stApp::after {
        content: '';
        position: fixed;
        top: -20%; left: -10%; width: 50vw; height: 50vw;
        background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    footer, #MainMenu { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 7rem; max-width: 1060px; position: relative; z-index: 1; }

    /* ── Sidebar Glassmorphism ── */
    section[data-testid="stSidebar"] {
        background: rgba(15, 17, 26, 0.7) !important;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-right: 1px solid rgba(255,255,255,0.05) !important;
        padding: 1.2rem 1rem;
    }

    .lunor-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 1.2rem;
    }
    .brand-icon {
        display: none;
    }
    .brand-text {
        font-size: 1.35rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .brand-badge {
        font-size: 0.62rem;
        color: #e0e7ff;
        background: linear-gradient(90deg, #4f46e5, #9333ea);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 999px;
        padding: 2px 9px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-top: 2px;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(79,70,229,0.3);
    }

    .sidebar-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #64748b;
        margin: 1.4rem 0 0.5rem;
    }

    /* ── Hero ── */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem 2rem;
        animation: fadeInDown 0.7s ease-out forwards;
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-18px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #a5b4fc;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 999px;
        padding: 0.4rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        backdrop-filter: blur(8px);
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1.2px;
        margin-bottom: 0.6rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        max-width: 90%;
        margin: 0 auto;
        word-wrap: break-word;
    }

    /* ── Code Blocks (Premium IDE) ── */
    pre {
        position: relative;
        background: rgba(9, 10, 15, 0.92) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.84rem !important;
        padding: 1.3rem !important;
        padding-top: 2.4rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.35) !important;
        overflow-x: auto;
    }
    code {
        font-family: 'JetBrains Mono', monospace !important;
        color: #c7d2fe !important;
        background: rgba(99,102,241,0.1) !important;
        padding: 2px 6px !important;
        border-radius: 5px !important;
    }

    /* ── Copy button injected via JS ── */
    .copy-btn {
        position: absolute;
        top: 0.6rem; right: 0.7rem;
        font-size: 0.7rem;
        font-family: 'JetBrains Mono', monospace;
        color: #94a3b8;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 3px 10px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .copy-btn:hover { color: #c7d2fe; border-color: rgba(99,102,241,0.5); }

    /* ── Citations ── */
    .citation-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0.8rem 0 0.4rem;
    }
    .citation-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.72rem;
        font-family: 'JetBrains Mono', monospace;
        color: #7dd3fc;
        background: rgba(56,189,248,0.1);
        border: 1px solid rgba(56,189,248,0.3);
        border-radius: 8px;
        padding: 4px 10px;
        transition: transform 0.2s, background 0.2s;
    }
    .citation-pill:hover { background: rgba(56,189,248,0.18); transform: translateY(-1px); }
    .citation-score { color: #34d399; font-size: 0.68rem; font-weight: 600; }

    /* ── Query Rewrite badge ── */
    .rewrite-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.69rem;
        font-family: 'JetBrains Mono', monospace;
        color: #fbbf24;
        background: rgba(251,191,36,0.08);
        border: 1px solid rgba(251,191,36,0.25);
        border-radius: 6px;
        padding: 3px 9px;
        margin-bottom: 0.5rem;
    }

    /* ── Memory indicator ── */
    .memory-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.68rem;
        color: #a78bfa;
        background: rgba(167,139,250,0.08);
        border: 1px solid rgba(167,139,250,0.2);
        border-radius: 6px;
        padding: 3px 8px;
    }

    /* ── Status ── */
    .status-online { color: #34d399; font-size: 0.75rem; font-weight: 600; text-shadow: 0 0 10px rgba(52,211,153,0.4); }
    .status-offline { color: #f87171; font-size: 0.75rem; font-weight: 600; }

    /* ── Chat ── */
    .stChatMessage { background: transparent !important; }
    [data-testid="chatAvatarIcon-user"] { background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important; }
    [data-testid="chatAvatarIcon-assistant"] { background: linear-gradient(135deg, #6366f1, #a855f7) !important; }

    /* ── Quick Prompts (GPT Style) ── */
    .stButton > button {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #c5c5d2 !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 0.8rem !important;
        text-align: left !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        background: rgba(255,255,255,0.05) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: #ececf1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Copy-to-Clipboard JS ──────────────────────────────────────────────────────
st.markdown("""
<script>
function addCopyButtons() {
    document.querySelectorAll('pre').forEach(function(pre) {
        if (pre.querySelector('.copy-btn')) return;
        var btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = ' Copy';
        btn.onclick = function() {
            var code = pre.querySelector('code');
            var text = code ? code.innerText : pre.innerText;
            navigator.clipboard.writeText(text).then(function() {
                btn.textContent = ' Copied!';
                setTimeout(function() { btn.textContent = ' Copy'; }, 1500);
            });
        };
        pre.style.position = 'relative';
        pre.appendChild(btn);
    });
}
var obs = new MutationObserver(addCopyButtons);
obs.observe(document.body, { childList: true, subtree: true });
addCopyButtons();
</script>
""", unsafe_allow_html=True)


# ─── Output Sanitizer ─────────────────────────────────────────────────────────
def sanitize_output(text: str) -> str:
    """
    Post-processes model output to ensure clean, well-formatted markdown:
    1. Strips non-ASCII characters (prevents random Chinese symbols).
    2. Removes any residual ChatML tokens.
    3. Strips trailing whitespace on each line.
    """
    # Remove ChatML artifacts
    text = re.sub(r'<\|im_start\|>.*?<\|im_end\|>', '', text, flags=re.DOTALL)
    text = re.sub(r'<\|im_start\|>|<\|im_end\|>', '', text)
    # Strip non-ASCII (preserves standard punctuation and emojis)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Clean up excessive blank lines (max 2 in a row)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip trailing spaces per line
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    return text.strip()


# ─── State Initialization ──────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # {role, content, citations?, rag_docs?, rewritten_query?}

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

ollama_online = is_ollama_available()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="kuli-brand">
        <div class="brand-icon"></div>
        <div>
            <div class="brand-text">Kuli AI</div>
            <span class="brand-badge">HYBRID RAG · 7B</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Model Selection ──
    st.markdown('<div class="sidebar-label">Inference Engine</div>', unsafe_allow_html=True)
    installed_models = ["Kuli (kuli-qwen-7b)", "Base Model (qwen2.5-coder:7b)"]

    default_idx = 0

    ui_engine_choice = st.selectbox(
        "Ollama Model",
        options=installed_models,
        index=default_idx,
        help="Select which model to chat with.",
        label_visibility="collapsed"
    )
    
    # Map UI choice to backend model name
    engine_choice = "kuli-qwen-7b:latest" if "Kuli" in ui_engine_choice else "qwen2.5-coder:7b"

    # ── Dynamic Compare Mode CSS Transition ──
    is_kuli = "kuli" in engine_choice.lower()
    if is_kuli:
        st.markdown("""
        <style>
        .stApp {
            background-color: #090a0f !important;
            transition: background-color 0.8s ease-in-out !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #1e293b !important;
            background-image: radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.05), transparent 25%),
                              radial-gradient(circle at 85% 30%, rgba(52, 211, 153, 0.05), transparent 25%) !important;
            transition: background-color 0.8s ease-in-out !important;
        }
        </style>
        """, unsafe_allow_html=True)

    if ollama_online:
        st.markdown(f'<span class="status-online">● Online: `{engine_choice}`</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-offline">○ Ollama Offline - run `ollama serve`</span>', unsafe_allow_html=True)

    # ── RAG Controls ──
    st.markdown('<div class="sidebar-label">RAG Pipeline</div>', unsafe_allow_html=True)
    use_rag = st.toggle("Enable Hybrid RAG", value=True, help="Injects context from the CS/C++/ML knowledge base using BM25 + Vector search.")
    use_reranker = st.toggle("Cross-Encoder Reranker", value=True, disabled=not use_rag,
                             help="Reranks candidates with ms-marco cross-attention. Mitigates Lost-in-the-Middle.")
    use_query_rewrite = st.toggle("Query Rewriting", value=True, disabled=not use_rag,
                                  help="Rewrites vague queries into precise technical queries before retrieval (~1s overhead).")

    # ── Memory ──
    st.markdown('<div class="sidebar-label">Conversation Memory</div>', unsafe_allow_html=True)
    memory_placeholder = st.empty()

    # ── Hyperparameters ──
    st.markdown('<div class="sidebar-label">Hyperparameters</div>', unsafe_allow_html=True)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05,
                            help="Lower = more factual, higher = more creative.")

    st.markdown("---")
    if st.button(" Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─── Hero View (empty state) ──────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-pill"> Hybrid RAG · Query Rewriting · Fine-Tuned 7B</div>
        <h1 class="hero-title">Kuli AI Assistant</h1>
        <p class="hero-subtitle">Production-grade coding copilot with multi-turn memory, hybrid retrieval, and Unsloth fine-tuning.</p>
    </div>
    """, unsafe_allow_html=True)

    QUICK_PROMPTS = [
        ("", "Cycle detection in a linked list using Floyd's Tortoise & Hare in C++"),
        ("", "Aggressive Cows: binary search on answer with greedy placement in C++"),
        ("", "Explain LoRA low-rank decomposition and its math: ΔW = B·A"),
        ("", "Find median of two sorted arrays in O(log(min(N,M))) - binary search"),
        ("", "0/1 Knapsack with 1D DP space optimization - trace through the loop"),
        ("", "How does Reciprocal Rank Fusion combine BM25 and vector search scores?"),
    ]

    cols = st.columns(3)
    for i, (icon, prompt_text) in enumerate(QUICK_PROMPTS):
        with cols[i % 3]:
            if st.button(f"{icon} {prompt_text}", key=f"quick_{i}", use_container_width=True):
                st.session_state.quick_prompt = prompt_text
                st.rerun()

# ─── Conversation History ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # ── ChatGPT Style Follow-up Suggestions ──
        if msg["role"] == "assistant":
            # We only want to show suggestions on the very last message in the chat
            is_last_msg = (msg == st.session_state.messages[-1])
            if is_last_msg:
                st.markdown("<br>", unsafe_allow_html=True)
                cols = st.columns(3)
                suggestions = [
                    "Explain this in simpler terms",
                    "Can you provide a real-world example?",
                    "What are the edge cases for this?"
                ]
                for idx, sugg in enumerate(suggestions):
                    with cols[idx]:
                        if st.button(f"✨ {sugg}", key=f"sugg_{len(st.session_state.messages)}_{idx}", use_container_width=True):
                            st.session_state.quick_prompt = sugg
                            st.rerun()
# ─── Input & Response Handling ────────────────────────────────────────────────
user_query = st.chat_input("Ask Kuli about algorithms, C++, system design, or ML...")

if st.session_state.quick_prompt:
    user_query = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        text_placeholder = st.empty()
        full_response = ""
        context_metadata = {}
        citations = []
        rewritten_query = None

        # Prepare conversation history (last 5 turns = 10 messages)
        chat_history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]  # Exclude current user message
        ][-10:]  # Sliding window of last 10 messages (5 turns)

        with st.spinner(" Thinking..."):
            stream_gen = stream_response(
                prompt=user_query,
                model_name=engine_choice,
                use_rag=use_rag,
                use_reranker=use_reranker,
                use_query_rewrite=use_query_rewrite,
                temperature=temperature,
                chat_history=chat_history
            )

            for event in stream_gen:
                if event["type"] == "meta":
                    context_metadata = event.get("context", {})
                    rewritten_query = context_metadata.get("rewritten_query")
                    # Handle stream metadata (no longer showing rewrite badge in UI)
                    if rewritten_query:
                        pass
                elif event["type"] == "token":
                    clean_token = re.sub(r'[^\x00-\x7F]+', '', event["token"])
                    full_response += clean_token
                    text_placeholder.markdown(full_response + "▌")
                elif event["type"] == "done":
                    citations = event.get("citations", [])
                    final_text = event.get("full_text", full_response)
                    full_response = sanitize_output(final_text)

        # Final render
        text_placeholder.markdown(full_response)



        # Store in session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "citations": citations,
            "rewritten_query": rewritten_query,
            "rag_docs": [
                {
                    "filename": d.metadata.get("filename"),
                    "section": d.metadata.get("section"),
                    "rerank_score": d.metadata.get("rerank_score"),
                    "rrf_score": d.metadata.get("rrf_score"),
                    "content": d.page_content,
                    "language": d.metadata.get("language")
                }
                for d in context_metadata.get("documents", [])
            ]
        })
        
        # Force a rerun to immediately render the new message into the persistent 
        # conversation history loop (which draws the follow-up suggestion buttons!)
        st.rerun()

# ─── Final UI Updates ────────────────────────────────────────────────────────
mem_turns = len([m for m in st.session_state.messages if m["role"] == "user"])
if mem_turns > 0:
    memory_placeholder.markdown(f'<span class="memory-pill"> {mem_turns} turn{"s" if mem_turns != 1 else ""} in memory (last 5 used)</span>', unsafe_allow_html=True)
else:
    memory_placeholder.markdown('<span style="font-size:0.72rem; color:#475569;">No conversation history yet.</span>', unsafe_allow_html=True)
 
