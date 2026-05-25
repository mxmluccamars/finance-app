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
    <style>
    .stApp {{
        background-color: #0b111e; /* background color of the app */
        color: {THEME['text_main']};
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