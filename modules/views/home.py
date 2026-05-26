import streamlit as st
from modules.database import FinancialDB
from modules.utils import THEME

def show():
    # 1. DB engine original
    db = FinancialDB()
    df_full = db.get_full_telemetry()
    # df_profile = db.get_profile()
    
    # =========================================================
    # 🏁 PIT LANE DEBUGGER: INSPEÇÃO DO DATAFRAME (TEMPORÁRIO)
    # =========================================================
    st.markdown("### 🛠️ DEBUGGER: TELEMETRIA BRUTA (BRANCH DEV)")
    
    # Exibe a lista exata de colunas para checar se o Pandas aplicou os sufixos certos
    st.write("**Colunas disponíveis no motor:**", list(df_full.columns))
    
    # Exibe um resumo das colunas críticas para vermos se os valores estão batendo
    if not df_full.empty:
        cols_para_checar = ['date', 'desc', 'amount', 'real_amount', 'name_cat', 'color_cat']
        # Filtra apenas as colunas que realmente existem para não dar erro se alguma falhar
        cols_existentes = [c for c in cols_para_checar if c in df_full.columns]
        
        st.write("**Amostra de dados higienizados:**")
        st.dataframe(df_full.head(5), use_container_width=True)
    else:
        st.error("O DataFrame veio completamente vazio! 🚨")
        
    st.divider() # Linha visual para separar o debug do resto do seu app
    # =========================================================