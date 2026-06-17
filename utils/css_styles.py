# ==========================================
# utils/css_styles.py
# ==========================================

CSS_GLOBAL = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ============ BASE ============ */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {
        background: linear-gradient(160deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color-scheme: light !important;
    }

    /* ============ HIDE ELEMENTS ============ */
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    button[title="View fullscreen"] { display: none !important; }

    /* ============ SIDEBAR ============ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }

    [data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0 !important;
    }

    /* ============ SIDEBAR BUTTONS & LINKS ============ */
    [data-testid="stSidebar"] .stButton,
    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        margin-bottom: 2px !important;
        margin-top: 0 !important;
    }

    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] [data-testid="stPageLink"] > a {
        width: 100% !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: background 0.2s ease, color 0.2s ease, transform 0.18s ease !important;
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: #cbd5e1 !important;
        text-decoration: none !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] [data-testid="stPageLink"] > a:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #f1f5f9 !important;
        border-color: rgba(255,255,255,0.12) !important;
        transform: translateX(3px) !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(96,165,250,0.14) !important;
        border: 1px solid rgba(96,165,250,0.25) !important;
        color: #60a5fa !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(96,165,250,0.22) !important;
        color: #93c5fd !important;
    }

    /* ============ MAIN TYPOGRAPHY ============ */
    .main h1, .main h2, .main h3,
    .main p, .main label, .main input,
    .main [data-testid="stMarkdownContainer"] p,
    .main [data-testid="stMarkdownContainer"] span,
    .main [data-testid="stWidgetLabel"] label,
    .main [data-testid="stWidgetLabel"] p,
    .main .stButton > button,
    .main .stDownloadButton > button,
    [data-testid="stForm"] label,
    [data-testid="stForm"] p,
    [data-testid="stForm"] input {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    .main h1 {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.03em !important;
        line-height: 1.25 !important;
    }

    .main h2 {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.02em !important;
    }

    .main h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    .main p,
    .main [data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        color: #374151 !important;
    }

    .main strong {
        font-weight: 700 !important;
        color: #1e293b !important;
    }

    /* ============ LABEL INPUT ============ */
    .main [data-testid="stTextInput"] label,
    .main [data-testid="stNumberInput"] label,
    .main .stSelectbox label,
    .main .stCheckbox label,
    .main .stTextArea label {
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 6px !important;
    }

    /* ============ METRIC ============ */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
        transition: box-shadow 0.22s ease, transform 0.22s ease !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 14px rgba(0,0,0,0.07) !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #6b7280 !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
    }

    /* ============ BUTTONS ============ */
    .main .stButton > button {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        color: #374151 !important;
        border: 1.5px solid #d1d5db !important;
        background: #ffffff !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease !important;
        padding: 10px 16px !important;
    }

    .main .stButton > button:hover {
        background: #f9fafb !important;
        color: #111827 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        transform: translateY(-1px) !important;
    }

    .main .stButton > button:active {
        transform: translateY(0) !important;
    }

    .main .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        border: none !important;
        color: #ffffff !important;
    }

    .main .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.28) !important;
        transform: translateY(-1px) !important;
    }

    /* ============ DOWNLOAD BUTTON ============ */
    .main .stDownloadButton > button {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 16px !important;
        min-height: 42px !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease !important;
    }

    .main .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        box-shadow: 0 4px 14px rgba(5,150,105,0.28) !important;
        transform: translateY(-1px) !important;
    }

    .main .stDownloadButton > button p,
    .main .stDownloadButton > button span {
        color: #ffffff !important;
        font-size: 0.85rem !important;
    }

    /* ============ FORM ============ */
    [data-testid="stForm"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 14px !important;
        padding: 24px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    /* ============ EXPANDER ============ */
    [data-testid="stExpander"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        margin-bottom: 8px !important;
        transition: box-shadow 0.22s ease !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"]:hover {
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stExpander"] summary > span > div > p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }

    /* ============ DATAFRAME ============ */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid #e5e7eb !important;
        overflow: hidden !important;
    }

    [data-testid="stDataFrame"] th {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #4b5563 !important;
        background: #f9fafb !important;
        letter-spacing: 0.04em !important;
    }

    [data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        color: #374151 !important;
    }

    /* ============ ALERT ============ */
    .main [data-testid="stAlert"] {
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }

    .main [data-testid="stAlert"] p {
        font-size: 0.86rem !important;
        font-weight: 500 !important;
    }

    /* ============ TOGGLE ============ */
    .main .stToggle label p {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }

    /* ============ DIVIDER ============ */
    .main hr {
        border: none !important;
        border-top: 1px solid #e5e7eb !important;
        margin: 16px 0 !important;
    }

    /* ============ TABS ============ */
    .main [data-testid="stTabs"] [role="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
    }

    .main [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #2563eb !important;
    }

    /* ============ SCROLLBAR ============ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }

    /* ============ BLOCK CONTAINER ============ */
    .main .block-container {
        max-width: 82%;
        margin: 0 auto;
        padding-top: 1.5rem !important;
        animation: pageEnter 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    @keyframes pageEnter {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
        .main .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    /* ============ ANIMASI KONTEN ============ */
    [data-testid="stMetric"] {
        animation: fadeUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    [data-testid="stForm"] {
        animation: fadeUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.05s both;
    }

    [data-testid="stAlert"] {
        animation: fadeDown 0.3s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    [data-testid="stExpander"] {
        animation: fadeLeft 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    [data-testid="stDataFrame"] {
        animation: fadeUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.05s both;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeDown {
        from { opacity: 0; transform: translateY(-5px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeLeft {
        from { opacity: 0; transform: translateX(-5px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    /* ============ LOGIN CARD ============ */
    .login-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        animation: pageEnter 0.5s ease-out;
    }

    .login-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 40px 36px;
        box-shadow:
            0 10px 30px rgba(15, 23, 42, 0.08),
            0 4px 12px rgba(15, 23, 42, 0.04);
        width: 100%;
        max-width: 420px;
        text-align: center;
    }

    .login-logo {
        margin-bottom: 16px;
    }

    .login-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
    }

    .login-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        margin: 0 0 28px 0;
    }
</style>
"""


CSS_INPUT_TIMBUL = """
<style>
/* INPUT PUTIH TIMBUL — VERSI INLINE PER HALAMAN */
[data-baseweb="input"],
[data-baseweb="base-input"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 2px solid #64748b !important;
    border-radius: 10px !important;
    box-shadow:
        0 4px 12px rgba(15, 23, 42, 0.10),
        0 2px 4px rgba(15, 23, 42, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 1) !important;
    padding: 2px !important;
    transition: all 0.2s ease !important;
}

[data-baseweb="input"]:hover,
[data-baseweb="base-input"]:hover {
    border-color: #334155 !important;
    box-shadow:
        0 6px 16px rgba(15, 23, 42, 0.14),
        0 3px 6px rgba(15, 23, 42, 0.08) !important;
    transform: translateY(-1px) !important;
}

[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within {
    background: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow:
        0 0 0 4px rgba(37, 99, 235, 0.15),
        0 6px 16px rgba(37, 99, 235, 0.12) !important;
}

[data-baseweb="input"] input,
[data-baseweb="base-input"] input {
    background: #ffffff !important;
    color: #0f172a !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

[data-baseweb="input"] input::placeholder,
[data-baseweb="base-input"] input::placeholder {
    color: #94a3b8 !important;
    font-weight: 400 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 2px solid #64748b !important;
    border-radius: 10px !important;
    box-shadow:
        0 4px 12px rgba(15, 23, 42, 0.10),
        0 2px 4px rgba(15, 23, 42, 0.06) !important;
}

/* Text area */
.stTextArea textarea {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 2px solid #64748b !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.10) !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
}

/* Hilangkan tombol +/- */
button[data-testid="stNumberInputStepDown"],
button[data-testid="stNumberInputStepUp"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    pointer-events: none !important;
}

[data-testid="stNumberInput"] > div {
    gap: 0 !important;
}

/* TOMBOL HIDE SIDEBAR — SELALU TERLIHAT */
[data-testid="stSidebar"] button[kind="header"],
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
    background: rgba(255,255,255,0.25) !important;
    border: 2px solid rgba(255,255,255,0.50) !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
}

[data-testid="stSidebar"] button[kind="header"] svg *,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg * {
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    background: #ffffff !important;
    border: 2px solid #475569 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    opacity: 1 !important;
    visibility: visible !important;
}

[data-testid="collapsedControl"] svg *,
[data-testid="stSidebarCollapsedControl"] svg * {
    fill: #0f172a !important;
    stroke: #0f172a !important;
}
</style>
"""


CSS_WELCOME = """
<style>
    .welcome-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        padding: 20px;
    }

    .welcome-logo {
        animation: logoEntry 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards,
                   logoPulse 3.5s ease-in-out 1.5s infinite;
        opacity: 0;
        filter: drop-shadow(0 8px 20px rgba(0,0,0,0.12));
        will-change: transform, opacity;
    }

    @keyframes logoEntry {
        0%   { opacity: 0; transform: scale(0.4) translateY(20px); }
        60%  { opacity: 1; }
        80%  { transform: scale(1.05) translateY(-3px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }

    @keyframes logoPulse {
        0%, 100% { transform: scale(1); }
        50%       { transform: scale(1.03); }
    }

    .welcome-title {
        animation: textUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.3s forwards;
        opacity: 0;
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.03em;
        margin: 24px 0 0 0;
        line-height: 1.2;
        will-change: transform, opacity;
    }

    .welcome-subtitle {
        animation: textUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.45s forwards;
        opacity: 0;
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        font-weight: 500;
        color: #64748b;
        margin: 8px 0 0 0;
        will-change: transform, opacity;
    }

    .welcome-line {
        animation: lineExpand 0.55s cubic-bezier(0.22, 1, 0.36, 1) 0.6s forwards;
        opacity: 0;
        width: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
        margin: 20px auto;
        border-radius: 2px;
        will-change: width, opacity;
    }

    @keyframes lineExpand {
        from { opacity: 0; width: 0; }
        to   { opacity: 1; width: 100px; }
    }

    .welcome-hint {
        animation: textUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.75s forwards;
        opacity: 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 400;
        color: #94a3b8;
        margin: 8px 0 0 0;
        will-change: transform, opacity;
    }

    .welcome-credit {
        animation: textUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.9s forwards;
        opacity: 0;
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        will-change: transform, opacity;
    }

    .welcome-credit-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        font-weight: 400;
        color: #94a3b8;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 0 0 4px 0;
    }

    .welcome-credit-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        color: #475569;
        letter-spacing: 0.01em;
        margin: 0;
    }

    @keyframes textUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


def inject_input_style():
    import streamlit as st
    st.markdown(CSS_INPUT_TIMBUL, unsafe_allow_html=True)


def inject_welcome_css():
    import streamlit as st
    st.markdown(CSS_WELCOME, unsafe_allow_html=True)
