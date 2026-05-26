# imports
import streamlit as st
from modules.utils import THEME

def render(net_worth, month_out, budget_limit, month_balance, view_month_text):
    """
    Componente Estanque: Renderiza o painel de telemetria principal do cockpit.
    Isola completamente o CSS usando classes específicas para evitar vazamentos.
    """
    # percentual calculus
    budget_usage_pct = min((month_out / budget_limit) * 100, 100) if budget_limit > 0 else 0
    
    # bar color logic
    budget_color = THEME['accent_2'] if month_out > budget_limit else THEME['accent_1']
    
    # text formatting
    remaining_budget = budget_limit - month_out # budget left for the month
    left_val_html = f"R$ {remaining_budget:,.2f} <span style='font-size: 12px; opacity: 0.7;'>left</span>" 
    right_val_html = f"R$ {month_balance:,.2f}"
    
    # month balance color logic
    balance_text_color = "#00D18E" if month_balance >= 0 else THEME['accent_2']

    # css
    st.markdown(f"""
        <style>
        .rbr-main-card {{
            background-color: {THEME['primary']};
            padding: 25px;
            border-radius: 20px;
            color: {THEME['text_main']};
            border-left: 8px solid {THEME['accent_1']};
            position: relative;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }}
        .rbr-main-card .rbr-logo-bg {{
            position: absolute;
            top: 20px;
            right: 25px;
            width: 75px;
            opacity: 0.8;
        }}
        .rbr-main-card .rbr-label {{
            font-size: 11px;
            color: {THEME['accent_1']};
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .rbr-main-card .rbr-value {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 15px;
            font-family: 'Orbitron', monospace;
        }}
        .rbr-main-card .rbr-budget-container {{
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 15px;
            margin-top: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .rbr-main-card .rbr-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .rbr-main-card .rbr-progress-bar {{
            background-color: rgba(255, 255, 255, 0.1);
            height: 8px;
            border-radius: 4px;
            margin: 12px 0;
            overflow: hidden;
        }}
        .rbr-main-card .rbr-progress-fill {{
            background-color: {budget_color};
            width: {budget_usage_pct}%;
            height: 100%;
            transition: width 0.5s ease-in-out;
        }}
        </style>
        <div class="rbr-main-card">
            <img src="https://www.svgrepo.com/show/303227/redbull-logo.svg" class="rbr-logo-bg">
            <div class="rbr-label">Total Net Worth</div>
            <div class="rbr-value">R$ {net_worth:,.2f}</div>
            <div class="rbr-budget-container">
                <div class="rbr-header-row">
                    <div class="rbr-label" style="color: white; opacity: 0.6;">Budget</div>
                    <div class="rbr-label" style="color: white; opacity: 0.6;">Monthly Balance</div>
                </div>
                <div class="rbr-header-row" style="margin-top: 4px;">
                    <div style="font-size: 19px; font-weight: 700; font-family: 'Orbitron', monospace;">{left_val_html}</div>
                    <div style="font-size: 19px; font-weight: 700; font-family: 'Orbitron', monospace; color: {balance_text_color};">{right_val_html}</div>
                </div>
                <div class="rbr-progress-bar">
                    <div class="rbr-progress-fill"></div>
                </div>
                <div class="rbr-header-row" style="font-size: 11px; opacity: 0.8; font-family: 'Orbitron', monospace;">
                    <span>Spent: R$ {month_out:,.2f}</span>
                    <span>Limit: R$ {budget_limit:,.2f}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)