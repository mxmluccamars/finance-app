import streamlit as st
from modules.views import home, entry, history

st.set_page_config(page_title="Finanças na Mão", layout="wide", page_icon="💰")

# Sidebar - Menu de Navegação
st.sidebar.title("💳 Finance App")
selection = st.sidebar.radio("Navegação", ["Home", "Novo Gasto", "Histórico"])

# Roteamento
if selection == "Home":
    home.show()
elif selection == "Novo Gasto":
    entry.show()
elif selection == "Histórico":
    history.show()