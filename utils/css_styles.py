st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {
        background: linear-gradient(160deg, #f8fafc 0%, #f1f5f9 100%) !important;
        color-scheme: light !important;
    }

    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    button[title="View fullscreen"] { display: none !important; }

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

    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
        color: #ffffff !important;
        background: rgba(255,255,255,0.16) !important;
        border: 1.5px solid rgba(255,255,255,0.35) !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] button[kind="header"] svg * {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] > button,
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] > button {
        color: #111827 !important;
        background: #ffffff !important;
        border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
    }

    [data-testid="collapsedControl"] svg *,
    [data-testid="stSidebarCollapsedControl"] svg * {
        fill: #111827 !important;
        stroke: #111827 !important;
    }

    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
        margin: 1px 0 !important;
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: background 0.2s ease, color 0.2s ease, transform 0.18s ease !important;
        will-change: transform !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: #94a3b8 !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #e2e8f0 !important;
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
        transform: translateX(3px) !important;
    }

    .submenu-container {
        overflow: hidden;
        animation: submenuSlide 0.32s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transform-origin: top;
        will-change: transform, opacity;
    }

    @keyframes submenuSlide {
        from { max-height: 0; opacity: 0; transform: translateY(-6px) scaleY(0.96); }
        to   { max-height: 320px; opacity: 1; transform: translateY(0) scaleY(1); }
    }

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
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.03em !important;
        line-height: 1.25 !important;
    }

    .main h2 {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.02em !important;
    }

    .main h3 {
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    .main p,
    .main [data-testid="stMarkdownContainer"] p {
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        color: #374151 !important;
    }

    .main strong {
        font-weight: 700 !important;
        color: #1e293b !important;
    }

    .main .stTextInput label,
    .main .stNumberInput label,
    .main .stSelectbox label,
    .main .stCheckbox label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }

    .main .stTextInput input,
    .main .stNumberInput input {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #1e293b !important;
        background: #ffffff !important;
        border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .main .stTextInput input:focus,
    .main .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    }

    .main .stTextInput input::placeholder,
    .main .stNumberInput input::placeholder {
        color: #9ca3af !important;
    }

    /* HILANGKAN TOMBOL +/- NUMBER INPUT */
    .main .stNumberInput button,
    .main .stNumberInput [data-testid="stNumberInputStepUp"],
    .main .stNumberInput [data-testid="stNumberInputStepDown"] {
        display: none !important;
    }

    .main .stNumberInput input {
        width: 100% !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
        transition: box-shadow 0.22s ease, transform 0.22s ease !important;
        will-change: transform !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 14px rgba(0,0,0,0.07) !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
        color: #6b7280 !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
    }

    .main .stButton > button {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        color: #374151 !important;
        border: 1.5px solid #d1d5db !important;
        background: #ffffff !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease !important;
        will-change: transform !important;
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

    .main .stDownloadButton > button {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 8px 16px !important;
        min-height: 40px !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.18s ease !important;
        will-change: transform !important;
    }

    .main .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        box-shadow: 0 4px 14px rgba(5,150,105,0.28) !important;
        transform: translateY(-1px) !important;
    }

    .main .stDownloadButton > button p,
    .main .stDownloadButton > button span {
        color: #ffffff !important;
        font-size: 0.82rem !important;
    }

    [data-testid="stForm"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        background: #ffffff !important;
        margin-bottom: 6px !important;
        transition: box-shadow 0.22s ease !important;
    }

    [data-testid="stExpander"]:hover {
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stExpander"] summary > span > div > p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
    }

    [data-testid="stDataFrame"] th {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        color: #4b5563 !important;
        background: #f9fafb !important;
    }

    [data-testid="stDataFrame"] td {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        color: #374151 !important;
    }

    .main [data-testid="stAlert"] p {
        font-size: 0.84rem !important;
        font-weight: 500 !important;
    }

    .main hr {
        border: none !important;
        border-top: 1px solid #e5e7eb !important;
    }

    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    ::-webkit-scrollbar-track { background: transparent; }

    .main .block-container {
        max-width: 82%;
        margin: 0 auto;
        padding-top: 1.5rem !important;
        animation: pageEnter 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
        will-change: opacity, transform;
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

    [data-testid="stMetric"] {
        animation: fadeUp 0.38s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    [data-testid="stForm"] {
        animation: fadeUp 0.38s cubic-bezier(0.22, 1, 0.36, 1) 0.05s both;
    }

    [data-testid="stAlert"] {
        animation: fadeDown 0.3s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    [data-testid="stExpander"] {
        animation: fadeLeft 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    [data-testid="stDataFrame"] {
        animation: fadeUp 0.36s cubic-bezier(0.22, 1, 0.36, 1) 0.04s both;
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

</style>
""", unsafe_allow_html=True)
