import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME
from modules.views import method_detail

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
        
        /* Container precisa ser relativo para o botão absoluto se ancorar nele */
        .card-container {{
            position: relative;
            height: 150px;
            margin-bottom: 20px;
        }}

        /* O visual do card que fica NO FUNDO */
        .method-card-visual {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: 0.3s;
            z-index: 1; /* Fica atrás */
        }}

        /* O botão invisível que fica NA FRENTE de tudo */
        div.stButton > button {{
            width: 100%;
            height: 150px;
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            position: absolute;
            top: 0; left: 0;
            z-index: 100; /* Z-index alto para garantir o clique */
            cursor: pointer;
        }}

        /* Efeito de hover simulado no container quando o botão recebe foco */
        .card-container:hover .method-card-visual {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.3);
        }}
        </style>
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
       method_detail.show(st.session_state.method_focus)