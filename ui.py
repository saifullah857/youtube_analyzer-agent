import streamlit as st
import os
import time
from urllib.parse import urlparse, parse_qs
from Youtube_Analyzer import (
    build_youtube_agent,
    extract_timestamps,
    youtube_timestamp_url,
    get_cached_report,
    cache_report,
)

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IntelStream — YouTube Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "IntelStream AI · YouTube Intelligence Engine v3.0"},
)

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ── Reset & Base ─────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080810 !important;
    font-family: 'Sora', sans-serif !important;
    color: #e2e2f0 !important;
}

[data-testid="stAppViewContainer"] > .main { background: #080810 !important; }
[data-testid="stHeader"] { background: rgba(8,8,16,0.95) !important; backdrop-filter: blur(12px); border-bottom: 1px solid #1e1e30; }

/* ── Sidebar ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e30 !important;
}
[data-testid="stSidebar"] * { font-family: 'Sora', sans-serif !important; }

/* ── Typography ───────────────────────────── */
h1, h2, h3, h4, h5, h6 { font-family: 'Sora', sans-serif !important; }

/* ── Logo + Brand ─────────────────────────── */
.brand-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 24px;
    border-bottom: 1px solid #1e1e30;
    margin-bottom: 24px;
}
.brand-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #00d4aa, #0099ff);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700;
    box-shadow: 0 0 20px rgba(0,212,170,0.3);
}
.brand-name {
    font-size: 18px; font-weight: 700;
    background: linear-gradient(90deg, #00d4aa, #0099ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.3px;
}
.brand-tag { font-size: 10px; color: #5a5a78; letter-spacing: 1.5px; text-transform: uppercase; }

/* ── Nav Items ────────────────────────────── */
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 10px;
    font-size: 13px; font-weight: 500; color: #8888a8;
    cursor: pointer; margin-bottom: 4px;
    transition: all 0.2s ease;
}
.nav-item.active {
    background: rgba(0,212,170,0.08);
    color: #00d4aa;
    border: 1px solid rgba(0,212,170,0.15);
}

/* ── Status Badge ─────────────────────────── */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
    background: rgba(0,212,170,0.08);
    border: 1px solid rgba(0,212,170,0.2);
    color: #00d4aa;
}
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #00d4aa;
    box-shadow: 0 0 8px #00d4aa; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }

