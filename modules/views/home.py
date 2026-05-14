import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.utils import THEME
from modules.database import FinancialDB
import textwrap

def show():
    # --- ENGINE DE DADOS (Centralizado) ---
    db = FinancialDB()
    df_full = db.get_full_telemetry()
    df_profile = db.get_profile()
    
    # Verificação de segurança caso o banco esteja vazio
    if df_full.empty:
        st.warning("No telemetry data found. Start your first stint! 🏎️")
        if st.button("🛠️ Go to Pit Stop"):
            st.session_state.selection = "Novo Gasto"
            st.rerun()
        return

    # --- CONTROLO DE NAVEGAÇÃO DE DATA ---
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.now().replace(day=1)

    # --- CÁLCULOS TÉCNICOS ---
    # Net Worth Total (Independente do mês selecionado)
    net_worth = df_full['real_amount'].sum()
    
    # Filtragem do Mês selecionado
    view_date = st.session_state.view_date
    df_month = df_full[(df_full['date'].dt.month == view_date.month) & 
                       (df_full['date'].dt.year == view_date.year)]
    
    # Métricas do Mês
    month_out = df_month[df_month['real_amount'] < 0]['amount'].sum()
    month_balance = df_month['real_amount'].sum()
    
    # Budget (Vindo do Perfil)
    budget_limit = float(df_profile.iloc[0]['monthly_budget_limit']) if not df_profile.empty else 0
    remaining_budget = budget_limit - month_out

    # --- CSS E NAVEGAÇÃO ---
    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem !important; padding-bottom: 0rem !important; }
        div[data-testid="stColumn"] button[kind="secondary"] {
            border: none !important; background-color: transparent !important;
            box-shadow: none !important; color: white !important; padding: 0px !important;
        }
        .date-display { font-size: 20px; font-weight: 600; text-align: center; line-height: 40px; color: white; }
        </style>
    """, unsafe_allow_html=True)

    # Seletor de Mês (Navegação da Temporada)
    c_prev, c_date, c_next = st.columns([0.5, 4, 0.5])
    with c_prev:
        if st.button("", icon=":material/chevron_left:", key="btn_prev"):
            st.session_state.view_date = (st.session_state.view_date - timedelta(days=1)).replace(day=1)
            st.rerun()
    with c_date:
        st.markdown(f"<div class='date-display'>{st.session_state.view_date.strftime('%B - %Y')}</div>", unsafe_allow_html=True)
    with c_next:
        if st.button("", icon=":material/chevron_right:", key="btn_next"):
            st.session_state.view_date = (st.session_state.view_date + timedelta(days=32)).replace(day=1)
            st.rerun()

    # --- UI: MAIN CARD (RBR TELEMETRY) ---
    budget_usage_pct = min((month_out / budget_limit) * 100, 100) if budget_limit > 0 else 0
    budget_color = THEME['accent_2'] if month_out > budget_limit else THEME['accent_1']
    
    left_val_html = f"R$ {remaining_budget:,.2f} <span style='font-size: 12px; opacity: 0.7;'>left</span>"
    right_val_html = f"R$ {month_balance:,.2f}"
    
    if df_month.empty:
        left_val_html = "<span style='font-size: 16px; opacity: 0.8;'>Clear track ahead...</span>"
        right_val_html = "<span style='font-size: 16px; font-style: italic;'>Standing by...</span>"

    st.markdown(textwrap.dedent(f"""
        <style>
        .main-card {{ background-color: {THEME['primary']}; padding: 25px; border-radius: 20px; color: {THEME['text_main']}; border-left: 8px solid {THEME['accent_1']}; position: relative; }}
        .logo-container {{ position: absolute; top: 20px; right: 25px; width: 75px; opacity: 0.9; }}
        .label {{ font-size: 11px; color: {THEME['accent_1']}; text-transform: uppercase; font-weight: bold; }}
        .value {{ font-size: 32px; font-weight: 800; margin-bottom: 15px; }}
        .budget-container {{ background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin-top: 10px; }}
        .progress-bar {{ background-color: rgba(255, 255, 255, 0.2); height: 8px; border-radius: 4px; margin: 10px 0; overflow: hidden; }}
        .progress-fill {{ background-color: {budget_color}; width: {budget_usage_pct}%; height: 100%; }}
        .header-row {{ display: flex; justify-content: space-between; align-items: center; }}
        </style>
        <div class="main-card">
            <img src="https://www.svgrepo.com/show/303227/redbull-logo.svg" class="logo-container">
            <div class="label">Total Net Worth</div>
            <div class="value">R$ {net_worth:,.2f}</div>
            <div class="budget-container">
                <div class="header-row">
                    <div class="label" style="color: white; opacity: 0.6;">Budget for {view_date.strftime('%b')}</div>
                    <div class="label" style="color: white; opacity: 0.6;">Monthly Balance</div>
                </div>
                <div class="header-row">
                    <div style="font-size: 20px; font-weight: 700;">{left_val_html}</div>
                    <div style="font-size: 20px; font-weight: 700; color: {'#2ECC71' if month_balance >= 0 else THEME['accent_2']};">{right_val_html}</div>
                </div>
                <div class="progress-bar"><div class="progress-fill"></div></div>
                <div class="header-row" style="font-size: 11px; opacity: 0.8;">
                    <span>Spent: R$ {month_out:,.2f}</span>
                    <span>Limit: R$ {budget_limit:,.2f}</span>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # --- QUICK ACTIONS ---
    st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
    st.markdown(f'<div style="display: flex; align-items: center; gap: 10px; margin-top: 20px;"><span class="material-symbols-outlined" style="color: {THEME["accent_1"]}; font-size: 24px;">graphic_eq</span><span style="color: {THEME["accent_1"]}; font-weight: bold; letter-spacing: 1.5px; font-size: 13px; text-transform: uppercase;">Radio Check: Lucca</span></div>', unsafe_allow_html=True)
    
    col_pit, col_telemetry, col_setup = st.columns(3)
    with col_pit:
        if st.button("🛠️\nPIT STOP", use_container_width=True):
            st.session_state.selection = "Novo Gasto"; st.rerun()
    with col_telemetry:
        if st.button("📊\nDATA LOG", use_container_width=True):
            st.session_state.selection = "Statement"; st.rerun()
    with col_setup:
        if st.button("🔧\nTIRES", use_container_width=True):
            st.session_state.selection = "Methods"; st.rerun()

    # --- RECENT ACTIVITY ---
    st.write("### Recent Activity")
    recent = df_full.sort_values(by='date', ascending=False).head(5)
    
    for _, row in recent.iterrows():
        cat_color = row['color_cat'] if row['color_cat'] else "#FFFFFF"
        cat_icon = row['icon'] if row['icon'] else "payments"
        # Usamos o sinal real do cálculo da engine
        impact_color = "#2ECC71" if row['real_amount'] >= 0 else THEME['accent_2']
        prefix = "+" if row['real_amount'] >= 0 else "-"
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="material-symbols-outlined" style="color: {cat_color}; font-size: 28px;">{cat_icon}</span>
                    <div>
                        <div style="font-weight: 500; font-size: 15px; color: white;">{row['desc']}</div>
                        <div style="font-size: 11px; color: gray;">{row['date'].strftime('%d %b')} • {row['name']}</div>
                    </div>
                </div>
                <div style="color: {impact_color}; font-weight: bold; font-size: 15px;">
                    {prefix} R$ {row['amount']:,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)