import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME

def show():
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df_trans = conn.read(worksheet="transactions", ttl="10s")
    df_methods = conn.read(worksheet="payment_methods", ttl="1h")
    df_cats = conn.read(worksheet="categories", ttl="1h")
    df_types = conn.read(worksheet="payment_types", ttl="1h")

    if 'method_focus' not in st.session_state:
        st.session_state.method_focus = None

    # --- CSS: TRICK PARA CARD CLICÁVEL ---
    st.markdown(f"""
        <style>
        .block-container {{ padding-top: 1.5rem !important; }}
        
        /* Estilização do Container do Card */
        .card-container {{
            position: relative;
            margin-bottom: 20px;
        }}

        /* O botão invisível que cobre o card todo */
        div.stButton > button {{
            width: 100%;
            height: 150px; /* Altura do card */
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            position: absolute;
            z-index: 10;
        }}

        /* O visual do card que fica por baixo do botão */
        .method-card-visual {{
            padding: 20px;
            border-radius: 15px;
            height: 150px;
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: 0.3s;
        }}
        .method-card-visual:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.3);
        }}
        </style>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    """, unsafe_allow_html=True)

    if st.session_state.method_focus is None:
        st.markdown("## 💳 Payment Methods")
        
        df_m_info = df_methods.merge(df_types, left_on='type_id', right_on='id', suffixes=('', '_type'))
        
        cols = st.columns(2)
        for i, row in df_m_info.iterrows():
            with cols[i % 2]:
                color = row.get('color', '#444')
                impact_type = str(row.get('impact', 'Out')).strip().lower()
                
                # Cálculo do total do mês
                current_month = datetime.now().month
                total_val = df_trans[
                    (df_trans['method_id'] == row['id']) & 
                    (pd.to_datetime(df_trans['date']).dt.month == current_month)
                ]['amount'].sum()

                # A MÁGICA ACONTECE AQUI:
                # 1. Desenhamos o visual do card
                # 2. Colocamos o botão por cima
                st.markdown(f"""
                    <div class="card-container">
                        <div class="method-card-visual" style="background: linear-gradient(135deg, {color}66, #061D39); border-left: 6px solid {color};">
                            <div>
                                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0.7;">{row['name_type']}</div>
                                <div style="font-size: 20px; font-weight: 800; margin-top: 5px;">{row['name']}</div>
                            </div>
                            <div style="font-size: 22px; font-weight: bold; color: {'#2ECC71' if impact_type in ['in', 'inflow'] else 'white'};">
                                R$ {total_val:,.2f}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botão invisível que detecta o clique
                if st.button("", key=f"card_btn_{row['id']}"):
                    st.session_state.method_focus = row['id']
                    st.rerun()

    else:
        # --- TELA DE DETALHES (DRILL-DOWN) ---
        m_id = st.session_state.method_focus
        m_row = df_methods[df_methods['id'] == m_id].iloc[0]

        # Botão de voltar estilizado (como o do Paddock)
        if st.button("⬅️ BACK TO METHODS"):
            st.session_state.method_focus = None
            st.rerun()

        st.markdown(f"### 🔍 Telemetry: {m_row['name']}")
        
        df_full = df_trans[df_trans['method_id'] == m_id].merge(df_cats, left_on='cat_id', right_on='id', suffixes=('', '_cat'))
        df_full['date'] = pd.to_datetime(df_full['date'])
        df_full = df_full.sort_values('date', ascending=False)

        if df_full.empty:
            st.info("Nenhuma transação registrada.")
        else:
            for _, row in df_full.iterrows():
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span class="material-symbols-outlined" style="color: {row['color']}; font-size: 24px;">{row['icon']}</span>
                            <div>
                                <div style="font-size: 14px; font-weight: 500;">{row['desc']}</div>
                                <div style="font-size: 10px; color: gray;">{row['date'].strftime('%d %b')}</div>
                            </div>
                        </div>
                        <div style="font-weight: bold;">R$ {row['amount']:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)