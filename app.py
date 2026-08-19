# imports

import streamlit as st
from modules.utils import THEME

# page config 
# this always needs to be the first thing in the app.py file
st.set_page_config(
    page_title="RBR Telemetry System", # page title
    page_icon="🏎️", # page icon
    layout="centered", # layout of the app (centered, wide, or fixed)
    initial_sidebar_state="collapsed" # initial state of the sidebar (auto, expanded, or collapsed)
)

# state initiation
if "selection" not in st.session_state:
    st.session_state.selection = "Home" # app routing

if "method_focus" not in st.session_state:
    st.session_state.method_focus = None # card focus

# app style
st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Titillium+Web:wght@300;400;700&display=swap" rel="stylesheet">

    <style>
    /* Aplica a tipografia na raiz do Streamlit */
    .stApp {{
        background-color: #0b111e;
        color: {THEME['text_main']};
        font-family: 'Titillium Web', sans-serif !important;
    }}
    
    /* Força os títulos principais, subheadings e labels do cockpit a usarem a fonte F1/Digital */
    h1, h2, h3, .rbr-label, .st-activity-title, .st-drag-label {{
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px !important;"
    }}
    </style>
""", unsafe_allow_html=True)

# app router
if st.session_state.selection == "Home":
    from modules.views import home
    home.show()

elif st.session_state.selection == "History":
    from modules.views import history
    history.show()

elif st.session_state.selection == "Pit Stop":
    from modules.views import entry
    entry.show()

elif st.session_state.selection == "Methods":
    from modules.views import methods
    methods.show()