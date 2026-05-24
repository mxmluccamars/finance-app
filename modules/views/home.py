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

    # --- CSS DE NAVEGAÇÃO DE COCKPIT (BLINDAGEM TOTAL E PERSONALIZAÇÃO PIRELLI) ---
    st.markdown("""
        <style>
        /* Trava a linha horizontal de navegação na proporção exata e zero gap */
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            width: 100% !important;
            gap: 0px !important; /* Sem espaço entre as pílulas */
            align-items: center !important;
            padding: 0px !important;
        }

        /* Proporções rígidas para colar as setas nas extremidades (15% | 70% | 15%) */
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) { flex: 1 1 15% !important; max-width: 15% !important; width: 15% !important; }
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) { flex: 1 1 70% !important; max-width: 70% !important; width: 70% !important; }
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) { flex: 1 1 15% !important; max-width: 15% !important; width: 15% !important; }

        /* Estilização base que anula qualquer herança de outros blocos */
        .scuderia-nav-row div[data-testid="stColumn"] button,
        .scuderia-nav-row div[data-testid="stColumn"] button:disabled {
            height: 46px !important;
            min-height: 46px !important;
            background-color: #061D39 !important; /* Azul Oficial RBR */
            border-radius: 0px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: none !important;
            padding: 0px !important;
            color: transparent !important; /* Esconde o texto da seta nativa */
        }

        /* RESET TOTAL: Remove qualquer ícone fantástico injetado por pseudo-elementos anteriores */
        .scuderia-nav-row div[data-testid="stColumn"] button::before,
        .scuderia-nav-row div[data-testid="stColumn"] button::after {
            content: "" !important;
            display: none !important;
            background: none !important;
        }

        /* Injeção de Ícones Espessos do Google Fonts (Sem emojis) via Pseudo-elemento */
        .scuderia-nav-row div[data-testid="stColumn"] button::before {
            font-family: 'Material Symbols Outlined' !important;
            font-size: 20px !important;
            font-weight: bold !important;
            display: inline-block !important;
        }

        /* 1. CONFIGURAÇÃO DA SETA ESQUERDA (Voltar - Soft - Vermelho) */
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button {
            border: 2px solid #E0001A !important;
            border-top-left-radius: 10px !important;
            border-bottom-left-radius: 10px !important;
            border-right: none !important;
        }
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button::before {
            content: "arrow_back_ios" !important;
            color: #E0001A !important;
            margin-left: 6px; /* Centralização do ícone ios */
        }
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) button:hover {
            background-color: rgba(224, 0, 26, 0.08) !important;
        }

        /* 2. CONFIGURAÇÃO DO DISPLAY CENTRAL (Médio - Sem clique - Amarelo) */
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button:disabled {
            border: 2px solid #FFCC00 !important;
            background-color: #061D39 !important;
            color: #FFFFFF !important;
            font-size: 14px !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            opacity: 1 !important;
            cursor: default !important;
        }

        /* 3. CONFIGURAÇÃO DA SETA DIREITA (Avançar - Hard - Branco) */
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button {
            border: 2px solid #FFFFFF !important;
            border-top-right-radius: 10px !important;
            border-bottom-right-radius: 10px !important;
            border-left: none !important;
        }
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button::before {
            content: "arrow_forward_ios" !important;
            color: #E0001A !important;
        }
        .scuderia-nav-row div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) button:hover {
            background-color: rgba(255, 255, 255, 0.06) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Geração dos componentes envelopados na classe de blindagem
    st.markdown('<div class="scuderia-nav-row">', unsafe_allow_html=True)
    c_prev, c_date, c_next = st.columns(3)
    
    with c_prev:
        # Passamos um texto invisível para centralizar e esconder o caractere
        if st.button("L", key="cockpit_nav_prev", use_container_width=True):
            st.session_state.view_date = (st.session_state.view_date - timedelta(days=1)).replace(day=1)
            st.rerun()
            
    with c_date:
        current_month_text = st.session_state.view_date.strftime('%B %Y')
        st.button(current_month_text, key="cockpit_nav_display", disabled=True, use_container_width=True)
        
    with c_next:
        if st.button("R", key="cockpit_nav_next", use_container_width=True):
            st.session_state.view_date = (st.session_state.view_date + timedelta(days=32)).replace(day=1)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)


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