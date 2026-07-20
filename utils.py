"""
AuraWrite AI - Utility Helpers
Session state initialization, word counts, download helpers.
"""

import streamlit as st
from datetime import datetime

from db import get_library_items, save_library_item, delete_library_item


def init_session_state():
    """Initialize all session state variables on first load."""
    saved_library = []
    try:
        saved_library = get_library_items()
    except Exception:
        saved_library = []

    defaults = {
        "library": saved_library,
        "total_words": sum(item.get("word_count", 0) for item in saved_library),
        "api_calls": 0,
        "chat_history": [],
        "blog_content": "",
        "social_content": "",
        "active_platform": "twitter",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def count_words(text: str) -> int:
    """Count words in a string."""
    if not text:
        return 0
    return len(text.strip().split())


def save_to_library(title: str, content: str, content_type: str, category: str):
    """Save a generated item to the session library."""
    wc = count_words(content)
    item = {
        "id": f"item_{int(datetime.now().timestamp() * 1000)}",
        "title": title or "Untitled",
        "content": content,
        "type": content_type,
        "category": category,
        "date": datetime.now().strftime("%b %d, %Y %I:%M %p"),
        "word_count": wc,
        "timestamp": int(datetime.now().timestamp()),
    }
    st.session_state.library.insert(0, item)
    st.session_state.total_words += wc
    st.session_state.api_calls += 1

    try:
        save_library_item(item)
    except Exception:
        pass

    return item


def delete_from_library(item_id: str):
    """Remove an item from the library by ID."""
    st.session_state.library = [
        i for i in st.session_state.library if i["id"] != item_id
    ]
    try:
        delete_library_item(item_id)
    except Exception:
        pass


def get_download_content(content: str, fmt: str, title: str = "content"):
    """Prepare content for download in the given format."""
    if fmt == "md":
        return content, "text/markdown", f"{title}.md"
    elif fmt == "html":
        html = f"""<!DOCTYPE html><html><head><title>{title}</title>
<style>body{{font-family:system-ui,sans-serif;line-height:1.6;max-width:800px;margin:40px auto;padding:0 20px;color:#333;}}</style>
</head><body>{content}</body></html>"""
        return html, "text/html", f"{title}.html"
    else:
        return content, "text/plain", f"{title}.txt"
