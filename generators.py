"""
AuraWrite AI - Content Generators Module
Handles Gemini API integration and mock/simulation fallbacks.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(DOTENV_PATH, override=True)

# --- Gemini API Setup ---
_api_available = False
_genai = None
_last_api_error = None
DEFAULT_GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')

def _clean_api_key(api_key: str) -> str:
    """Return a valid API key or an empty string for missing/placeholder values."""
    if not api_key:
        return ""
    key = api_key.strip().strip('"').strip("'")
    if not key:
        return ""
    normalized = key.upper()
    placeholders = ["REDACTED", "PLACEHOLDER", "YOUR_API_KEY", "INSERT_API_KEY", "CHANGE_ME"]
    if any(marker in normalized for marker in placeholders):
        return ""
    return key


def _init_genai():
    """Lazily initialize the Gemini API."""
    global _api_available, _genai, _last_api_error
    try:
        import google.generativeai as genai
        _genai = genai
        api_key = _clean_api_key(os.getenv('GEMINI_API_KEY', ''))
        if api_key:
            genai.configure(api_key=api_key)
            _api_available = True
            _last_api_error = None
            logger.info("Gemini API configured successfully.")
        else:
            _api_available = False
            _last_api_error = "GEMINI_API_KEY missing or placeholder value detected."
            logger.warning("GEMINI_API_KEY not found or placeholder value used. Running in Simulation Mode.")
    except Exception as e:
        _api_available = False
        _last_api_error = str(e)
        logger.error(f"Error configuring Gemini API: {e}")

_init_genai()


def is_api_available():
    return _api_available


def get_last_api_error():
    return _last_api_error


def configure_api_key(key: str):
    """Dynamically set a new API key."""
    global _api_available, _last_api_error
    cleaned_key = _clean_api_key(key)
    if not cleaned_key:
        _api_available = False
        _last_api_error = "Invalid API key provided."
        return False
    try:
        os.environ['GEMINI_API_KEY'] = cleaned_key
        if _genai is None:
            _init_genai()
        else:
            _genai.configure(api_key=cleaned_key)
        _api_available = True
        _last_api_error = None

        # Persist to .env
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        lines = []
        key_written = False
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith('GEMINI_API_KEY='):
                    lines[i] = f"GEMINI_API_KEY={cleaned_key}\n"
                    key_written = True
                    break
        if not key_written:
            lines.append(f"GEMINI_API_KEY={cleaned_key}\n")
        with open(env_path, 'w') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        _api_available = False
        _last_api_error = str(e)
        logger.error(f"Error setting API key: {e}")
        return False


# =========================================================================
#  BLOG GENERATORS
# =========================================================================

def generate_blog(topic, keywords, tone, word_count, sections):
    """Generate a blog post using Gemini API or mock fallback."""
    if _api_available:
        try:
            return _generate_blog_api(topic, keywords, tone, word_count, sections), "api"
        except Exception as e:
            global _last_api_error
            _last_api_error = str(e)
            logger.error(f"Gemini blog error: {e}")
            return _generate_blog_mock(topic, keywords, tone, word_count), "simulation"
    return _generate_blog_mock(topic, keywords, tone, word_count), "simulation"


def _generate_blog_api(topic, keywords, tone, word_count, sections):
    kw_str = ", ".join(keywords) if keywords else "general"
    sec_str = ", ".join(sections) if sections else "Introduction, Body, Conclusion"
    prompt = f"""You are an expert content writer and SEO specialist.
Write a highly engaging, professional blog post in Markdown format.

Topic: {topic}
Tone of Voice: {tone}
Target Word Count: ~{word_count} words
Keywords to include naturally: {kw_str}
Outline / Sections to include: {sec_str}

Format guidelines:
- Use clean Markdown syntax.
- Include a catchy, SEO-friendly H1 title.
- Use H2 and H3 subheadings for sections.
- Use bullet points, bold text, and code snippets if applicable to enhance readability.
- Write a compelling introduction and a strong conclusion with a call to action.
- DO NOT wrap the output in markdown block codes like ```markdown ... ```. Output the raw markdown text directly.
"""
    model = _genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text


def _generate_blog_mock(topic, keywords, tone, word_count):
    kw_str = ", ".join(keywords) if keywords else "growth, strategy"
    return f"""# The Ultimate Guide to {topic}

In today's fast-paced digital landscape, mastering **{topic}** has transitioned from a nice-to-have advantage to an absolute necessity. Whether you are a seasoned professional or just beginning your journey, understanding the core dynamics of this field can unlock unprecedented growth.

