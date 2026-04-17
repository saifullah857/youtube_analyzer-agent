from textwrap import dedent
import os
import re
import hashlib
import time
import functools
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.youtube import YouTubeTools

load_dotenv()

# ─── In-memory response cache ────────────────────────────────────────────────
_REPORT_CACHE: dict[str, dict] = {}


def _cache_key(url: str) -> str:
    return hashlib.md5(url.strip().encode()).hexdigest()


def get_cached_report(url: str) -> dict | None:
    key = _cache_key(url)
    entry = _REPORT_CACHE.get(key)
    if entry and (time.time() - entry["ts"]) < 3600:   # 1-hour TTL
        return entry
    return None


def cache_report(url: str, content: str, metadata: dict) -> None:
    _REPORT_CACHE[_cache_key(url)] = {
        "content": content,
        "metadata": metadata,
        "ts": time.time(),
    }


# ─── Timestamp Utilities ──────────────────────────────────────────────────────
def extract_timestamps(text: str) -> list[dict]:
    """
    Parse all [MM:SS] or [HH:MM:SS] markers the agent writes into the report.
    Returns a list of dicts: {label, raw, seconds, description}
    """
    pattern = re.compile(
        r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*[-–]?\s*([^\n\[]+)?",
        re.MULTILINE,
    )
    results = []
    for match in pattern.finditer(text):
        raw = match.group(1)
        desc = (match.group(2) or "").strip(" -–|")
        parts = raw.split(":")
        if len(parts) == 2:
            seconds = int(parts[0]) * 60 + int(parts[1])
        else:
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        results.append({"label": raw, "seconds": seconds, "description": desc})
    return results


def youtube_timestamp_url(video_id: str, seconds: int) -> str:
    return f"https://www.youtube.com/watch?v={video_id}&t={seconds}s"


# ─── Agent Builder ────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def build_youtube_agent() -> Agent:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )

    return Agent(
        name="YouTube Intelligence Pro",
        model=Groq(
            id="llama-3.3-70b-versatile",
            api_key=api_key,
            # Slightly higher temp for richer prose; keep low for factual
            temperature=0.35,
            max_tokens=4096,
        ),
        tools=[YouTubeTools()],
        instructions=dedent("""\
            You are an Elite Video Intelligence Agent built by IntelStream AI.
            Your mission: transform raw YouTube transcripts into world-class,
            investor-ready intelligence reports.

            ══════════════════════════════════════════════
            📐 REPORT STRUCTURE — FOLLOW EXACTLY
            ══════════════════════════════════════════════

            ### SECTION 0 — HEADER
            # 📺 [Exact Video Title]
            ## *By [Channel Name]*
            ---

            ### SECTION 1 — VIDEO SNAPSHOT
            > ⏱️ **Duration:** [X min] &nbsp;|&nbsp; 🎯 **Category:** [Niche]
            > 📊 **Views:** [count or "N/A"] &nbsp;|&nbsp; 📅 **Published:** [date or "N/A"]
            > 💡 **Core Value:** [One crisp sentence — what does the viewer walk away with?]

            ---

            ### SECTION 2 — TIMESTAMPED CHAPTER TIMELINE
            This is the MOST IMPORTANT section. For EVERY distinct topic or segment:
            - Use this EXACT format on its own line:
              [MM:SS] - **[Segment Title]** — [2-3 sentence punchy summary of what happens]
            - Use real timestamps from the transcript data.
            - Include 6–12 timestamps minimum.
            - Prefix segment titles with context icons:
              📚 Theory | 🛠️ Tutorial | 🎙️ Opinion | ⚠️ Warning | 💡 Key Insight | 🔥 Highlight

            ---

            ### SECTION 3 — INTELLIGENCE TABLE
            A clean professional table:
            | # | 🕒 Timestamp | 🚀 Topic | 💡 Core Insight | 🎯 Takeaway |
            |---|:---|:---|:---|:---|

            ---

            ### SECTION 4 — DEEP INTELLIGENCE BRIEF
            **🧠 Primary Concepts** (top 3–5 bold headers with bullet explanations)

            **⚡ Actionable Blueprint** — Numbered steps the reader can execute TODAY.

            **🔗 Resource Vault** — All tools, links, products, books mentioned.

            **⚠️ Watch-Outs** — Risks, caveats, or counterpoints raised in the video.

            ---

            ### SECTION 5 — ANALYST VERDICT
            A powerful 2–3 sentence executive summary rating the video's value:
            - **Clarity:** ⭐⭐⭐⭐⭐ (out of 5) [brief justification]
            - **Actionability:** ⭐⭐⭐⭐⭐ [brief justification]
            - **Audience Fit:** [Who benefits most from this video?]

            ══════════════════════════════════════════════
            🎨 PRESENTATION RULES
            ══════════════════════════════════════════════
            - NO walls of text. Max 3 lines before converting to bullets.
            - Use --- as visual separators between all sections.
            - Timestamps MUST follow [MM:SS] format precisely — this is parsed programmatically.
            - Be analytical, precise, and expert-level. No filler.
            - Always extract the actual video title from tool output — never guess.
        """),
        add_datetime_to_context=True,
        markdown=True,
    )