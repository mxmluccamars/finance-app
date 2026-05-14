import streamlit as st
import pandas as pd
from modules.utils import THEME
from modules.database import FinancialDB

def show(method_id):
    # --- ENGINE DE DADOS (Consumindo Cache) ---
    db = FinancialDB()
    df_full = db.get_full_telemetry() # Já possui todos os joins e real_amount
    
    # Buscamos as informações do método específico na tabela de referência
    df_methods = db.get_methods()
    method_info = df_methods[df_methods['id'] == method_id].iloc[0]
    
    # --- UI: CABEÇALHO PERSONALIZADO ---
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
            <div class="method-badge">Telemetry Analysis</div>
            <h2 style="margin: 5px 0 0 0; color: white;">{method_info['name']}</h2>
            <div style="font-size: 14px; opacity: 0.8; margin-top: 5px;">Detailed Stint Overview</div>
        </div>
    """, unsafe_allow_html=True)

    # --- PROCESSAMENTO ---
    # Filtramos as transações apenas deste método
    df_filtered = df_full[df_full['method_id'] == method_id].copy()
    df_filtered = df_filtered.sort_values('date', ascending=False)

    # --- LISTAGEM DE TRANSAÇÕES ---
    if df_filtered.empty:
        st.info(f"Nenhum registro encontrado para {method_info['name']} nesta temporada.")
    else:
        st.write(f"### Activity Log ({len(df_filtered)} entries)")
        
        for _, row in df_filtered.iterrows():
            # Usamos a lógica de sinal já processada pela Engine
            is_positive = row['real_amount'] >= 0
            val_color = "#2ECC71" if is_positive else "#FFFFFF"
            val_prefix = "+" if is_positive else "-"

            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span class="material-symbols-outlined" style="color: {row['color_cat']}; font-size: 28px;">
                            {row['icon']}
                        </span>
                        <div>
                            <div style="font-weight: 500; font-size: 16px; color: white;">{row['desc']}</div>
                            <div style="font-size: 11px; color: gray;">
                                {row['date'].strftime('%d %b, %Y')} • {row['name_cat']}
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