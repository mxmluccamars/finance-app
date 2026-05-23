import streamlit as st

THEME = {
    "primary": "#061D39",
    "accent_1": "#FFCC00",  # Amarelo RBR
    "accent_2": "#E0001A",  # Vermelho RBR
    "text_main": "#FFFFFF"
}

def render_quick_actions():
    """
    Componente padrão de ações rápidas.
    Usa botões 100% nativos do Streamlit com CSS ultra-responsivo,
    garantindo que as 3 colunas fiquem na horizontal mesmo no celular.
    """
    # --- INJEÇÃO DE CSS BLINDADO CONTRA EMPILHAMENTO ---
    st.markdown(f"""
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
        <style>
        /* FORÇA O CONTAINER DAS COLUNAS A FICAR EM LINHA HORIZONTAL NO MOBILE */
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important; /* Impede o empilhamento vertical */
            flex-wrap: nowrap !important;   /* Força linha única */
            width: 100% !important;
            gap: 6px !important;            /* Espaço sutil entre os botões */
        }}
        /* Força cada coluna a ocupar exatamente 1/3 do espaço disponível */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
            flex: 1 1 33.33% !important;
            min-width: 33.33% !important;
            max-width: 33.33% !important;
            width: 33.33% !important;
        }}
        /* Estilização dos Botões Nativos do Streamlit */
        div[data-testid="stColumn"] button {{
            height: 75px !important;        /* Altura compacta ideal para mobile */
            min-height: 75px !important;
            background-color: rgba(255, 255, 255, 0.02) !important;
            border-radius: 12px !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 10px !important;     /* Fonte menor para garantir que cabe o texto em linha única */
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            white-space: normal !important; /* Permite a quebra de linha do texto (\n) */
            word-wrap: break-word !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 4px !important;
        }}
        /* Bordas Coloridas por Posição (Pirelli Style) */
        /* 1. Pit Stop (Soft - Vermelho) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button {{
            border: 2px solid #E0001A !important;
        }}
        /* 2. Telemetry (Medium - Amarelo) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button {{
            border: 2px solid #FFCC00 !important;
        }}
        /* 3. Tyres (Hard - Branco) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button {{
            border: 2px solid #FFFFFF !important;
        }}
        /* Efeitos de Hover/Toque */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button:hover {{ background-color: rgba(224, 0, 26, 0.08) !important; }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:hover {{ background-color: rgba(255, 204, 0, 0.08) !important; }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button:hover {{ background-color: rgba(255, 255, 255, 0.06) !important; }}
        </style>
    """, unsafe_allow_html=True)

    # Label do Rádio Check
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 15px; margin-bottom: 12px;">
            <span class="material-symbols-outlined" style="color: {THEME['accent_1']}; font-size: 20px;">graphic_eq</span>
            <span style="color: {THEME['accent_1']}; font-weight: bold; letter-spacing: 1.5px; font-size: 11px; text-transform: uppercase;">Radio Check: Lucca</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Gerador das colunas nativas
    col_pit, col_telemetry, col_setup = st.columns(3)
    
    with col_pit:
        if st.button("🛠️\nPIT STOP\n(SOFT)", key="tyre_btn_pit", use_container_width=True):
            st.session_state.selection = "Novo Gasto"
            st.rerun()
            
    with col_telemetry:
        if st.button("📊\nTELEMETRY\n(MEDIUM)", key="tyre_btn_history", use_container_width=True):
            st.session_state.selection = "History"
            st.rerun()
            
    with col_setup:
        if st.button("🔧\nTYRES\n(HARD)", key="tyre_btn_methods", use_container_width=True):
            st.session_state.selection = "Methods"
            st.rerun()