/* ── Hero Section ─────────────────────────── */
.hero-section {
    text-align: center;
    padding: 60px 20px 40px;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0,212,170,0.08); border: 1px solid rgba(0,212,170,0.2);
    border-radius: 20px; padding: 5px 16px;
    font-size: 11px; font-weight: 600; color: #00d4aa;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 24px;
}
.hero-title {
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 700; line-height: 1.1;
    letter-spacing: -1.5px;
    background: linear-gradient(135deg, #ffffff 30%, #8888b0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
}
.hero-subtitle {
    font-size: 16px; color: #6666a0; font-weight: 400; max-width: 540px; margin: 0 auto 40px;
    line-height: 1.7;
}

/* ── URL Input Box ────────────────────────── */
.url-input-wrapper {
    max-width: 720px; margin: 0 auto 32px;
    background: #0d0d1a;
    border: 1.5px solid #1e1e30;
    border-radius: 16px;
    padding: 6px 6px 6px 20px;
    display: flex; align-items: center; gap: 12px;
    transition: border-color 0.3s ease;
}
.url-input-wrapper:focus-within { border-color: #00d4aa; box-shadow: 0 0 0 3px rgba(0,212,170,0.08); }
.url-prefix { font-size: 13px; color: #4444668; font-family: 'JetBrains Mono', monospace; white-space: nowrap; }

/* ── Streamlit overrides inside input wrapper ─ */
.url-input-wrapper [data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    color: #e2e2f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    padding: 0 !important;
    box-shadow: none !important;
}

/* ── Analyze Button ───────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00d4aa, #0099ff) !important;
    color: #080810 !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 14px 32px !important;
    letter-spacing: 0.3px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,212,170,0.35) !important;
}

/* ── Metric Cards ─────────────────────────── */
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 32px 0; }
.metric-card {
    background: #0d0d1a;
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease;
}
.metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00d4aa, #0099ff);
}
.metric-card:hover { border-color: rgba(0,212,170,0.3); }
.metric-label { font-size: 11px; color: #5a5a78; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
.metric-value { font-size: 26px; font-weight: 700; color: #e2e2f0; letter-spacing: -0.5px; }
.metric-unit { font-size: 12px; color: #6666a0; margin-top: 4px; }

/* ── Timestamp Card ───────────────────────── */
.ts-card {
    background: #0d0d1a;
    border: 1px solid #1e1e30;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
    transition: all 0.2s ease;
    text-decoration: none !important;
}
.ts-card:hover { border-color: rgba(0,212,170,0.35); background: #11112a; transform: translateX(4px); }
.ts-badge {
    background: rgba(0,212,170,0.1);
    border: 1px solid rgba(0,212,170,0.25);
    color: #00d4aa;
    border-radius: 8px;
    padding: 4px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 600;
    white-space: nowrap; flex-shrink: 0;
    min-width: 62px; text-align: center;
}
.ts-desc { font-size: 13px; color: #b0b0cc; line-height: 1.5; }

/* ── Report Card ──────────────────────────── */
.report-container {
    background: #0d0d1a;
    border: 1px solid #1e1e30;
    border-radius: 18px;
    padding: 36px 40px;
}
.report-container h1 { font-size: 22px !important; color: #ffffff !important; margin-bottom: 4px !important; }
.report-container h2 { font-size: 16px !important; color: #8888a8 !important; }
.report-container h3 { font-size: 15px !important; color: #00d4aa !important; border-left: 3px solid #00d4aa; padding-left: 12px; margin: 20px 0 10px; }
.report-container table { width: 100%; border-collapse: collapse; margin: 16px 0; }
.report-container th { background: #12122a; color: #8888a8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; padding: 10px 14px; border: 1px solid #1e1e30; }
.report-container td { padding: 10px 14px; border: 1px solid #1a1a2e; font-size: 13px; color: #c0c0d8; vertical-align: top; }
.report-container tr:hover td { background: rgba(0,212,170,0.03); }
.report-container blockquote { border-left: 3px solid #0099ff; background: rgba(0,153,255,0.06); border-radius: 0 8px 8px 0; padding: 14px 18px; margin: 16px 0; color: #a0a0c0; }
.report-container code { background: #12122a; color: #00d4aa; border-radius: 4px; padding: 2px 6px; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.report-container hr { border: none; border-top: 1px solid #1e1e30; margin: 24px 0; }
.report-container ul, .report-container ol { padding-left: 20px; color: #b0b0cc; }
.report-container li { margin-bottom: 6px; font-size: 13.5px; line-height: 1.7; }
.report-container strong { color: #e2e2f0; }
.report-container a { color: #00d4aa; text-decoration: none; }
.report-container a:hover { text-decoration: underline; }
.report-container p { font-size: 14px; line-height: 1.8; color: #c0c0d8; margin-bottom: 12px; }

/* ── Tab Overrides ────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0d0d1a !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Sora', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #6666a0 !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    border: none !important;
    background: transparent !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: rgba(0,212,170,0.12) !important;
    color: #00d4aa !important;
}

/* ── Progress / Spinner ───────────────────── */
.stSpinner > div { border-top-color: #00d4aa !important; }

/* ── Alert overrides ──────────────────────── */
.stAlert { border-radius: 12px !important; font-family: 'Sora', sans-serif !important; font-size: 13px !important; }

/* ── Video Player ─────────────────────────── */
[data-testid="stVideo"] { border-radius: 14px; overflow: hidden; border: 1px solid #1e1e30; }

/* ── Download Button ──────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: rgba(0,212,170,0.1) !important;
    color: #00d4aa !important;
    border: 1px solid rgba(0,212,170,0.3) !important;
    border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    width: 100%;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0,212,170,0.18) !important;
}

/* ── Divider ──────────────────────────────── */
[data-testid="stDivider"] { border-color: #1e1e30 !important; }

/* ── Section Labels ───────────────────────── */
.section-label {
    font-size: 11px; font-weight: 600; letter-spacing: 1.5px;
    text-transform: uppercase; color: #4a4a68;
    margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: #1e1e30; }

/* ── Scrollbar ────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #2a2a40; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a55; }

/* Hide default Streamlit elements */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 0 2rem 2rem !important; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)


# ─── Utilities ────────────────────────────────────────────────────────────────
def extract_video_id(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        if parsed.hostname in ("youtu.be",):
            return parsed.path.lstrip("/").split("?")[0]
        qs = parse_qs(parsed.query)
        return qs.get("v", [None])[0]
    except Exception:
        return None


def estimate_reading_time(text: str) -> int:
    return max(1, len(text.split()) // 200)


def word_count(text: str) -> int:
    return len(text.split())


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-logo">
        <div class="brand-icon">IS</div>
        <div>
            <div class="brand-name">IntelStream</div>
            <div class="brand-tag">YouTube Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-item active">🎯 &nbsp; Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">📁 &nbsp; Report History</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">⚙️ &nbsp; Settings</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Controls</div>', unsafe_allow_html=True)

    debug_mode = st.toggle("Debug Logs", value=False, help="Print verbose logs to terminal")
    use_cache  = st.toggle("Response Cache", value=True, help="Skip re-analysis for recent URLs")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️  Clear Cache", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">System</div>', unsafe_allow_html=True)
    st.markdown('<div class="status-badge"><div class="status-dot"></div>All Systems Operational</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("IntelStream AI · v3.0\nGroq · LLaMA 3.3 70B")


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">⚡ Powered by Groq + LLaMA 3.3 70B</div>
    <div class="hero-title">YouTube Intelligence,<br>Instantly Decoded</div>
    <div class="hero-subtitle">
        Paste any YouTube URL. Get a structured intelligence report with timestamps,
        key insights, and an actionable blueprint — in seconds.
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Input ────────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1], gap="small")

with col_input:
    video_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )

with col_btn:
    analyze_clicked = st.button("⚡  Analyze", use_container_width=True)

st.markdown("---")

# ─── Main Analysis ────────────────────────────────────────────────────────────
if analyze_clicked and video_url:
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("⚠️  Could not parse a valid YouTube video ID from the URL. Please check and try again.")
        st.stop()

    # ── Check Cache ──────────────────────────────────────────────────────
    cached = get_cached_report(video_url) if use_cache else None

    if cached:
        st.toast("⚡ Loaded from cache", icon="💾")
        report_content = cached["content"]
        meta = cached["metadata"]
    else:
        # ── Live Analysis ────────────────────────────────────────────────
        progress_bar = st.progress(0, text="Initializing agent...")
        status_placeholder = st.empty()

        try:
            start = time.time()

            status_placeholder.markdown(
                "🔌 **Connecting to Groq inference engine…**", unsafe_allow_html=False
            )
            progress_bar.progress(10, text="Connecting to Groq…")
            agent = build_youtube_agent()

            progress_bar.progress(30, text="Fetching transcript from YouTube…")
            status_placeholder.markdown("📡 **Fetching transcript & metadata from YouTube…**")

            if debug_mode:
                print(f"\n[DEBUG] Starting analysis — video_id={video_id}")

            progress_bar.progress(55, text="Running LLaMA 3.3 70B intelligence pass…")
            status_placeholder.markdown("🧠 **Running LLaMA 3.3 70B intelligence pass…** (this takes ~10–20s)")

            response = agent.run(
                f"Perform a full Intelligence Report on this YouTube video: {video_url}\n"
                f"Make sure to include all timestamp markers in [MM:SS] format throughout the report."
            )

            elapsed = round(time.time() - start, 1)
            progress_bar.progress(90, text="Building report…")
            status_placeholder.empty()

            report_content = response.content

            meta = {
                "elapsed": elapsed,
                "words": word_count(report_content),
                "read_time": estimate_reading_time(report_content),
                "video_id": video_id,
            }

            cache_report(video_url, report_content, meta)

            if debug_mode:
                print(f"[DEBUG] video_id={video_id} | elapsed={elapsed}s | words={meta['words']}")

            progress_bar.progress(100, text="Done!")
            time.sleep(0.3)
            progress_bar.empty()
            status_placeholder.empty()
            st.toast("✅ Intelligence Report generated!", icon="🎯")

        except Exception as err:
            progress_bar.empty()
            status_placeholder.empty()
            st.error(f"**Analysis Failed:** {err}")
            st.info("💡 Ensure the video URL is correct, public, and has captions/subtitles enabled.")
            st.stop()

    # ── Metric Row ───────────────────────────────────────────────────────
    timestamps = extract_timestamps(report_content)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Generation Time</div>
            <div class="metric-value">{meta.get('elapsed', '—')}<span style="font-size:14px;color:#6666a0">s</span></div>
            <div class="metric-unit">via Groq inference</div>
        </div>""", unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Report Words</div>
            <div class="metric-value">{meta.get('words', 0):,}</div>
            <div class="metric-unit">intelligence output</div>
        </div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Timestamps</div>
            <div class="metric-value">{len(timestamps)}</div>
            <div class="metric-unit">chapters mapped</div>
        </div>""", unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Read Time</div>
            <div class="metric-value">{meta.get('read_time', 1)}<span style="font-size:14px;color:#6666a0"> min</span></div>
            <div class="metric-unit">estimated</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Main Layout ──────────────────────────────────────────────────────
    left_col, right_col = st.columns([1, 2], gap="large")

    # ── LEFT: Media + Timestamps ──────────────────────────────────────────
    with left_col:
        st.markdown('<div class="section-label">Source Media</div>', unsafe_allow_html=True)
        st.video(video_url)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("🖼️ Thumbnail Preview", expanded=False):
            st.image(
                f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                use_container_width=True,
            )

        # ── Timestamps Panel ──────────────────────────────────────────────
        if timestamps:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Chapter Timeline</div>', unsafe_allow_html=True)

            for ts in timestamps:
                yt_link = youtube_timestamp_url(video_id, ts["seconds"])
                desc_html = ts["description"] if ts["description"] else "Jump to segment →"
                st.markdown(f"""
                <a href="{yt_link}" target="_blank" class="ts-card" style="display:flex;text-decoration:none;">
                    <span class="ts-badge">{ts['label']}</span>
                    <span class="ts-desc">{desc_html}</span>
                </a>""", unsafe_allow_html=True)
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("No timestamps were extracted. The video may lack transcript data.")

    # ── RIGHT: Report Tabs ────────────────────────────────────────────────
    with right_col:
        tab_report, tab_raw = st.tabs(["📄  Intelligence Report", "🔧  Raw Markdown"])

        with tab_report:
            dl_col, _ = st.columns([1, 3])
            with dl_col:
                st.download_button(
                    label="📥 Download .md",
                    data=report_content,
                    file_name=f"IntelStream_{video_id}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="report-container">', unsafe_allow_html=True)
            st.markdown(report_content)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_raw:
            st.code(report_content, language="markdown")

# ─── Empty State ──────────────────────────────────────────────────────────────
elif not analyze_clicked:
    st.markdown("""
    <div style="text-align:center; padding: 40px 20px; color: #3a3a58;">
        <div style="font-size: 48px; margin-bottom: 16px;">🎯</div>
        <div style="font-size: 15px; font-weight: 600; color: #5a5a78; margin-bottom: 8px;">
            Ready to Analyze
        </div>
        <div style="font-size: 13px; color: #3a3a52;">
            Paste a YouTube URL above and click <strong style="color:#00d4aa">⚡ Analyze</strong> to generate your intelligence report.
        </div>
        <br>
        <div style="display:flex; justify-content:center; gap:24px; flex-wrap:wrap; margin-top:16px;">
            <div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:12px;padding:20px 28px;min-width:150px;">
                <div style="font-size:22px;margin-bottom:8px;">⚡</div>
                <div style="font-size:12px;font-weight:600;color:#6666a0;">Ultra-fast</div>
                <div style="font-size:11px;color:#3a3a52;">Groq inference</div>
            </div>
            <div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:12px;padding:20px 28px;min-width:150px;">
                <div style="font-size:22px;margin-bottom:8px;">🕒</div>
                <div style="font-size:12px;font-weight:600;color:#6666a0;">Timestamps</div>
                <div style="font-size:11px;color:#3a3a52;">Clickable chapters</div>
            </div>
            <div style="background:#0d0d1a;border:1px solid #1e1e30;border-radius:12px;padding:20px 28px;min-width:150px;">
                <div style="font-size:22px;margin-bottom:8px;">📥</div>
                <div style="font-size:12px;font-weight:600;color:#6666a0;">Exportable</div>
                <div style="font-size:11px;color:#3a3a52;">Download as .md</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)