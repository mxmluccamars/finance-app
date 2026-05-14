import streamlit as st
from modules.views import history, home, entry, methods

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO F1/RED BULL) ---
st.set_page_config(
    page_title="Kimi Finance | RBR Telemetry",
    layout="wide",
    page_icon="🏎️"
)

# --- CSS PARA ESCONDER ELEMENTOS NATIVOS E MELHORAR UX ---
st.markdown("""
    <style>
        /* Esconde a barra lateral nativa e o cabeçalho padrão */
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        footer {visibility: hidden;}
        header {background-color: rgba(0,0,0,0) !important;}
        
        /* Ajuste de padding para telas mobile/compactas */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 5rem; /* Espaço para não cobrir o conteúdo com menus futuros */
        }
    </style>
""", unsafe_allow_html=True)

# --- GERENCIAMENTO DE NAVEGAÇÃO (SESSION STATE) ---
if 'selection' not in st.session_state:
    st.session_state.selection = "Home"

# Lógica para garantir que o foco do método seja resetado ao mudar de tela
def navigate_to(page):
    st.session_state.selection = page
    if page != "Methods":
        st.session_state.method_focus = None
    st.rerun()

# --- ROTEADOR DE TELAS ---
# Aqui o app decide qual módulo de visão carregar
if st.session_state.selection == "Home":
    home.show()
    
elif st.session_state.selection == "Novo Gasto":
    entry.show()
    
elif st.session_state.selection == "Statement":
    history.show()
    
elif st.session_state.selection == "Methods":
    methods.show()

# --- BOTÃO GLOBAL DE SYNC (OPCIONAL NA SIDEBAR INVISÍVEL OU RODAPÉ) ---
# Se você quiser um botão de refresh que apareça em todas as telas:
# if st.button("🔄 Sync Cloud"):
#     st.cache_data.clear()
#     st.rerun()