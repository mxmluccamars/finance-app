import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME

def show(method_id):
    # --- CONEXÃO E DADOS ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Buscamos os dados necessários para o cruzamento
    df_trans = conn.read(worksheet="transactions", ttl="10s")
    df_methods = conn.read(worksheet="payment_methods", ttl="1h")
    df_cats = conn.read(worksheet="categories", ttl="1h")
    df_types = conn.read(worksheet="payment_types", ttl="1h")

    # Obtemos as informações específicas deste método
    method_info = df_methods[df_methods['id'] == method_id].iloc[0]
    method_type = df_types[df_types['id'] == method_info['type_id']].iloc[0]
    
    # --- UI: CABEÇALHO DO SCANNER ---
    color = method_info.get('color', THEME['accent_1'])
    
    st.markdown(f"""
        <style>
        .detail-header {{
            background: linear-gradient(135deg, {color}44, #061D39);
            padding: 25px;
            border-radius: 15px;
            border-left: 8px solid {color};
            margin-bottom: 25px;
        }}
        .method-badge {{
            background-color: rgba(255,255,255,0.1);
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
            color: {color};
        }}
        </style>
        <div class="detail-header">
            <div class="method-badge">{method_type['name']}</div>
            <h2 style="margin: 5px 0 0 0; color: white;">{method_info['name']}</h2>
            <div style="font-size: 14px; opacity: 0.8; margin-top: 5px;">Detailed Stint Analysis</div>
        </div>
    """, unsafe_allow_html=True)

    # --- PROCESSAMENTO ---
    # Filtramos e cruzamos com as categorias para exibir ícones e cores
    df_filtered = df_trans[df_trans['method_id'] == method_id].copy()
    df_filtered = df_filtered.merge(df_cats, left_on='cat_id', right_on='id', suffixes=('', '_cat'))
    df_filtered['date'] = pd.to_datetime(df_full['date'])
    df_filtered = df_filtered.sort_values('date', ascending=False)

    # --- LISTAGEM DE TRANSAÇÕES ---
    if df_filtered.empty:
        st.info(f"Nenhum registro encontrado para {method_info['name']} nesta temporada.")
    else:
        st.write(f"### Activity Log ({len(df_filtered)} entries)")
        
        for _, row in df_filtered.iterrows():
            # Lógica de cor baseada no tipo do método (In vs Out)
            is_positive = str(method_type['impact']).strip().lower() in ['in', 'inflow']
            val_color = "#2ECC71" if is_positive else "#FFFFFF"
            val_prefix = "+" if is_positive else "-"

            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span class="material-symbols-outlined" style="color: {row['color']}; font-size: 28px;">
                            {row['icon']}
                        </span>
                        <div>
                            <div style="font-weight: 500; font-size: 16px; color: white;">{row['desc']}</div>
                            <div style="font-size: 11px; color: gray;">
                                {row['date'].strftime('%d %b, %Y')} • {row['name']}
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {val_color}; font-weight: bold; font-size: 16px;">
                            {val_prefix} R$ {row['amount']:,.2f}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Botão de retorno
    if st.button("⬅️ BACK TO GARAGE"):
        st.session_state.method_focus = None
        st.rerun()