This article explores the foundational principles of {topic}, highlights key strategies to leverage, and guides you through integrating elements like **{kw_str}** to maximize your impact.

---

## Why {topic} Matters Now More Than Ever

Every successful venture is built on a series of calculated decisions and strategic tools. When it comes to {topic}, the numbers speak for themselves. Recent industry analyses indicate that organizations prioritizing this area observe a significant increase in efficiency, user satisfaction, and long-term retention.

By adopting a **{tone}** approach, you position yourself as a forward-thinking player. It's not just about keeping pace with trends; it's about actively setting them.

### Key Benefits Include:
1. **Enhanced Authority:** Solidifies your brand's presence in a crowded market.
2. **Optimized Performance:** Streamlines operations, allowing you to focus on high-leverage activities.
3. **Deeper Engagement:** Fosters a stronger connection with your target audience by addressing their pain points directly.

---

## Implementing Core Strategies

To truly succeed with {topic}, you must look beyond basic concepts and focus on advanced integration. Here are three actionable strategies you can implement starting today:

### 1. Leverage High-Value Keywords
Incorporating relevant terms like **{kw_str}** isn't just about search engines; it's about matching the search intent of your target demographic. Ensure these terms are woven naturally into headings, body text, and image alt text.

### 2. Tailor Your Communication Style
The way you communicate determines how your message is received. Since we are aiming for a **{tone}** tone, ensure your vocabulary matches the expectation of your readers. Avoid unnecessary jargon if writing casually, or lean into data-driven insights if adopting a highly professional angle.

### 3. Measure, Refine, and Scale
Never let your strategy stagnate. Establish key performance indicators (KPIs) early. Monitor metrics such as time-on-page, click-through rates, and social shares. Use this data to continuously refine your approach.

---

## Final Thoughts & Next Steps

Mastering **{topic}** is a continuous journey rather than a destination. By staying adaptable, prioritizing user value, and consistently optimizing for key themes like **{kw_str}**, you set the stage for sustained success.

Now is the time to act. Review your current assets, apply these strategies, and watch your engagement metrics soar.

**What is your biggest challenge with {topic}? Let us know in the comments below!**
"""


# =========================================================================
#  SOCIAL MEDIA GENERATORS
# =========================================================================

def generate_social(platform, topic, tone, keywords, instructions=""):
    """Generate social media copy using Gemini API or mock fallback."""
    if _api_available:
        try:
            return _generate_social_api(platform, topic, tone, keywords, instructions), "api"
        except Exception as e:
            global _last_api_error
            _last_api_error = str(e)
            logger.error(f"Gemini social error: {e}")
            return _generate_social_mock(platform, topic, tone, keywords), "simulation"
    return _generate_social_mock(platform, topic, tone, keywords), "simulation"


def _generate_social_api(platform, topic, tone, keywords, instructions):
    kw_str = ", ".join(keywords) if keywords else ""
    platform_rules = {
        'twitter': "Write a Twitter thread (3-5 tweets). Keep each tweet under 280 characters. Number them as 1/, 2/ etc. Include a hook in the first tweet.",
        'linkedin': "Write an engaging, professional LinkedIn post. Use line breaks for readability, start with a strong hook, include 3 bullet points, and end with a question to prompt discussion.",
        'instagram': "Write a caption for Instagram. Make it punchy, use emojis, and end with a relevant list of hashtags.",
        'facebook': "Write an engaging post suitable for Facebook or Threads."
    }
    prompt = f"""You are a social media copywriter.
Generate a high-performing social media post based on the following:

Platform: {platform}
Topic: {topic}
Tone of Voice: {tone}
Keywords to include (either as hashtags or naturally in text): {kw_str}
Custom instructions: {instructions}

Platform Guidelines:
{platform_rules.get(platform, platform_rules['facebook'])}

Do not include any intro like 'Here is your post:' or meta-commentary. Output the raw text of the post directly.
"""
    model = _genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text


def _generate_social_mock(platform, topic, tone, keywords):
    kw_str = " ".join([f"#{k.replace(' ', '')}" for k in keywords]) if keywords else "#growth #strategy"

    mocks = {
        'twitter': f"""🧵 **Tweet 1/4**
Unlocking the full potential of **{topic}** is easier than you think. Here's a quick thread on how to get started, stay consistent, and drive real results. 👇

🧵 **Tweet 2/4**
The secret sauce? Focus heavily on your core message and integrate key concepts like {kw_str.split()[0] if kw_str.split() else '#growth'}. A structured approach prevents audience fatigue and keeps them coming back for more.

