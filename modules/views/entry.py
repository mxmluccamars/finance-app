import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME
import time

def show():
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Carregamos as tabelas de referência
    df_cats = conn.read(worksheet="categories", ttl="1h")
    df_methods = conn.read(worksheet="payment_methods", ttl="1h")
    
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
            # 2. MÉTODO DE PAGAMENTO (Define o fluxo automaticamente)
            method_options = df_methods['name'].tolist()
            method_selected = st.selectbox("Payment Method", options=method_options)
        
        with col2:
            # 3. CATEGORIA (Skins, Fuel, Salary, etc.)
            cat_options = df_cats['name'].tolist()
            category_selected = st.selectbox("Compound (Category)", options=cat_options)

        # 4. DESCRIÇÃO E DATA
        description = st.text_input("Description", placeholder="Ex: Burger, Fuel, Salary...")
        date = st.date_input("Race Date", value=datetime.now())

        submitted = st.form_submit_button("🏁 CONFIRM STINT")

        if submitted:
            if amount > 0 and description:
                # --- BUSCA DE IDs (Mapeamento) ---
                # Pegamos o ID do método e da categoria baseados no nome selecionado
                m_id = df_methods[df_methods['name'] == method_selected]['id'].values[0]
                c_id = df_cats[df_cats['name'] == category_selected]['id'].values[0]

                new_entry = pd.DataFrame([{
                    "id": int(time.time()), # Transaction ID
                    "date": date.strftime("%Y-%m-%d"),
                    "desc": description,
                    "amount": amount,
                    "cat_id": c_id,
                    "method_id": m_id,
                    "user_id": 1
                }])
                
                try:
                    # Lemos apenas para dar o append (usando ttl=0 para garantir que não pule IDs)
                    df_existing = conn.read(worksheet="transactions", ttl=0)
                    updated_df = pd.concat([df_existing, new_entry], ignore_index=True)
                    conn.update(worksheet="transactions", data=updated_df)
                    
                    # Redirecionamento direto
                    st.session_state.selection = "Home"
                    st.rerun()
                except Exception as e:
                    st.error(f"Engine failure: {e}")
            else:
                st.warning("Telemetry incomplete! Check amount and description.")

    if st.button("📻 BOX BOX (Cancel)"):
        st.session_state.selection = "Home"
        st.rerun()