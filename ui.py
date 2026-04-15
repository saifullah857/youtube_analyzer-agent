import streamlit as st
import os
from Youtube_Analyzer import build_youtube_agent

# 1. Advanced Dashboard Configuration
st.set_page_config(
    page_title="Video Intel Pro - Debug Mode",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Dashboard Styling
st.markdown("""
    <style>
        .report-card {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #e1e4e8;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #D43F3F;
            border: 1px solid white;
        }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Control Center)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1384/1384060.png", width=70)
    st.title("Admin Controls")
    st.divider()
    debug_mode = st.toggle("Enable Debug Logs", value=True)
    if st.button("🧹 Clear Agent Cache"):
        st.cache_resource.clear()
        st.rerun()
    st.info("System Status: Operational 🟢")

# 4. Main Application Interface
st.title("🎥 YouTube Intelligence Dashboard")
st.caption("Advanced Semantic Analysis Engine v2.0")

video_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")

if st.button("🚀 Analyze Intelligence") and video_url:
    try:
        # Extract Video ID for high-res assets
        video_id = video_url.split("v=")[-1].split("&")[0]
        
        with st.spinner("🧠 Initializing Neural Agent & Fetching Subtitles..."):
            agent = build_youtube_agent()
            
            # RUN AGENT
            response = agent.run(f"Perform a high-level Intelligence Report on: {video_url}")

            # DEBUG LOGS (Shows in Terminal)
            if debug_mode:
                print(f"--- DEBUG LOG START ---")
                print(f"Video ID: {video_id}")
                print(f"Response Length: {len(response.content)} characters")
                print(f"--- DEBUG LOG END ---")

        st.divider()

        # 5. Dual-Column Dashboard Layout
        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            st.subheader("📺 Source Media")
            st.video(video_url)
            
            with st.expander("🖼️ Technical Assets (Thumbnail)", expanded=False):
                st.image(f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg", use_container_width=True)
            
            st.success("✅ Semantic Data Extracted")
            st.toast("Intelligence Report Generated!")

        with col_right:
            st.subheader("📄 Intelligence Report")
            
            # Action Row
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Download Report (.md)", response.content, file_name=f"Intel_{video_id}.md")
            with c2:
                st.button("📋 Copy to Clipboard (Beta)")

            # The Main Content Area
            st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
            st.markdown(response.content)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Critical System Error: {e}")
        st.info("Debugging Tip: Ensure the video URL is correct and has a transcript available.")

else:
    st.divider()
    st.markdown("### 🔍 Awaiting Input...")
    st.text("Paste a YouTube link above to trigger the analysis agent.")