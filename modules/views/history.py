import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.utils import THEME
from modules.database import FinancialDB

def show():
    # --- ENGINE DE DADOS (Centralizado) ---
    db = FinancialDB()
    df_full = db.get_full_telemetry() # Já vem com todos os joins e real_amount calculado

    # --- UI & CSS CUSTOM ---
    st.markdown(f"""
        <style>
        .block-container {{ padding-top: 1rem !important; }}
        
        /* Estilo Paddock Button */
        div[data-testid="stButton"] > button {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-left: 5px solid {THEME['accent_1']} !important;
            color: white !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            width: 100%;
            transition: 0.3s;
        }}
        div[data-testid="stButton"] > button:hover {{
            border-left: 5px solid {THEME['accent_2']} !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }}
        
        .date-display {{ font-size: 22px; font-weight: 800; text-align: center; color: white; padding: 10px 0; }}
        </style>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    """, unsafe_allow_html=True)

    # --- TOPO: BOTÃO PADDOCK ---
    if st.button("⬅️ RETURN TO PADDOCK (HOME)"):
        st.session_state.selection = "Home"
        st.rerun()

    st.divider()

    # --- NAVEGAÇÃO DE MÊS ---
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.now().replace(day=1)

    c_prev, c_date, c_next = st.columns([0.5, 4, 0.5])
    with c_prev:
        if st.button("◀", key="log_prev"):
            st.session_state.view_date = (st.session_state.view_date - timedelta(days=1)).replace(day=1)
            st.rerun()
    with c_date:
        st.markdown(f"<div class='date-display'>{st.session_state.view_date.strftime('%B %Y').upper()}</div>", unsafe_allow_html=True)
    with c_next:
        if st.button("▶", key="log_next"):
            st.session_state.view_date = (st.session_state.view_date + timedelta(days=32)).replace(day=1)
            st.rerun()

    # --- FILTRAGEM E EXIBIÇÃO ---
    if df_full.empty:
        st.info("No telemetry recorded yet.")
        return

    # Filtro de Data baseado no seletor
    view_date = st.session_state.view_date
    df_month = df_full[(df_full['date'].dt.month == view_date.month) & 
                       (df_full['date'].dt.year == view_date.year)].copy()
    
    df_month = df_month.sort_values(by='date', ascending=False)

    st.markdown("### 🏁 Transaction Log")

    if df_month.empty:
        st.info("No data for this stint.")
    else:
        for _, row in df_month.iterrows():
            # Usamos a lógica de sinal já processada pela Engine no real_amount
            is_positive = row['real_amount'] >= 0
            color_val = "#2ECC71" if is_positive else THEME['accent_2']
            prefix = "+" if is_positive else "-"
            
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span class="material-symbols-outlined" style="color: {row['color_cat']}; font-size: 28px;">
                            {row['icon']}
                        </span>
                        <div>
                            <div style="font-weight: 500; font-size: 15px; color: white;">{row['desc']}</div>
                            <div style="font-size: 11px; color: #888;">
                                {row['date'].strftime('%d %b')} • {row['name']}
                            </div>
                        </div>
                    </div>
                    <div style="color: {color_val}; font-weight: bold; font-size: 16px; font-family: 'Courier New', monospace;">
                        {prefix} R$ {row['amount']:,.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)