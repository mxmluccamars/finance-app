import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Finance App", page_icon="💰")

st.title("💰 Finance Tracker Connection Test")

# Criando a conexão
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Tenta ler a aba de categorias
    df_categories = conn.read(worksheet="categories")
    
    st.success("Successfully connected to Google Sheets!")
    
    st.subheader("Your Categories:")
    st.dataframe(df_categories)
    
except Exception as e:
    st.error("Failed to connect.")
    st.code(e)

if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()