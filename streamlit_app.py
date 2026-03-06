import streamlit as st
import requests
import json
import base64

BACKEND_URL = "http://127.0.0.1:8000/analyze-document"

st.set_page_config(
    page_title="Content Understanding Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- LOAD LOGO ----------
def get_base64_logo(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

logo_base64 = get_base64_logo("Exavalu_logo.png")
logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="top-right-logo">' if logo_base64 else ""

# ---------- CUSTOM CSS ----------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    /* ---- Reset & Base ---- */
    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background: #F7F8FC;
    }}

    /* ---- Top logo ---- */
    .top-right-logo {{
        position: fixed;
        top: 18px;
        right: 32px;
        width: 210px;
        z-index: 1000;
        filter: drop-shadow(0 1px 3px rgba(0,0,0,0.10));
    }}

    /* ---- Hide Streamlit chrome ---- */
    #MainMenu, footer, header {{visibility: hidden;}}

    /* ---- Main container ---- */
    .main .block-container {{
        max-width: 860px;
        padding: 3rem 2rem 4rem;
        margin: 0 auto;
    }}

    /* ---- Header ---- */
    .page-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 6px;
    }}
    .page-header .icon {{
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        border-radius: 14px;
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 4px 14px rgba(37,99,235,0.30);
        flex-shrink: 0;
    }}
    .page-header h1 {{
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        font-weight: 400;
        color: #0F172A;
        margin: 0;
        line-height: 1.2;
    }}
    .subtitle {{
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 2.4rem;
        font-weight: 400;
        padding-left: 66px;
    }}

    /* ---- Divider ---- */
    .divider {{
        height: 1px;
        background: linear-gradient(to right, #E2E8F0, transparent);
        margin: 0 0 2.2rem;
    }}

    /* ---- Upload card ---- */
    .upload-card {{
        background: #ffffff;
        border: 1.5px dashed #CBD5E1;
        border-radius: 18px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: border-color 0.2s;
        margin-bottom: 1.4rem;
    }}
    .upload-card:hover {{
        border-color: #2563EB;
    }}
    .upload-card .upload-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.6rem;
    }}
    .upload-card p {{
        color: #64748B;
        font-size: 0.9rem;
        margin: 0;
    }}

    /* ---- File info pill ---- */
    .file-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E40AF;
        border-radius: 999px;
        padding: 6px 16px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 1.4rem;
    }}

    /* ---- Streamlit uploader override ---- */
    [data-testid="stFileUploader"] {{
        background: white;
        border: 1.5px dashed #CBD5E1;
        border-radius: 18px;
        padding: 1.8rem 1.5rem;
        transition: border-color 0.2s;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: #2563EB;
    }}
    [data-testid="stFileUploaderDropzone"] {{
        background: transparent !important;
        border: none !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] {{
        color: #64748B !important;
    }}

    /* ---- Button ---- */
    .stButton > button {{
        background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 2rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.30) !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(37,99,235,0.40) !important;
    }}
    .stButton > button:active {{
        transform: translateY(0px) !important;
    }}

    /* ---- Results card ---- */
    .results-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'DM Serif Display', serif;
        font-size: 1.3rem;
        color: #0F172A;
        margin-bottom: 1rem;
    }}
    .results-badge {{
        background: #DCFCE7;
        color: #15803D;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        letter-spacing: 0.04em;
    }}

    /* ---- Spinner override ---- */
    .stSpinner {{
        color: #2563EB !important;
    }}

    /* ---- Alert boxes ---- */
    .stSuccess {{
        border-radius: 12px !important;
        border-left: 4px solid #22C55E !important;
    }}
    .stError {{
        border-radius: 12px !important;
        border-left: 4px solid #EF4444 !important;
    }}

    /* ---- JSON output ---- */
    .stJson {{
        border-radius: 14px !important;
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
    }}

    /* ---- Step labels ---- */
    .step-label {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        color: #94A3B8;
        margin-bottom: 0.5rem;
    }}
    </style>
    {logo_html}
    """,
    unsafe_allow_html=True,
)

# ---------- HEADER ----------
st.markdown("""
    <div class="page-header">
        <div class="icon">📄</div>
        <h1>Content Understanding Analyzer</h1>
    </div>
    <p class="subtitle">Powered by Azure AI · Extract structured insights from any document instantly</p>
    <div class="divider"></div>
""", unsafe_allow_html=True)

# ---------- LAYOUT ----------
col_main, col_side = st.columns([3, 1])

with col_main:
    st.markdown('<p class="step-label">Step 1 — Upload your file</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drag & drop or click to browse",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="visible"
    )

    if uploaded_file is not None:
        ext = uploaded_file.name.split(".")[-1].upper()
        size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
        st.markdown(
            f'<div class="file-pill">📎 {uploaded_file.name} &nbsp;·&nbsp; {ext} &nbsp;·&nbsp; {size_kb} KB</div>',
            unsafe_allow_html=True
        )

        st.markdown('<p class="step-label">Step 2 — Run analysis</p>', unsafe_allow_html=True)

        if st.button("⚡  Analyze Document"):
            with st.spinner("Analyzing document — this may take a few seconds…"):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }
                try:
                    response = requests.post(BACKEND_URL, files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.code(json.dumps(result, indent=2))
                        st.markdown("""
                            <div class="results-header">
                                📊 Extracted Results
                                <span class="results-badge">✓ COMPLETE</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.json(result)
                    else:
                        st.error(f"**Server Error {response.status_code}** — The backend returned an unexpected response.")
                        with st.expander("View raw response"):
                            st.code(response.text, language="text")
                except Exception as e:
                    st.error(f"**Connection Failed** — Could not reach the backend at `{BACKEND_URL}`\n\n`{e}`")

with col_side:
    st.markdown("""
        <div style="background:white; border-radius:16px; padding:1.4rem 1.2rem; border:1px solid #E2E8F0; margin-top:1.8rem;">
            <p style="font-size:0.72rem; font-weight:600; letter-spacing:0.10em; text-transform:uppercase; color:#94A3B8; margin-bottom:0.8rem;">Supported Formats</p>
            <div style="display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#334155;">
                    <span style="background:#FEF9C3; border-radius:6px; padding:2px 8px; font-weight:600; color:#854D0E; font-size:0.75rem;">PDF</span> Documents
                </div>
                <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#334155;">
                    <span style="background:#DCFCE7; border-radius:6px; padding:2px 8px; font-weight:600; color:#166534; font-size:0.75rem;">PNG</span> Images
                </div>
                <div style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:#334155;">
                    <span style="background:#DBEAFE; border-radius:6px; padding:2px 8px; font-weight:600; color:#1E40AF; font-size:0.75rem;">JPG</span> Photos
                </div>
            </div>
            <div style="margin-top:1.2rem; border-top:1px solid #F1F5F9; padding-top:1.2rem;">
                <p style="font-size:0.72rem; font-weight:600; letter-spacing:0.10em; text-transform:uppercase; color:#94A3B8; margin-bottom:0.6rem;">How it works</p>
                <p style="font-size:0.82rem; color:#64748B; line-height:1.6; margin:0;">Upload a file, click Analyze, and Azure AI will extract structured fields, tables, and key information automatically.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("""
    <div style="margin-top:4rem; border-top:1px solid #E2E8F0; padding-top:1.2rem; text-align:center; color:#94A3B8; font-size:0.78rem;">
        Exavalu · Azure Content Understanding · Confidential
    </div>
""", unsafe_allow_html=True)