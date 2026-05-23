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
    Usa botões nativos do Streamlit acoplados ao Google Material Icons via CSS.
    Design minimalista ultra-clean: apenas ícone e nome principal da ação.
    """
    # --- INJEÇÃO DE CSS RECALIBRADO (MINIMALISTA) ---
    st.markdown(f"""
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
        <style>
        /* Força linha horizontal rígida */
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 6px !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
            flex: 1 1 33.33% !important;
            min-width: 33.33% !important;
            max-width: 33.33% !important;
            width: 33.33% !important;
        }}
        /* Estilização Base dos Botões (Otimizado para Texto Único) */
        div[data-testid="stColumn"] button {{
            height: 75px !important;
            min-height: 75px !important;
            background-color: rgba(255, 255, 255, 0.01) !important;
            border-radius: 12px !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 11px !important;     /* Aumentamos levemente a fonte do título */
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            white-space: nowrap !important; /* Texto sempre em linha única */
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 8px !important;
            gap: 6px !important;            /* Espaço perfeito entre ícone e texto */
        }}
        /* INJEÇÃO DOS ÍCONES VIA PSEUDO-ELEMENTO (:before) */
        div[data-testid="stColumn"] button::before {{
            font-family: 'Material Symbols Outlined' !important;
            font-size: 24px !important;
            font-weight: normal !important;
            font-style: normal !important;
            display: inline-block !important;
            line-height: 1 !important;
            text-transform: none !important;
            letter-spacing: normal !important;
            word-wrap: normal !important;
            white-space: nowrap !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
        }}
        /* Customização por Posição (Borda + Ícone específico) */
        /* 1. PIT STOP (Vermelho) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button {{
            border: 2px solid #E0001A !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button::before {{
            content: "mode_standby" !important;
            color: #E0001A !important;
        }}
        /* 2. TELEMETRY (Amarelo) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button {{
            border: 2px solid #FFCC00 !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button::before {{
            content: "monitoring" !important;
            color: #FFCC00 !important;
        }}
        /* 3. TYRES (Branco) */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button {{
            border: 2px solid #FFFFFF !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button::before {{
            content: "credit_card" !important;
            color: #FFFFFF !important;
        }}
        /* Hovers Suaves */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button:hover {{ background-color: rgba(224, 0, 26, 0.08) !important; }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:hover {{ background-color: rgba(255, 204, 0, 0.08) !important; }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button:hover {{ background-color: rgba(255, 255, 255, 0.06) !important; }}
        </style>
    """, unsafe_allow_html=True)

    # Label de Rádio Check
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 15px; margin-bottom: 12px;">
            <span class="material-symbols-outlined" style="color: {THEME['accent_1']}; font-size: 20px;">graphic_eq</span>
            <span style="color: {THEME['accent_1']}; font-weight: bold; letter-spacing: 1.5px; font-size: 11px; text-transform: uppercase;">Radio Check: Lucca</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Renderização sem as legendas secundárias
    col_pit, col_telemetry, col_setup = st.columns(3)
    
    with col_pit:
        if st.button("PIT STOP", key="tyre_btn_pit", use_container_width=True):
            st.session_state.selection = "Novo Gasto"
            st.rerun()
            
    with col_telemetry:
        if st.button("TELEMETRY", key="tyre_btn_history", use_container_width=True):
            st.session_state.selection = "History"
            st.rerun()
            
    with col_setup:
        if st.button("TYRES", key="tyre_btn_methods", use_container_width=True):
            st.session_state.selection = "Methods"
            st.rerun()