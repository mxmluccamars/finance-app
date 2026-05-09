import streamlit as st
from modules.views import home, entry, history

# Esconde a barra lateral nativa e o menu do topo para parecer um app
st.set_page_config(page_title="RBR Finance", layout="wide", page_icon="🏎️")

st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;} /* Esconde a sidebar */
        #MainMenu {visibility: hidden;} /* Esconde o menu de 3 pontinhos */
        header {visibility: hidden;} /* Esconde o header do Streamlit */
    </style>
""", unsafe_allow_html=True)

# Gerenciamento de Navegação
if 'selection' not in st.session_state:
    st.session_state.selection = "Home"

# Roteador Simples
if st.session_state.selection == "Home":
    home.show()
elif st.session_state.selection == "Novo Gasto":
    entry.show()
elif st.session_state.selection == "Statement":
    history.show()

# Botão de Voltar Global (opcional para telas que não sejam a Home)
if st.session_state.selection != "Home":
    if st.button("⬅ Back to Home"):
        st.session_state.selection = "Home"
        st.rerun()