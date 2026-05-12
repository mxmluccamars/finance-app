import streamlit as st
from modules.views import home, entry, statement, methods

# Esconde a barra lateral nativa e o menu do topo para parecer um app
st.set_page_config(page_title="RBR Finance", layout="wide", page_icon="🏎️")

st.markdown("""
    <style>
        /* Esconde apenas o botão da Sidebar e o rodapé 'Made with Streamlit' */
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        footer {visibility: hidden;}
        
        /* Mantém o header mas remove a decoração colorida do topo */
        header {background-color: rgba(0,0,0,0) !important;}
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
    statement.show()
elif st.session_state.selection == "Methods":
    methods.show()

# # Botão de Voltar Global (opcional para telas que não sejam a Home)
# if st.session_state.selection != "Home":
#     if st.button("⬅ Back to Home"):
#         st.session_state.selection = "Home"
#         st.rerun()