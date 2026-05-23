import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.utils import THEME, render_quick_actions
from modules.database import FinancialDB

import textwrap

def show():
    # DB engine
    db = FinancialDB()
    df_full = db.get_full_telemetry()
    df_profile = db.get_profile()
    
    # DB is null?
    if df_full.empty:
        st.warning("No telemetry data found. Start your first stint! 🏎️")
        if st.button("🛠️ Go to Pit Stop"):
            st.session_state.selection = "Novo Gasto"
            st.rerun()
        return

    # date navegation
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.now().replace(day=1)

    # net worth total 
    net_worth = df_full['real_amount'].sum()
    
    # month filter
    view_date = st.session_state.view_date
    df_month = df_full[(df_full['date'].dt.month == view_date.month) &
                       (df_full['date'].dt.year == view_date.year)]
    
    # month metrics
    month_out = df_month[df_month['real_amount'] < 0]['amount'].sum()
    month_balance = df_month['real_amount'].sum()
    
    # budget limit
    budget_limit = float(df_profile.iloc[0]['monthly_budget_limit']) if not df_profile.empty else 0
    remaining_budget = budget_limit - month_out

    # css

    # --- CSS DO HEADER CENTRALIZADO (LOGO EXPANDIDO) ---
    st.markdown("""
        <style>
        /* Mantém o topo colado no limite da tela */
        .block-container { 
            padding-top: 0rem !important; 
        }
        
        .rbr-logo-centered-wrapper {
            display: flex !important;
            flex-direction: row !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            padding: 0px !important; 
            margin-top: -10px !important; /* Ajustado para compensar a nova altura */
            border-bottom: none !important;
            margin-bottom: 20px !important; 
        }
        
        .rbr-logo-img-centered {
            /* AQUI: Aumentamos de 38px para 65px para dar mais presença na tela */
            height: 65px !important; 
            width: auto !important;
            object-fit: contain;
            margin: 0 !important;
            padding: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- INJEÇÃO DO HTML RECALIBRADO ---
    st.markdown("""
        <div class="rbr-logo-centered-wrapper">
            <img class="rbr-logo-img-centered" src="https://upload.wikimedia.org/wikipedia/commons/6/62/RED_BULL_LOGO_2026.svg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original" alt="Red Bull Racing Logo">
        </div>
    """, unsafe_allow_html=True)

    # --- CSS DEFINITIVO GRID RESPONSIVO (20% | 60% | 20%) ---
    st.markdown("""
        <style>
        .block-container { padding-top: 1.5rem !important; padding-bottom: 0rem !important; }
        
        /* FORÇA O CONTAINER PAI A SER UM GRID RÍGIDO DE 3 COLUNAS
           Garante que as proporções propostas (20% / 60% / 20%) sejam respeitadas 
           mesmo em ecrãs extremamente estreitos, sem nunca quebrar linha.
        */
        div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: 20% 60% 20% !important;
            align-items: center !important;
            gap: 4px !important;
            width: 100% !important;
        }

        /* Anula o comportamento flex individual das colunas nativas do Streamlit */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            max-width: 100% !important;
            flex: none !important;
            padding: 0px !important;
            margin: 0px !important;
        }

        /* Estilização imersiva dos botões de navegação */
        div[data-testid="stColumn"] button {
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important; 
            padding: 0px !important;
            width: 100% !important;
            min-height: 40px !important;
            height: 40px !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        div[data-testid="stColumn"] button:hover {
            border-color: #FFCC00 !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Caixa central do display do mês */
        .date-container {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 40px;
            background-color: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            width: 100%;
            box-sizing: border-box;
        }
        
        .date-display { 
            font-size: 12px !important; /* Calibrado perfeitamente para caber 'SETEMBRO 2026' em telas pequenas */
            font-weight: 700 !important; 
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: white; 
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        </style>
    """, unsafe_allow_html=True)

    # Declaramos st.columns(3) para criar a infraestrutura de 3 colunas no HTML.
    # O nosso CSS Grid injetado acima vai anular o comportamento padrão e assumir as rédeas.
    c_prev, c_date, c_next = st.columns(3)
    
    with c_prev:
        if st.button("◀", key="btn_prev"):
            st.session_state.view_date = (st.session_state.view_date - timedelta(days=1)).replace(day=1)
            st.rerun()
            
    with c_date:
        st.markdown(f"""
            <div class='date-container'>
                <div class='date-display'>{st.session_state.view_date.strftime('%B %Y')}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c_next:
        if st.button("▶", key="btn_next"):
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
    render_quick_actions()

    # --- RECENT ACTIVITY ---
    st.write("### Recent Activity")
    recent = df_full.sort_values(by='date', ascending=False).head(10)
    
    for _, row in recent.iterrows():
        cat_color = row['color_cat'] if row['color_cat'] else "#FFFFFF"
        cat_icon = row['icon'] if row['icon'] else "payments"
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