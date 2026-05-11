import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME
import textwrap

def show():
    # --- CONEXÃO E DADOS ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_trans = conn.read(worksheet="transactions")
    df_profile = conn.read(worksheet="user_profile")
    
    # 1. Inicializar o mês de visualização no Session State
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.now().replace(day=1)

    # --- CSS PARA BOTÕES LÍMPIDOS ---
    st.markdown("""
        <style>
        /* 1. Remove o espaço excessivo no topo sem quebrar o layout */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 0rem !important;
        }
        
        /* 2. Remove fundos e bordas apenas dos botões de navegação específicos */
        /* Usamos o atributo 'key' do Streamlit que se traduz em um help ou id interno */
        div[data-testid="stColumn"] button[kind="secondary"] {
            border: none !important;
            background-color: transparent !important;
            box-shadow: none !important;
            color: white !important;
            outline: none !important;
            padding: 0px !important;
            min-height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Ajuste para o ícone não sumir */
        div[data-testid="stColumn"] button p {
            font-size: 24px !important;
            margin: 0px !important;
        }

        .date-display {
            font-size: 20px;
            font-weight: 600;
            text-align: center;
            line-height: 40px;
            white-space: nowrap;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- CONTROLE DE NAVEGAÇÃO ---
    # Aumentei um pouco a proporção lateral para garantir que o botão tenha área de clique
    c_prev, c_date, c_next = st.columns([0.5, 4, 0.5])
    
    with c_prev:
        if st.button("", icon=":material/chevron_left:", key="btn_prev"):
            st.session_state.view_date = (st.session_state.view_date - timedelta(days=1)).replace(day=1)
            st.rerun()
            
    with c_date:
        current_view_label = st.session_state.view_date.strftime('%B - %Y')
        st.markdown(f"<div class='date-display'>{current_view_label}</div>", unsafe_allow_html=True)
        
    with c_next:
        if st.button("", icon=":material/chevron_right:", key="btn_next"):
            st.session_state.view_date = (st.session_state.view_date + timedelta(days=32)).replace(day=1)
            st.rerun()
            
    # --- LÓGICA DE FILTRO ---
    view_date = st.session_state.view_date
    df_trans['date'] = pd.to_datetime(df_trans['date'])
    
    # Filtrando transações do mês selecionado
    df_month = df_trans[(df_trans['date'].dt.month == view_date.month) & 
                        (df_trans['date'].dt.year == view_date.year)]
    
    # --- CÁLCULOS ---
    total_in = df_trans[df_trans['flow'] == 'In']['amount'].sum()
    total_out = df_trans[df_trans['flow'] == 'Out']['amount'].sum()
    net_worth = total_in - total_out

    # Valores do Mês Selecionado
    month_in = df_month[df_month['flow'] == 'In']['amount'].sum()
    month_out = df_month[df_month['flow'] == 'Out']['amount'].sum()
    month_balance = month_in - month_out
    
    budget_limit = float(df_profile.iloc[0]['monthly_budget_limit'])
    remaining_budget = budget_limit - month_out
    
    # --- LÓGICA DE MENSAGEM CRIATIVA (F1 STYLE) ---
    if df_month.empty:
        # Se não há transações, substituímos os valores por mensagens de rádio da equipe
        left_val_html = f"<span style='font-size: 16px; opacity: 0.8; font-style: italic;'>Clear track ahead...</span>"
        right_val_html = f"<span style='font-size: 16px; color: {THEME['accent_1']}; font-style: italic;'>Standing by...</span>"
        budget_usage_pct = 0
    else:
        # Se há transações, mostramos os números normalmente
        left_val_html = f"R$ {remaining_budget:,.2f} <span style='font-size: 12px; font-weight: normal; opacity: 0.7;'>left</span>"
        right_val_html = f"R$ {month_balance:,.2f}"
        budget_usage_pct = min((month_out / budget_limit) * 100, 100) if budget_limit > 0 else 0

    budget_color = THEME['accent_2'] if month_out > budget_limit else THEME['accent_1']

    logo_url = "https://www.svgrepo.com/show/303227/redbull-logo.svg"

    # --- UI: HEADER RBR ---
    html_content = textwrap.dedent(f"""
        <style>
        .main-card {{
            background-color: {THEME['primary']};
            padding: 25px;
            border-radius: 20px;
            color: {THEME['text_main']};
            margin-bottom: 20px;
            border-left: 8px solid {THEME['accent_1']};
            position: relative; /* Necessário para posicionar o logo */
            overflow: hidden;
        }}
        .logo-container {{
            position: absolute;
            top: 20px;
            right: 25px;
            width: 75px; /* Tamanho do logo */
            opacity: 0.9;
        }}
        .label {{ font-size: 13px; color: {THEME['accent_1']}; text-transform: uppercase; font-weight: bold; }}
        .value {{ font-size: 32px; font-weight: 800; margin-bottom: 15px; position: relative; z-index: 2; }}
        .budget-container {{ 
            background-color: rgba(255, 255, 255, 0.1); 
            border-radius: 10px; 
            padding: 15px; 
            margin-top: 10px;
            position: relative;
            z-index: 2;
        }}
        .progress-bar {{ background-color: rgba(255, 255, 255, 0.2); height: 8px; border-radius: 4px; margin: 10px 0; overflow: hidden; }}
        .progress-fill {{ background-color: {budget_color}; width: {budget_usage_pct}%; height: 100%; }}
        .header-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
        </style>
        <div class="main-card">
            <!-- LOGO DA RED BULL -->
            <img src="{logo_url}" class="logo-container">
            <div class="label">Total Net Worth</div>
            <div class="value">R$ {net_worth:,.2f}</div>
            <div class="budget-container">
                <div class="header-row">
                    <div class="label" style="font-size: 11px; color: {THEME['text_main']};">Budget for {view_date.strftime('%b')}</div>
                    <div class="label" style="font-size: 11px; color: {THEME['text_main']};">Monthly Balance</div>
                </div>                 
                <div class="header-row">
                    <div style="font-size: 20px; font-weight: 700;">
                        {left_val_html}
                    </div>
                    <div style="font-size: 20px; font-weight: 700; color: {'#2ECC71' if month_balance >= 0 else THEME['accent_2']};">
                        {right_val_html}
                    </div>
                </div>
                <div class="progress-bar"><div class="progress-fill"></div></div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; opacity: 0.8;">
                    <span>Spent: R$ {month_out:,.2f}</span>
                    <span>Limit: R$ {budget_limit:,.2f}</span>
                </div>
            </div>
        </div>
    """)
    st.markdown(html_content, unsafe_allow_html=True)

    # --- CÁLCULO DO NOME DO USUÁRIO ---
    # Pegamos o nome da aba user_profile
    user_name = df_profile.iloc[0]['name'] if not df_profile.empty else "Driver"

    # --- MENSAGEM PERSONALIZADA (RADIO CHECK) ---
    # 1. Importa a fonte de ícones (coloque isso no topo da função ou do script)
    st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)

    # 2. Renderiza a linha completa
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px;">
            <span class="material-symbols-outlined" style="color: {THEME['accent_1']}; font-size: 24px;">
                graphic_eq
            </span>
            <span style="color: {THEME['accent_1']}; font-weight: bold; letter-spacing: 1.5px; font-size: 13px; text-transform: uppercase; white-space: nowrap;">
                Radio Check: Lucca
            </span>
        </div>
        <h3 style="margin-top: 5px; margin-bottom: 20px; font-size: 24px; font-weight: 700;">
            What's the strategy for now?
        </h3>
    """, unsafe_allow_html=True)

    # --- QUICK ACTIONS AREA ---
    # Criando as 3 colunas para os botões principais
    col_pit, col_telemetry, col_setup = st.columns(3)

    with col_pit:
        # PIT STOP = Adicionar transação (onde o carro para para se reabastecer)
        if st.button("🛠️\nPIT STOP", use_container_width=True, key="btn_pit", help="Add new transaction"):
            st.session_state.selection = "Novo Gasto"
            st.rerun()

    with col_telemetry:
        # TELEMETRY = Histórico/Extrato (onde analisamos os dados da corrida)
        if st.button("📊\nDATA LOG", use_container_width=True, key="btn_telemetry", help="View history"):
            st.session_state.selection = "Statement"
            st.rerun()

    with col_setup:
        # SETUP = Configurações/Cartões (ajustes finos do carro)
        if st.button("🔧\nSETUP", use_container_width=True, key="btn_setup", help="Manage cards and profile"):
            st.session_state.selection = "Profile"
            st.rerun()

    st.markdown("---") # Divisor para a próxima seção

    # --- RECENT ACTIVITY ---
    st.write("### Recent Activity")
    recent = df_trans.sort_values(by='date', ascending=False).head(5)
    
    for _, row in recent.iterrows():
        icon = "⬆️" if row['flow'] == "In" else "⬇️"
        color = "#2ECC71" if row['flow'] == "In" else THEME['accent_2']
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div>
                    <span style="font-size: 18px;">{icon}</span>
                    <span style="font-weight: 500; margin-left: 10px;">{row['description']}</span>
                    <div style="font-size: 11px; color: gray; margin-left: 32px;">{row['date'].strftime('%d %b')}</div>
                </div>
                <div style="color: {color}; font-weight: bold;">
                    {" " if row['flow'] == "In" else "-"} R$ {row['amount']:,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True) 