"""
AuraWrite AI - Streamlit Content Generator Dashboard
Premium dark glassmorphism UI for AI-powered blog & social media writing.
"""

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

import streamlit as st
from db import get_mongo_client
from generators import generate_blog, generate_social, chat_assistant, is_api_available, get_last_api_error, configure_api_key
from utils import init_session_state, count_words, save_to_library, delete_from_library

# =========================================================================
#  PAGE CONFIG
# =========================================================================
st.set_page_config(
    page_title="AuraWrite AI | Content Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

# =========================================================================
#  CUSTOM CSS — preserving original dark glassmorphism palette
# =========================================================================
st.markdown("""
<style>
    /* ---- Import Google Fonts ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* ---- Root Color Tokens (same as original) ---- */
    :root {
        --bg-darker: #06070b;
        --bg-dark: #0a0c16;
        --bg-card: rgba(15, 17, 28, 0.65);
        --bg-card-hover: rgba(22, 25, 41, 0.8);
        --border-glass: rgba(255, 255, 255, 0.07);
        --border-glass-focus: rgba(255, 255, 255, 0.15);
        --primary: #6366f1;
        --primary-glow: rgba(99, 102, 241, 0.35);
        --primary-dark: #4f46e5;
        --secondary: #a855f7;
        --secondary-glow: rgba(168, 85, 247, 0.35);
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --text-white: #ffffff;
        --text-main: #cbd5e1;
        --text-muted: #64748b;
    }

    /* ---- Global Body ---- */
    .stApp {
        background-color: var(--bg-darker) !important;
        color: var(--text-main);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* ---- Background Glow Blobs ---- */
    .stApp::before {
        content: "";
        position: fixed;
        width: 450px; height: 450px;
        background: radial-gradient(circle, rgba(99,102,241,0.45) 0%, transparent 70%);
        top: -10%; left: -10%;
        border-radius: 50%;
        filter: blur(120px);
        z-index: 0;
        pointer-events: none;
    }
    .stApp::after {
        content: "";
        position: fixed;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(168,85,247,0.45) 0%, transparent 70%);
        bottom: -10%; right: -10%;
        border-radius: 50%;
        filter: blur(120px);
        z-index: 0;
        pointer-events: none;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background-color: rgba(6, 7, 12, 0.92) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Outfit', sans-serif;
        color: var(--text-white);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-main) !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: var(--text-white) !important;
    }

    /* ---- Main Content Headers ---- */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-white) !important;
    }
    p, li, span, div {
        color: var(--text-main);
    }

    /* ---- Glass Card Styling ---- */
    div[data-testid="stMetric"],
    div[data-testid="stExpander"],
    .glass-card {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(16px);
        padding: 6px;
    }

    /* ---- Metric Cards ---- */
    div[data-testid="stMetric"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: var(--border-glass-focus) !important;
    }
    div[data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        text-transform: uppercase;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-white) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }

    /* ---- Input & Textarea Styling ---- */
    .stTextInput input, .stTextArea textarea, .stSelectbox select,
    div[data-baseweb="select"] {
        background-color: rgba(255,255,255,0.92) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        color: #000 !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder,
    .stSelectbox select::placeholder {
        color: #444 !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 10px var(--primary-glow) !important;
    }

    /* ---- Labels ---- */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stSlider label, .stMultiSelect label, .stRadio label {
        color: var(--text-white) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.2);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #0891b2 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid var(--border-glass);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--text-muted);
        font-weight: 600;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.06) !important;
        color: var(--text-white) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--primary) !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ---- Chat Messages ---- */
    div[data-testid="stChatMessage"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 16px !important;
    }

    /* ---- Expander ---- */
    div[data-testid="stExpander"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 16px !important;
    }
    div[data-testid="stExpander"] summary {
        color: var(--text-white) !important;
        font-weight: 600;
    }

    /* ---- Dividers ---- */
    hr {
        border-color: var(--border-glass) !important;
    }

    /* ---- Status Badge Styles ---- */
    .status-badge-active {
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
        color: #10b981; padding: 6px 14px; border-radius: 20px;
        font-size: 13px; font-weight: 600;
    }
    .status-badge-active::before {
        content: ""; width: 8px; height: 8px; border-radius: 50%;
        background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.6);
        animation: pulse-dot 2s infinite;
    }
    .status-badge-sim {
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3);
        color: #f59e0b; padding: 6px 14px; border-radius: 20px;
        font-size: 13px; font-weight: 600;
    }
    .status-badge-sim::before {
        content: ""; width: 8px; height: 8px; border-radius: 50%;
        background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.6);
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0% { transform: scale(0.95); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.5; }
    }

    /* ---- Welcome Banner ---- */
    .welcome-banner {
        background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.05) 100%);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
    }

    /* ---- Library Cards ---- */
    .library-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        transition: all 0.2s ease;
        margin-bottom: 12px;
    }
    .library-card:hover {
        border-color: var(--border-glass-focus);
    }

    /* ---- Platform Badge Colors ---- */
    .badge-purple {
        background: rgba(168,85,247,0.15); border: 1px solid rgba(168,85,247,0.3);
        color: #a855f7; padding: 4px 12px; border-radius: 12px;
        font-size: 11px; font-weight: 600; text-transform: uppercase;
    }
    .badge-cyan {
        background: rgba(6,182,212,0.15); border: 1px solid rgba(6,182,212,0.3);
        color: #06b6d4; padding: 4px 12px; border-radius: 12px;
        font-size: 11px; font-weight: 600; text-transform: uppercase;
    }

    /* ---- Logo Styling ---- */
    .logo-text {
        font-family: 'Outfit', sans-serif;
        font-size: 26px; font-weight: 700; letter-spacing: -0.5px;
        color: var(--text-white);
    }
    .logo-gradient {
        background: linear-gradient(135deg, #a855f7 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }

    /* ---- Hide Streamlit Default UI ---- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background-color: rgba(6,7,12,0.4) !important;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border-glass);
    }

    /* ---- Scrollbar ---- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)


# =========================================================================
#  SIDEBAR
# =========================================================================
with st.sidebar:
    st.markdown('<span class="logo-text">✨ AuraWrite <span class="logo-gradient">AI</span></span>', unsafe_allow_html=True)
    st.caption("AI Content Generator Dashboard")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📝 Blog Generator", "📣 Social Creator", "📚 Content Library", "⚙️ Settings"],
        label_visibility="collapsed",
    )

    st.divider()

    # API Status Widget
    if is_api_available():
        st.markdown('<div class="status-badge-active">Gemini API Active</div>', unsafe_allow_html=True)
        st.caption("Model: Gemini 2.0")
    else:
        st.markdown('<div class="status-badge-sim">Simulation Mode</div>', unsafe_allow_html=True)
        st.caption("Add API key in Settings")

    st.divider()

    # Chat Assistant in Sidebar
    st.markdown("#### 💬 Aura Assistant")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="✨" if msg["role"] == "assistant" else "👤"):
            st.write(msg["content"])

    if chat_input := st.chat_input("Ask Aura anything...", key="sidebar_chat"):
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        with st.chat_message("user", avatar="👤"):
            st.write(chat_input)
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Thinking..."):
                response, mode = chat_assistant(chat_input, st.session_state.chat_history)
            st.write(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()


# =========================================================================
#  PAGES
# =========================================================================

# ----- DASHBOARD -----
if page == "🏠 Dashboard":
    st.markdown('<div class="welcome-banner"><h1>Welcome back, Creator! 🚀</h1><p style="color:#cbd5e1;font-size:15px;max-width:600px;">What spectacular pieces of content are we crafting today? Choose a tool from the sidebar or talk to your AI assistant.</p></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Words Generated", f"{st.session_state.total_words:,}")
    with col2:
        st.metric("Saved Items", f"{len(st.session_state.library):,}")
    with col3:
        st.metric("AI Generations", f"{st.session_state.api_calls:,}")

    st.divider()

    col_tools, col_recent = st.columns([1, 1])

    with col_tools:
        st.markdown("### ⚡ Quick Actions")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 Write Blog Post", use_container_width=True):
                st.session_state["_nav"] = "📝 Blog Generator"
                st.rerun()
            if st.button("💼 LinkedIn Post", use_container_width=True):
                st.session_state.active_platform = "linkedin"
                st.session_state["_nav"] = "📣 Social Creator"
                st.rerun()
        with c2:
            if st.button("🐦 Twitter Thread", use_container_width=True):
                st.session_state.active_platform = "twitter"
                st.session_state["_nav"] = "📣 Social Creator"
                st.rerun()
            if st.button("📸 Instagram Caption", use_container_width=True):
                st.session_state.active_platform = "instagram"
                st.session_state["_nav"] = "📣 Social Creator"
                st.rerun()

    with col_recent:
        st.markdown("### 📄 Recent Generations")
        if st.session_state.library:
            for item in st.session_state.library[:4]:
                badge_class = "badge-purple" if item["type"] == "blog" else "badge-cyan"
                st.markdown(f"""<div class="library-card">
                    <span class="{badge_class}">{item['category']}</span>
                    <span style="color:var(--text-muted);font-size:12px;float:right;">{item['word_count']} words</span>
                    <h4 style="margin:8px 0 4px;font-size:14px;">{item['title']}</h4>
                    <p style="font-size:12px;color:var(--text-muted);">{item['date']}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No content generated yet. Use the tools above to create your first draft! ✨")


# ----- BLOG GENERATOR -----
elif page == "📝 Blog Generator":
    st.markdown("## 📝 Blog Writer")
    st.caption("Generate high-quality, SEO-optimized long-form blog posts")
    st.divider()

    col_form, col_preview = st.columns([2, 3])

    with col_form:
        with st.container(border=True):
            topic = st.text_input("Topic / Main Idea", placeholder="e.g., The Future of Machine Learning in Healthcare")
            keywords_raw = st.text_input("Keywords (comma-separated)", placeholder="e.g., SEO, Artificial Intelligence, Growth")
            keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()] if keywords_raw else []

            c1, c2 = st.columns(2)
            with c1:
                tone = st.selectbox("Tone of Voice", [
                    "Informative & Clear", "Professional & Data-driven",
                    "Casual & Conversational", "Inspirational & Thoughtful",
                    "Playful & Witty", "Authoritative & Decisive"
                ])
            with c2:
                word_count = st.slider("Approx. Word Count", 400, 1500, 800, 100)

            sections = st.multiselect("Outline Sections", [
                "Introduction", "Industry Context", "Core Strategies",
                "Code Snippet / Example", "Case Study", "Conclusion & CTA"
            ], default=["Introduction", "Core Strategies", "Conclusion & CTA"])

            generate_clicked = st.button("✨ Generate Full Blog Post", use_container_width=True, type="primary")

    with col_preview:
        if generate_clicked and topic:
            with st.spinner("AI is writing your article..."):
                content, mode = generate_blog(topic, keywords, tone, word_count, sections)
                st.session_state.blog_content = content
                st.session_state.api_calls += 1
                st.session_state.total_words += count_words(content)
            if mode == "simulation":
                if is_api_available():
                    st.warning("Simulation fallback used. The API key is configured, but the Gemini request failed. Check the key, model, and billing/quota details.")
                    if get_last_api_error():
                        st.info(f"API error: {get_last_api_error()}")
                else:
                    st.warning("Generated in Simulation Mode (no API key configured)")
            else:
                st.success("Blog generated successfully via Gemini API!")

        if st.session_state.blog_content:
            wc = count_words(st.session_state.blog_content)
            st.markdown(f'<span class="badge-purple">Preview Mode</span> &nbsp; <span style="color:var(--text-muted);font-size:12px;">{wc} words</span>', unsafe_allow_html=True)

            tab_preview, tab_edit = st.tabs(["👁️ Preview", "✏️ Editor"])
            with tab_preview:
                st.markdown(st.session_state.blog_content)
            with tab_edit:
                edited = st.text_area("Edit raw markdown", st.session_state.blog_content, height=400, label_visibility="collapsed")
                if edited != st.session_state.blog_content:
                    st.session_state.blog_content = edited

            # Action buttons
            bcol1, bcol2, bcol3, bcol4 = st.columns(4)
            with bcol1:
                if st.button("📋 Copy", key="blog_copy", use_container_width=True):
                    st.code(st.session_state.blog_content, language=None)
                    st.toast("Content displayed for copying!", icon="📋")
            with bcol2:
                if st.button("💾 Save to Library", key="blog_save", use_container_width=True):
                    save_to_library(topic or "Untitled Blog", st.session_state.blog_content, "blog", "Blog Post")
                    st.toast("Saved to library!", icon="✅")
            with bcol3:
                st.download_button("⬇️ .md", st.session_state.blog_content, file_name=f"{topic or 'blog'}.md", mime="text/markdown", use_container_width=True)
            with bcol4:
                st.download_button("⬇️ .txt", st.session_state.blog_content, file_name=f"{topic or 'blog'}.txt", mime="text/plain", use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:80px 20px;color:var(--text-muted);">
                <div style="font-size:48px;margin-bottom:16px;opacity:0.3;">📝</div>
                <h4 style="color:var(--text-white);margin-bottom:8px;">Blog Content Workspace</h4>
                <p style="max-width:320px;margin:0 auto;font-size:13px;line-height:1.5;">Fill out the settings on the left and hit generate to draft a beautifully structured, SEO-optimized blog post.</p>
            </div>
            """, unsafe_allow_html=True)


# ----- SOCIAL CREATOR -----
elif page == "📣 Social Creator":
    st.markdown("## 📣 Social Media Creator")
    st.caption("Create platform-optimized short-form posts")
    st.divider()

    col_form, col_preview = st.columns([2, 3])

    with col_form:
        with st.container(border=True):
            platform = st.radio(
                "Platform",
                ["🐦 Twitter/X", "💼 LinkedIn", "📸 Instagram", "📘 Facebook"],
                horizontal=True,
                index=["twitter", "linkedin", "instagram", "facebook"].index(st.session_state.active_platform) if st.session_state.active_platform in ["twitter", "linkedin", "instagram", "facebook"] else 0,
            )
            platform_map = {"🐦 Twitter/X": "twitter", "💼 LinkedIn": "linkedin", "📸 Instagram": "instagram", "📘 Facebook": "facebook"}
            active_platform = platform_map[platform]
            st.session_state.active_platform = active_platform

            topic = st.text_area("Topic / Hook Description", placeholder="What is this post going to be about?", height=100)
            keywords_raw = st.text_input("Keywords (comma-separated)", placeholder="e.g., motivation, productivity", key="social_kw")
            keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()] if keywords_raw else []

            c1, c2 = st.columns(2)
            with c1:
                tone = st.selectbox("Tone", ["Informative", "Professional", "Casual / Direct", "Playful / Witty", "Inspiring / Visionary"], key="social_tone")
            with c2:
                instructions = st.text_input("Style Guidelines (optional)", placeholder="e.g., use emojis, be humble...")

            generate_clicked = st.button("✨ Compose Copy", use_container_width=True, type="primary", key="gen_social")

    with col_preview:
        limits = {"twitter": 280, "linkedin": 3000, "instagram": 2200, "facebook": 5000}

        if generate_clicked and topic:
            with st.spinner("AI is composing copy..."):
                content, mode = generate_social(active_platform, topic, tone, keywords, instructions)
                st.session_state.social_content = content
                st.session_state.api_calls += 1
                st.session_state.total_words += count_words(content)
            if mode == "simulation":
                if is_api_available():
                    st.warning("Simulation fallback used. The API key is configured, but the Gemini request failed. Check the key, model, and billing/quota details.")
                    if get_last_api_error():
                        st.info(f"API error: {get_last_api_error()}")
                else:
                    st.warning("Composed in Simulation Mode (no API key configured)")
            else:
                st.success("Social copy composed via Gemini API!")

        if st.session_state.social_content:
            char_count = len(st.session_state.social_content)
            limit = limits.get(active_platform, 5000)
            color = "#ef4444" if char_count > limit else ("#f59e0b" if char_count > limit * 0.9 else "var(--text-muted)")

            badge_text = {"twitter": "Twitter Thread", "linkedin": "LinkedIn Post", "instagram": "Instagram Caption", "facebook": "Facebook Post"}
            st.markdown(f'<span class="badge-cyan">{badge_text.get(active_platform, "Social Post")}</span> &nbsp; <span style="color:{color};font-size:12px;">{char_count} / {limit} chars</span>', unsafe_allow_html=True)

            tab_preview, tab_edit = st.tabs(["👁️ Preview", "✏️ Editor"])
            with tab_preview:
                st.text(st.session_state.social_content)
            with tab_edit:
                edited = st.text_area("Edit copy", st.session_state.social_content, height=300, label_visibility="collapsed", key="social_edit")
                if edited != st.session_state.social_content:
                    st.session_state.social_content = edited

            scol1, scol2, scol3 = st.columns(3)
            with scol1:
                if st.button("📋 Copy", key="social_copy", use_container_width=True):
                    st.code(st.session_state.social_content, language=None)
                    st.toast("Content displayed for copying!", icon="📋")
            with scol2:
                category = badge_text.get(active_platform, "Social Copy")
                if st.button("💾 Save to Library", key="social_save", use_container_width=True):
                    save_to_library(f"Draft: {topic[:40]}...", st.session_state.social_content, "social", category)
                    st.toast("Saved to library!", icon="✅")
            with scol3:
                st.download_button("⬇️ .txt", st.session_state.social_content, file_name="social_post.txt", mime="text/plain", use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:80px 20px;color:var(--text-muted);">
                <div style="font-size:48px;margin-bottom:16px;opacity:0.3;">📣</div>
                <h4 style="color:var(--text-white);margin-bottom:8px;">Social Media Feed Preview</h4>
                <p style="max-width:320px;margin:0 auto;font-size:13px;line-height:1.5;">Select your platform, fill out key concepts, and compose. Output will adapt to platform character limits and conventions.</p>
            </div>
            """, unsafe_allow_html=True)


# ----- CONTENT LIBRARY -----
elif page == "📚 Content Library":
    st.markdown("## 📚 Your Content Library")
    st.caption("Manage, edit, export, and search your saved AI creations.")
    st.divider()

    # Filters
    fcol1, fcol2 = st.columns([3, 1])
    with fcol1:
        search = st.text_input("🔍 Search saved posts...", label_visibility="collapsed", placeholder="Search saved posts...")
    with fcol2:
        category_filter = st.selectbox("Filter", ["All Content", "Blog Posts", "Social Copy"], label_visibility="collapsed")

    # Filter logic
    items = st.session_state.library
    if search:
        items = [i for i in items if search.lower() in i["title"].lower() or search.lower() in i["content"].lower()]
    if category_filter == "Blog Posts":
        items = [i for i in items if i["type"] == "blog"]
    elif category_filter == "Social Copy":
        items = [i for i in items if i["type"] == "social"]

    if not items:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:var(--text-muted);">
            <div style="font-size:48px;margin-bottom:16px;opacity:0.3;">📚</div>
            <h4 style="color:var(--text-white);">No matching drafts found</h4>
            <p style="font-size:13px;">Generate and save content to fill your vault!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display as card grid
        cols = st.columns(2)
        for idx, item in enumerate(items):
            with cols[idx % 2]:
                badge_class = "badge-purple" if item["type"] == "blog" else "badge-cyan"
                preview = item["content"][:150].replace("\n", " ") + "..."

                st.markdown(f"""<div class="library-card">
                    <span class="{badge_class}">{item['category']}</span>
                    <span style="color:var(--text-muted);font-size:11px;float:right;">{item['word_count']} words • {item['date']}</span>
                    <h4 style="margin:10px 0 6px;font-size:15px;">{item['title']}</h4>
                    <p style="font-size:13px;color:var(--text-muted);line-height:1.5;">{preview}</p>
                </div>""", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("👁️ View", key=f"view_{item['id']}", use_container_width=True):
                        st.session_state[f"expand_{item['id']}"] = True
                with c2:
                    st.download_button("⬇️", item["content"], file_name=f"{item['title'][:20]}.txt", mime="text/plain", key=f"dl_{item['id']}", use_container_width=True)
                with c3:
                    if st.button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                        delete_from_library(item["id"])
                        st.rerun()

                # Expandable view
                if st.session_state.get(f"expand_{item['id']}", False):
                    with st.expander(f"📄 {item['title']}", expanded=True):
                        if item["type"] == "blog":
                            st.markdown(item["content"])
                        else:
                            st.text(item["content"])
                        if st.button("Close", key=f"close_{item['id']}"):
                            st.session_state[f"expand_{item['id']}"] = False
                            st.rerun()


# ----- SETTINGS -----
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ System Configuration")
    st.caption("Manage API credentials and customize your content workspace.")
    st.divider()

    with st.container(border=True):
        st.markdown("### 🔑 Google Gemini API Configuration")
        st.markdown("Connect to Google Gemini models for context-aware, high-quality AI generations. Get a free API key at [Google AI Studio](https://aistudio.google.com/).")

        api_key_input = st.text_input("API Key", type="password", placeholder="AIzaSy...", key="settings_key")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 Test Connection", use_container_width=True):
                if api_key_input:
                    with st.spinner("Testing connection..."):
                        success = configure_api_key(api_key_input)
                    if success:
                        st.success("✅ Connection successful! Gemini API is active.")
                    else:
                        st.error("❌ Connection failed. Please check your API key.")
                else:
                    st.warning("Please enter an API key first.")
        with c2:
            if st.button("💾 Save Settings", use_container_width=True, type="primary"):
                if api_key_input:
                    success = configure_api_key(api_key_input)
                    if success:
                        st.success("Settings saved! API key written to .env file.")
                        st.rerun()
                    else:
                        st.error("Failed to save settings.")
                else:
                    st.info("No key entered. Running in Simulation Mode.")

    st.divider()

    last_error = get_last_api_error()
    if last_error:
        st.error(f"Last Gemini API error: {last_error}")

    with st.container(border=True):
        st.markdown("### 🎨 Content Preferences")
        st.toggle("Include rich emojis in social drafts", value=True, key="pref_emojis")
        st.toggle("Auto-highlight code blocks in blogs", value=True, key="pref_code")

    st.divider()

    with st.container(border=True):
        st.markdown("### 📊 System Info")
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**API Status:** {'🟢 Active' if is_api_available() else '🟡 Simulation'}")
            st.markdown(f"**Model:** {'Gemini 2.0' if is_api_available() else 'Mock Compiler'}")
        with info_col2:
            st.markdown(f"**Items in Library:** {len(st.session_state.library)}")
            st.markdown(f"**Database:** {'🟢 Connected' if get_mongo_client() else '🟡 Not connected'}")
            st.markdown(f"**Total Words Generated:** {st.session_state.total_words:,}")
