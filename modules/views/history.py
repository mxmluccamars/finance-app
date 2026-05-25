import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.utils import THEME
from modules.database import FinancialDB

def show():
    # --- ENGINE DE DADOS (Centralizado) ---
    db = FinancialDB()
    df_full = db.get_full_telemetry() # Já vem com todos os joins e real_amount calculado
    df_profile = db.get_profile()     # Puxa as configurações de teto do cockpit

    # --- UI & CSS CUSTOM ---
    st.markdown(f"""
        <style>
        .block-container {{ padding-top: 1rem !important; }}
        
        /* Estilo Paddock Button */
        div[data-testid="stButton"] > button {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-left: 5px solid {THEME['accent_1']} !important;
            color: white !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            width: 100%;
            transition: 0.3s;
        }}
        div[data-testid="stButton"] > button:hover {{
            border-left: 5px solid {THEME['accent_2']} !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }}
        
        .date-display {{ font-size: 22px; font-weight: 800; text-align: center; color: white; padding: 10px 0; }}
        </style>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    """, unsafe_allow_html=True)

    # --- TOPO: BOTÃO PADDOCK ---
    if st.button("⬅️ RETURN TO PADDOCK (HOME)"):
        st.session_state.selection = "Home"
        st.rerun()

    st.divider()

    # --- NAVEGAÇÃO DE MÊS ---
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.now().replace(day=1)

    c_prev, c_date, c_next = st.columns([0.5, 4, 0.5])
    with c_prev:
        if st.button("◀", key="log_prev"):
            st.session_state.view_date = (st.session_state.view_date - timedelta(days=1)).replace(day=1)
            st.rerun()
    with c_date:
        st.markdown(f"<div class='date-display'>{st.session_state.view_date.strftime('%B %Y').upper()}</div>", unsafe_allow_html=True)
    with c_next:
        if st.button("▶", key="log_next"):
            st.session_state.view_date = (st.session_state.view_date + timedelta(days=32)).replace(day=1)
            st.rerun()

    # --- FILTRAGEM DE DADOS BASE —--
    if df_full.empty:
        st.info("No telemetry recorded yet.")
        return

    # Filtro de Data baseado no seletor
    view_date = st.session_state.view_date
    df_month = df_full[(df_full['date'].dt.month == view_date.month) & 
                       (df_full['date'].dt.year == view_date.year)].copy()
    # print(df_month.columns) # Debug: Verificar colunas disponíveis após o merge
    
    budget_limit = float(df_profile.iloc[0]['monthly_budget_limit']) if not df_profile.empty else 0