🧵 **Tweet 3/4**
Adopt a **{tone}** voice. Keep your writing punchy, omit needless words, and always, always end with a clear value proposition. Your audience's attention is a premium; respect it.

🧵 **Tweet 4/4**
Ready to scale? Make sure to save, bookmark, and share this thread if you found it useful.

What is your #1 blocker when it comes to {topic}? Let's discuss! 🚀""",

        'linkedin': f"""Are you maximizing your results with **{topic}**?

In today's environment, execution is everything. However, many professionals struggle to bridge the gap between planning and implementation.

Here are 3 key frameworks to guide your journey:

1️⃣ **Context-First Delivery:** Align your message with current market trends.
2️⃣ **Natural Optimization:** Weave key ideas like {kw_str} organically rather than forcing them.
3️⃣ **Active Feedback Loops:** Never guess. Let data guide your revisions.

We've been adopting a **{tone}** approach to this, and the results speak for themselves: client engagement is up, and production timelines are down.

👉 What's your experience with {topic}? Have you noticed a shift in trends lately?

Let's start a conversation in the comments.

{kw_str} #ProfessionalGrowth #ContentStrategy""",

        'instagram': f"""✨ Transforming the way you approach **{topic}**! 🚀

Sometimes all it takes is a fresh perspective and a shift in strategy. By focusing on core priorities and optimizing for what truly matters, you can elevate your results overnight. 🎯

💡 Key takeaway: Always stay true to your target tone (**{tone}**) and let authenticity guide your voice.

Save this post for later inspiration! 💾

.
.
.
{kw_str} #instadaily #contentcreator #motivation #success #goals""",

        'facebook': f"""Let's talk about **{topic}**.

Whether you're looking to scale operations, improve outreach, or simply learn the ropes, having a clear roadmap is crucial.

We recently adopted a **{tone}** framework to address these exact points, focusing heavily on core drivers like {kw_str}. The feedback has been overwhelmingly positive.

What strategies are you currently using to master {topic}? Drop your thoughts or questions below—I'd love to hear what's working for you! 📣

{kw_str}"""
    }
    return mocks.get(platform, mocks['facebook'])


# =========================================================================
#  CHAT ASSISTANT
# =========================================================================

def chat_assistant(message, history=None):
    """Handle chat assistant requests."""
    if _api_available:
        try:
            return _chat_api(message, history or []), "api"
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return _chat_mock(message), "simulation"
    return _chat_mock(message), "simulation"


def _chat_api(message, history):
    model = _genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
    formatted_history = []
    for h in history:
        role = "user" if h.get("role") == "user" else "model"
        formatted_history.append({"role": role, "parts": [h.get("content", "")]})
    chat_session = model.start_chat(history=formatted_history)
    response = chat_session.send_message(message)
    return response.text


def _chat_mock(message):
    msg = message.lower()
    if "blog" in msg:
        return "Writing a great blog post starts with a solid outline. I recommend beginning with an engaging hook, dividing the body into 3 actionable sections, and closing with a strong Call to Action (CTA). Would you like me to draft an outline for a specific topic?"
    elif "twitter" in msg or "tweet" in msg or "thread" in msg:
        return "For Twitter/X, keep your hooks ultra-short (under 120 chars) to grab attention. Use threads to tell a story, and format each tweet with numbers (e.g. 1/5) so readers know it is a thread. What topic are we tweeting about today?"
    elif "linkedin" in msg:
        return "LinkedIn posts perform best when they tell a personal story or share a hard-learned lesson. Start with a contrarian hook or a statistic, use generous line breaks, and end with a question to drive comments. Let me know if you want a template!"
    elif "instagram" in msg:
        return "Instagram captions should lead with the value proposition in the first two lines before the 'more' button. Use emojis to break up text and group your hashtags at the bottom. What vibe are we aiming for?"
    elif "headline" in msg or "title" in msg:
        return "A great headline is clear, specific, and promises a benefit. For example: 'X Ways to Master Y without Z' or 'The Content Framework That Saved Us 10+ Hours'. What topic should we brainstorm headlines for?"
    elif "hello" in msg or "hi" in msg:
        return "Hello! 👋 I'm your AI Content Assistant. I can help you draft blog outlines, write social media posts, brainstorm headlines, or refine your copy. What are we creating today?"
    else:
        return f"That sounds like an interesting angle! Regarding '{message}', I suggest focusing on the target audience's pain points. Should we write a blog outline, draft some social media copy, or brainstorm headlines around this?"
