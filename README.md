# AuraWrite AI - Content Generator Dashboard

AuraWrite AI is a premium, responsive AI copywriting dashboard designed to generate search-optimized blog posts and platform-specific social media copy (Twitter/X threads, LinkedIn posts, Instagram captions, Facebook updates).

Built with **Python & Streamlit** and styled with a custom **dark glassmorphism theme**, it offers direct integration with Google's Gemini API, in-session content persistence, and a smart offline simulation mode.

---

## Key Features

*   **Dark Glassmorphic UI**: Deep obsidian aesthetic with radial glow blobs, glass-border cards, and premium typography (Outfit & Inter fonts).
*   **SEO Blog Generator**: Outline editor, keyword inputs, word-count slider, markdown preview/editor tabs, and direct file downloads (.txt, .md).
*   **Social Media Post Builder**: Platform-specific layouts with character counts:
    *   **Twitter/X**: Auto-formatted tweet threads with live character warnings.
    *   **LinkedIn**: Professional stories with hooks and discussion prompts.
    *   **Instagram**: Punchy captions with emojis and hashtag blocks.
    *   **Facebook/Threads**: Clean general announcement style.
*   **Content Library Vault**: In-session storage for content tracking, viewing, editing, downloading, and deleting.
*   **Dynamic API Settings**: Enter and save Gemini API keys directly from the UI. Keys are persisted to the `.env` file and hot-reload the active runtime.
*   **AI Chat Assistant**: Sidebar chat assistant powered by Gemini or simulation mode for brainstorming headlines, hooks, and rewrites.
*   **Persistent Content Vault**: Saved drafts are stored in MongoDB for cross-session persistence.
*   **Offline Simulation Mode**: If no Gemini API key is configured, the app falls back to a smart rule-based template compiler for instant usability.

---

## Tech Stack

*   **Framework**: Python, Streamlit
*   **AI Backend**: Google Generative AI SDK (Gemini 2.0 Flash)
*   **Styling**: Custom CSS injection (dark glassmorphism theme)
*   **Fonts**: Google Fonts (Outfit & Inter)

---

## Project Structure

```text
├── app.py              # Main Streamlit application (UI + routing + custom CSS theme)
├── generators.py       # Gemini API integration + mock/simulation fallback generators
├── utils.py            # Session state management, word counting, library helpers
├── requirements.txt    # Python dependencies (streamlit, google-generativeai, etc.)
├── .env                # Environment configuration (GEMINI_API_KEY)
└── README.md           # Project documentation (this file)
```

---

## Setup & Running Locally

### Prerequisites

*   Python 3.10 or higher installed.
*   A Gemini API Key (optional). Get one for free at the [Google AI Studio](https://aistudio.google.com/).

### Installation Steps

1.  **Navigate** to the project directory:
    ```bash
    cd summer_intern
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate      # Windows
    # source venv/bin/activate # macOS/Linux
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  *(Optional)* Add your Gemini API Key and MongoDB connection string to the `.env` file, or supply the API key later in the app's Settings page:
    ```text
    GEMINI_API_KEY=your_api_key_here
    MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.2prcygs.mongodb.net/
    MONGODB_DB=aura_write_ai
    ```

5.  **Launch the application**:
    ```bash
    streamlit run app.py
    ```

6.  **Open the interface**: Your browser will automatically open to **http://localhost:8501**.

---

## Usage Guide

1.  **Check API Status**: The sidebar shows a green badge (Gemini API Active) or yellow badge (Simulation Mode).
2.  **Generate Content**: Use "Blog Generator" or "Social Creator" pages to draft content. Fill in your topic, keywords, and tone preferences.
3.  **Chat Assistant**: Use the sidebar chat input to brainstorm headlines, copywriting hooks, or get rewrites.
4.  **Save & Manage**: Hit "Save to Library" on any draft, then navigate to "Content Library" to view, search, download, or delete your saved vault.
5.  **Configure API**: Go to "Settings" to enter your Gemini API key. Click "Test Connection" to verify, then "Save Settings" to persist it.