# --- GRAPH MOTOR: PREDICTIVE INFLOW vs OUTFLOW PACE (PLOTLY) ---
    if not df_month.empty:
        # 1. Separar dados em Gastos (Saídas) e Incomes (Entradas)
        df_expenses = df_month[df_month['real_amount'] < 0].copy()
        df_incomes = df_month[df_month['real_amount'] > 0].copy()
        
        # Mapeia dias para o grid do Pandas
        last_day = (view_date.replace(month=view_date.month % 12 + 1, day=1) - timedelta(days=1)).day
        df_daily = pd.DataFrame({'day': range(1, last_day + 1)})

        # Processa a base de Gastos
        if not df_expenses.empty:
            df_expenses['day'] = df_expenses['date'].dt.day
            df_daily_exp = df_expenses.groupby('day')['amount'].sum().reset_index().rename(columns={'amount': 'exp_amount'})
            df_daily = pd.merge(df_daily, df_daily_exp, on='day', how='left')
        else:
            df_daily['exp_amount'] = 0
            
        # Processa a base de Ganhos (Incomes)
        if not df_incomes.empty:
            df_incomes['day'] = df_incomes['date'].dt.day
            df_daily_inc = df_incomes.groupby('day')['amount'].sum().reset_index().rename(columns={'amount': 'inc_amount'})
            df_daily = pd.merge(df_daily, df_daily_inc, on='day', how='left')
        else:
            df_daily['inc_amount'] = 0
            
        df_daily = df_daily.fillna(0)

        # Calculo das Somas Cumulativas Reais
        df_daily['exp_accumulated'] = df_daily['exp_amount'].cumsum()
        df_daily['inc_accumulated'] = df_daily['inc_amount'].cumsum()

        # Captura tempo real para a lógica de Forecasting
        now = datetime.now()
        is_current_month = (view_date.month == now.month and view_date.year == now.year)

        # --- CONSTRUÇÃO VISUAL (PLOTLY MOTOR COM DEGRADÊ E MOLDURA) ---
        fig = go.Figure()

        if is_current_month:
            today = min(now.day, last_day)
            
            # Pega os últimos valores reais acumulados de gastos e ganhos até hoje
            exp_today = df_daily.loc[df_daily['day'] == today, 'exp_accumulated'].values[0]
            inc_today = df_daily.loc[df_daily['day'] == today, 'inc_accumulated'].values[0]
            
            salary_target = float(df_profile.iloc[0]['monthly_budget_limit']) if not df_profile.empty else inc_today
            days_remaining = last_day - today
            
            avg_daily_spend = exp_today / today if today > 0 else 0
            allowed_daily_inc = (salary_target - inc_today) / days_remaining if days_remaining > 0 and salary_target > inc_today else 0

            for d in range(today + 1, last_day + 1):
                days_passed_since_today = d - today
                df_daily.loc[df_daily['day'] == d, 'exp_accumulated'] = exp_today + (avg_daily_spend * days_passed_since_today)
                df_daily.loc[df_daily['day'] == d, 'inc_accumulated'] = inc_today + (allowed_daily_inc * days_passed_since_today)

            df_actual = df_daily[df_daily['day'] <= today]
            df_projected = df_daily[df_daily['day'] >= today]

            # --- LINHAS DE GASTOS (VERMELHO SOFT COM DEGRADÊ) ---
            # --- LINHAS DE GASTOS (VERMELHO SOFT COM DEGRADÊ CORRIGIDO) ---
            fig.add_trace(go.Scatter(
                x=df_actual['day'], y=df_actual['exp_accumulated'],
                mode='lines', name='Gastos Reais',
                line=dict(color=THEME['accent_2'], width=3),
                fill='tozeroy',
                # Nova sintaxe correta usando colorscale para o degradê sumir na base
                fillgradient=dict(
                    type='vertical',
                    colorscale=[
                        [0.0, 'rgba(224, 0, 26, 0.0)'],  # 0% (base) totalmente transparente
                        [1.0, 'rgba(224, 0, 26, 0.25)']  # 100% (linha) vermelho soft visível
                    ]
                ),
                hovertemplate='<b>DIA %{x}</b><br>Gasto Acumulado: R$ %{y:,.2f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df_projected['day'], y=df_projected['exp_accumulated'],
                mode='lines', name='Projeção Gastos',
                line=dict(color=THEME['accent_2'], width=3, dash='dot'),
                hovertemplate='<b>DIA %{x} (Previsão)</b><br>Gasto: R$ %{y:,.2f}<extra></extra>'
            ))

            # --- LINHAS DE INCOME (VERDE REGEN COM DEGRADÊ CORRIGIDO) ---
            fig.add_trace(go.Scatter(
                x=df_actual['day'], y=df_actual['inc_accumulated'],
                mode='lines', name='Income Real',
                line=dict(color='#2ECC71', width=3),
                fill='tozeroy',
                # Nova sintaxe correta usando colorscale para o degradê
                fillgradient=dict(
                    type='vertical',
                    colorscale=[
                        [0.0, 'rgba(46, 204, 113, 0.0)'],  # 0% (base) transparente
                        [1.0, 'rgba(46, 204, 113, 0.25)']  # 100% (linha) verde visível
                    ]
                ),
                hovertemplate='<b>DIA %{x}</b><br>Income Acumulado: R$ %{y:,.2f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df_projected['day'], y=df_projected['inc_accumulated'],
                mode='lines', name='Projeção Income',
                line=dict(color='#2ECC71', width=3, dash='dot'),
                hovertemplate='<b>DIA %{x} (Previsão)</b><br>Income: R$ %{y:,.2f}<extra></extra>'
            ))

        else:
            # Mês Encerrado: Desenha as duas curvas cheias normais com degradê corrigido
            fig.add_trace(go.Scatter(
                x=df_daily['day'], y=df_daily['exp_accumulated'],
                mode='lines', name='Gastos',
                line=dict(color=THEME['accent_2'], width=3),
                fill='tozeroy',
                fillgradient=dict(
                    type='vertical',
                    colorscale=[
                        [0.0, 'rgba(224, 0, 26, 0.0)'],
                        [1.0, 'rgba(224, 0, 26, 0.2)']
                    ]
                ),
                hovertemplate='<b>DIA %{x}</b><br>Total Gasto: R$ %{y:,.2f}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=df_daily['day'], y=df_daily['inc_accumulated'],
                mode='lines', name='Incomes',
                line=dict(color='#2ECC71', width=3),
                fill='tozeroy',
                fillgradient=dict(
                    type='vertical',
                    colorscale=[
                        [0.0, 'rgba(46, 204, 113, 0.0)'],
                        [1.0, 'rgba(46, 204, 113, 0.2)']
                    ]
                ),
                hovertemplate='<b>DIA %{x}</b><br>Total Income: R$ %{y:,.2f}<extra></extra>'
            ))

        # Customização do Layout F1 Grid
        fig.update_layout(
            paper_bgcolor='rgba(6, 29, 57, 0.25)', # Azul escuro RBR no fundo do card
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=15, r=15, t=15, b=15),
            height=260,
            showlegend=False,
            
            # --- SOLUÇÃO DA BORDA: Usando os espelhos de eixos (Mirrored Axis Lines) ---
            # Ativando 'showline' e 'mirror' cria a moldura perfeita travada pelo Plotly
            xaxis=dict(
                title=dict(text='DAY / LAP', font=dict(color='gray', size=10)),
                tickfont=dict(color='gray', size=10),
                gridcolor='rgba(255, 255, 255, 0.03)',
                showgrid=True,
                dtick=5,
                showline=True,
                linecolor='rgba(255, 255, 255, 0.08)', # Cor da moldura horizontal
                linewidth=1,
                mirror=True # Replica a linha para o topo do gráfico
            ),
            yaxis=dict(
                tickfont=dict(color='gray', size=10),
                gridcolor='rgba(255, 255, 255, 0.03)',
                showgrid=True,
                side='right',
                showline=True,
                linecolor='rgba(255, 255, 255, 0.08)', # Cor da moldura vertical
                linewidth=1,
                mirror=True # Replica a linha para a esquerda do gráfico
            )
        )

        st.write("### 📈 TELEMETRY PACE: INCOMES vs EXPENSES")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # =========================================================
        # GRAPH 2: ISOLATED CUSTOM PROGRESS BARS COMPONENT
        # =========================================================
        if not df_expenses.empty:
            st.write("### 📊 SECTOR DRAG: GASTOS POR CATEGORIA")
            
            cat_column_name = 'name_cat' if 'name_cat' in df_expenses.columns else 'categoria'
            
            if cat_column_name in df_expenses.columns:
                # Agrupa os gastos reais agrupados por categoria
                df_cat = df_expenses.groupby(cat_column_name).agg({
                    'amount': 'sum',
                    'color_cat': 'first',
                    'icon': 'first'
                }).reset_index()
                
                df_cat = df_cat.sort_values(by='amount', ascending=False)
                total_expenses_value = df_cat['amount'].sum()

                st.markdown("""
                    <style>
                    .telemetry-drag-container { margin-bottom: 25px !important; width: 100% !important; }
                    .telemetry-drag-row { padding: 12px 0 !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; margin-bottom: 6px !important; }
                    .telemetry-drag-header { display: flex !important; justify-content: space-between !important; align-items: center !important; margin-bottom: 8px !important; }
                    .telemetry-drag-left { display: flex !important; align-items: center !important; gap: 12px !important; }
                    .telemetry-drag-icon { font-size: 26px !important; font-family: 'Material Symbols Outlined' !important; font-weight: normal !important; }
                    .telemetry-drag-label { font-weight: 700 !important; font-size: 14px !important; color: white !important; letter-spacing: 0.5px !important; }
                    .telemetry-drag-value { color: white !important; font-weight: bold !important; font-size: 15px !important; font-family: 'Courier New', monospace !important; }
                    .telemetry-drag-bar-track { background-color: rgba(255, 255, 255, 0.04) !important; height: 5px !important; width: 100% !important; border-radius: 3px !important; overflow: hidden !important; position: relative !important; }
                    .telemetry-drag-bar-fill { height: 100% !important; border-radius: 3px !important; opacity: 0.85 !important; }
                    </style>
                """, unsafe_allow_html=True)

                # Dicionário de presets locais idêntico ao da Home para sincronismo total
                fallback_theme = {
                    'home': '#1E90FF', 'tech': '#FF8C00', 'health': '#2ECC71', 
                    'food': '#E74C3C', 'motorbike': '#F1C40F', 'apparel': '#9B59B6', 
                    'subscriptions': '#1ABC9C'
                }

                st.markdown('<div class="telemetry-drag-container">', unsafe_allow_html=True)

                for _, row in df_cat.iterrows():
                    pure_name = str(row[cat_column_name]).strip()
                    cat_name_upper = pure_name.upper()
                    cat_key_lower = pure_name.lower()
                    cat_amount = row['amount']
                    
                    # Resgata a cor da planilha ou aplica o fallback correspondente
                    if pd.notna(row.get('color_cat')) and str(row['color_cat']).startswith('#'):
                        cat_color = str(row['color_cat'])
                    else:
                        cat_color = fallback_theme.get(cat_key_lower, '#FFFFFF')
                        
                    cat_icon = row['icon'] if pd.notna(row['icon']) else "payments"
                    share_pct = (cat_amount / total_expenses_value) * 100 if total_expenses_value > 0 else 0
                    
                    st.markdown(f"""
                        <div class="telemetry-drag-row">
                            <div class="telemetry-drag-header">
                                <div class="telemetry-drag-left">
                                    <span class="telemetry-drag-icon" style="color: {cat_color} !important;">{cat_icon}</span>
                                    <span class="telemetry-drag-label">{cat_name_upper}</span>
                                </div>
                                <div class="telemetry-drag-value">
                                    R$ {cat_amount:,.2f} <span style="font-size: 11px; color: gray; font-weight: normal; font-family: sans-serif; margin-left: 4px;">({share_pct:.1f}%)</span>
                                </div>
                            </div>
                            <div class="telemetry-drag-bar-track">
                                <div class="telemetry-drag-bar-fill" style="background-color: {cat_color} !important; width: {share_pct}%;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Coluna de categoria não identificada no DataFrame. Verifique as chaves do banco! 🛠️")



    # --- LOG HISTÓRICO ORIGINAL ---
    st.markdown("### 🏁 Transaction Log")
    df_month = df_month.sort_values(by='date', ascending=False)

    if df_month.empty:
        st.info("No data for this stint.")
    else:
        for _, row in df_month.iterrows():
            is_positive = row['real_amount'] >= 0
            color_val = "#2ECC71" if is_positive else THEME['accent_2']
            prefix = "+" if is_positive else "-"
            
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span class="material-symbols-outlined" style="color: {row['color_cat']}; font-size: 28px;">
                            {row['icon']}
                        </span>
                        <div>
                            <div style="font-weight: 500; font-size: 15px; color: white;">{row['desc']}</div>
                            <div style="font-size: 11px; color: #888;">
                                {row['date'].strftime('%d %b')} • {row['name']}
                            </div>
                        </div>
                    </div>
                    <div style="color: {color_val}; font-weight: bold; font-size: 16px; font-family: 'Courier New', monospace;">
                        {prefix} R$ {row['amount']:,.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)