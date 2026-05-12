import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME

def show():
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 1. Leitura com cache para não estourar a cota
    df_trans = conn.read(worksheet="transactions", ttl="10s")
    df_methods = conn.read(worksheet="payment_methods", ttl="1h")
    df_cats = conn.read(worksheet="categories", ttl="1h")
    df_types = conn.read(worksheet="payment_types", ttl="1h")

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

    # --- PROCESSAMENTO DE DADOS (MERGE SEGURO) ---
    try:
        # Join 1: Transações + Métodos
        df_full = df_trans.merge(df_methods, left_on='method_id', right_on='id', suffixes=('', '_meth'))
        
        # Join 2: + Tipos (Aqui pegamos o 'impact')
        # Garantimos que estamos usando a coluna 'type_id' correta
        df_full = df_full.merge(df_types, left_on='type_id', right_on='id', suffixes=('', '_type'))
        
        # Join 3: + Categorias
        df_full = df_full.merge(df_cats, left_on='cat_id', right_on='id', suffixes=('', '_cat'))
        
        df_full['date'] = pd.to_datetime(df_full['date'])
        
        # Filtro de Data
        view_date = st.session_state.view_date
        df_month = df_full[(df_full['date'].dt.month == view_date.month) & 
                           (df_full['date'].dt.year == view_date.year)].copy()
        df_month = df_month.sort_values(by='date', ascending=False)

        st.markdown("### 🏁 Transaction Log")

        if df_month.empty:
            st.info("No data for this stint.")
        else:
            for _, row in df_month.iterrows():
                # AQUI ESTÁ O SEGREDO:
                # O seu print mostrou que na planilha está escrito "In"
                impact_val = str(row.get('impact', 'Out')).strip()
                
                # Ajustamos para reconhecer "In" ou "Inflow"
                is_positive = impact_val.lower() in ['in', 'inflow']
                
                color_val = "#2ECC71" if is_positive else THEME['accent_2']
                prefix = "+" if is_positive else "-"
                
                # Renderização do card (mesmo código anterior)
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
                
    except Exception as e:
        st.error(f"Telemetry Failure: {e}")