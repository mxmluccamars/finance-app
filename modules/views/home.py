# imports

from datetime import datetime
import streamlit as st
from modules.database import FinancialDB
from modules.utils import THEME
from modules.components import card_net_worth

def show():
    # 1. DB engine original
    db = FinancialDB()
    df_full = db.get_full_telemetry()
    # df_profile = db.get_profile()
    
    # df verification
    if df_full.empty:
        st.warning("No data available to display.")
        return
    
    # state management for month navigation
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.now().replace(day=1)
    
    view_date = st.session_state.view_date

    # net worth calculation (total balance)
    net_worth = df_full['real_amount'].sum()
    
    # monthly metrics calculation
    df_month = df_full[(df_full['date'].dt.month == view_date.month) &
                       (df_full['date'].dt.year == view_date.year)].copy()
    
    # monthly outflow and balance
    month_out = df_month[df_month['real_amount'] < 0]['amount'].sum()
    month_balance = df_month['real_amount'].sum()
    
    # budget limit
    # budget_limit = float(df_profile.iloc[0]['monthly_budget_limit']) if not df_profile.empty else 0
    budget_limit = 1800.00
    
    # text for month navigation component
    view_month_text = view_date.strftime('%B %Y')
    
    # TODO: Aqui vai entrar o componente de navegação de meses (nav_months)
    st.write(f"Navegação de Data: {view_month_text}") 
    
    # card 
    card_net_worth.render(
        net_worth=net_worth,
        month_out=month_out,
        budget_limit=budget_limit,
        month_balance=month_balance,
        view_month_text=view_month_text
    )

    # Botões de ações rápidas (Ainda no utils.py)
    st.write("### Quick Actions (Ainda por modularizar)")

    # TODO: Aqui vai entrar o componente unificado de histórico (transaction_log)
    st.write("### Recent Activity (Ainda por modularizar)")
