import streamlit as st
import pandas as pd
from datetime import datetime
from modules.utils import THEME
from modules.database import FinancialDB
from modules.views import method_detail

def show():
    # --- ENGINE DE DADOS ---
    db = FinancialDB()
    df_full = db.get_full_telemetry()
    
    # 1. VERIFICAÇÃO DE NAVEGAÇÃO (Drill-down)
    if 'method_focus' not in st.session_state:
        st.session_state.method_focus = None

    # Se houver um método focado, renderizamos a tela de detalhe e paramos por aqui
    if st.session_state.method_focus is not None:
        method_detail.show(st.session_state.method_focus)
        return # Importante para não renderizar a lista de cards embaixo

    # --- UI & CSS (O "Sanduíche" de camadas) ---
    st.markdown(f"""
        <style>
        .card-container {{
            position: relative;
            height: 140px;
            margin-bottom: 20px;
        }}
        .method-card-visual {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            z-index: 1; /* Camada de baixo (Visual) */
            transition: 0.3s ease;
        }}
        /* Botão invisível que cobre tudo */
        div[data-testid="stButton"] > button[key^="card_"] {{
            width: 100% !important;
            height: 140px !important;
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            position: absolute;
            top: 0; left: 0;
            z-index: 10; /* Camada de cima (Clique) */
            cursor: pointer;
        }}
        .card-container:hover .method-card-visual {{
            border-color: {THEME['accent_1']};
            transform: translateY(-3px);
            background: rgba(255,255,255,0.05);
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 💳 Payment Methods")
    
    # Buscamos as tabelas para montar os cards
    df_methods = db.get_methods()
    df_types = db.conn.read(worksheet="payment_types", ttl="1h")
    df_m_info = df_methods.merge(df_types, left_on='type_id', right_on='id', suffixes=('', '_type'))

    cols = st.columns(2)
    for i, row in df_m_info.iterrows():
        with cols[i % 2]:
            color = row.get('color', THEME['primary'])
            
            # Cálculo de saldo atual do método (usando a engine centralizada)
            total_val = df_full[df_full['method_id'] == row['id']]['real_amount'].sum()

            # HTML do Card
            st.markdown(f"""
                <div class="card-container">
                    <div class="method-card-visual" style="border-left: 5px solid {color};">
                        <div>
                            <div style="font-size: 10px; opacity: 0.6; text-transform: uppercase;">{row['name_type']}</div>
                            <div style="font-size: 18px; font-weight: bold;">{row['name']}</div>
                        </div>
                        <div style="font-size: 20px; font-weight: 800; font-family: 'Courier New', monospace;">
                            R$ {total_val:,.2f}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # O Botão que ativa a lógica
            if st.button("🔍", key=f"card_{row['id']}"):
                st.session_state.method_focus = row['id']
                st.rerun()

    # Botão para voltar (caso queira sair da tela de métodos)
    if st.button("⬅️ BACK TO PADDOCK"):
        st.session_state.selection = "Home"
        st.rerun()