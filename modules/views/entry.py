import streamlit as st
import pandas as pd
from datetime import datetime
from modules.utils import THEME
from modules.database import FinancialDB
import time

def show():
    # --- ENGINE DE DADOS (Centralizado) ---
    db = FinancialDB()
    
    # Carregamos apenas os dados estáticos necessários para os seletores (com cache de 1h)
    df_cats = db.get_categories()
    df_methods = db.get_methods()
    
    # Extraímos as opções únicas para os seletores a partir do DataFrame consolidado
    # Isso garante que apenas categorias e métodos ativos apareçam
    cat_options = df_cats['name'].tolist()
    method_options = df_methods['name'].tolist()
    
    st.markdown(f"""
        <style>
        .block-container {{ padding-top: 1.5rem !important; }}
        .pit-header {{
            background-color: {THEME['primary']};
            padding: 20px; border-radius: 15px;
            border-left: 8px solid {THEME['accent_2']};
            margin-bottom: 25px;
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="pit-header">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="material-symbols-outlined" style="color: {THEME['accent_1']};">timer</span>
                <span style="color: {THEME['accent_1']}; font-weight: bold; letter-spacing: 1.5px; font-size: 11px; text-transform: uppercase;">
                    Ultra-Fast Entry
                </span>
            </div>
            <h2 style="margin: 5px 0 0 0; color: white;">Pit Stop Entry</h2>
        </div>
    """, unsafe_allow_html=True)

    with st.form("pit_stop_form", clear_on_submit=True):
        # 1. VALOR
        amount = st.number_input("Amount (R$)", min_value=0.0, step=0.01, format="%.2f")

        col1, col2 = st.columns(2)
        with col1:
            # 2. MÉTODO DE PAGAMENTO
            method_selected = st.selectbox("Payment Method", options=method_options)
        
        with col2:
            # 3. CATEGORIA
            category_selected = st.selectbox("Compound (Category)", options=cat_options)

        # 4. DESCRIÇÃO E DATA
        description = st.text_input("Description", placeholder="Ex: Burger, Fuel, Salary...")
        date = st.date_input("Race Date", value=datetime.now())

        submitted = st.form_submit_button("🏁 CONFIRM STINT")

        if submitted:
            if amount > 0 and description:
                # --- BUSCA DE IDs PARA INTEGRIDADE ---
                # Buscamos os IDs correspondentes aos nomes selecionados no DataFrame mestre
                m_id = df_methods[df_methods['name'] == method_selected]['id'].values[0]
                c_id = df_cats[df_cats['name'] == category_selected]['id'].values[0]

                new_entry = pd.DataFrame([{
                    "id": int(time.time()), 
                    "date": date.strftime("%Y-%m-%d"),
                    "desc": description,
                    "amount": amount,
                    "cat_id": c_id,
                    "method_id": m_id,
                    "user_id": 1
                }])
                
                # Usamos a função centralizada que já lida com update e cache clear
                success = db.save_transaction(new_entry)
                
                if success:
                    st.session_state.selection = "Home"
                    st.rerun()
            else:
                st.warning("Telemetry incomplete! Check amount and description.")

    if st.button("📻 BOX BOX (Cancel)"):
        st.session_state.selection = "Home"
        st.rerun()