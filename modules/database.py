import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME

class FinancialDB:
    def __init__(self):
        # Estabelece a conexão com o Google Sheets utilizando os segredos configurados
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    @st.cache_data(ttl=3600)  # Cache de 1 hora para dados que mudam pouco
    def get_full_telemetry(_self):
        """
        Lê todas as worksheets e consolida num único DataFrame formatado.
        Centraliza a lógica de 'merges' para evitar repetição de código.
        """
        try:
            # 1. Leitura bruta das tabelas
            df_trans = _self.conn.read(worksheet="transactions")
            df_methods = _self.conn.read(worksheet="payment_methods")
            df_cats = _self.conn.read(worksheet="categories")
            df_types = _self.conn.read(worksheet="payment_types")
            
            # 2. Engine de Merges (Unificação da Telemetria)
            # Unir transações com métodos de pagamento
            df = df_trans.merge(df_methods, left_on='method_id', right_on='id', suffixes=('', '_meth'))
            
            # Unir com tipos de pagamento para obter o 'impact' (In/Out)
            # Verificamos o nome da coluna de ID na aba de tipos
            type_key = 'type_id' if 'type_id' in df_types.columns else 'id'
            df = df.merge(df_types, left_on='type_id', right_on=type_key, suffixes=('', '_type'))
            
            # Unir com categorias para obter ícones e cores
            df = df.merge(df_cats, left_on='cat_id', right_on='id', suffixes=('', '_cat'))
            
            # 3. Tratamento de Dados
            df['date'] = pd.to_datetime(df['date'])
            
            # Criar coluna de valor real (Sinalização Positiva ou Negativa)
            # Baseado no seu padrão observado: 'In' ou 'Inflow' são positivos
            df['real_amount'] = df.apply(
                lambda x: x['amount'] if str(x.get('impact', 'Out')).strip().lower() in ['in', 'inflow'] 
                else -x['amount'], axis=1
            )
            
            return df
        except Exception as e:
            st.error(f"Erro na Engine de Dados: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def get_profile(_self):
        """Retorna os dados do perfil do utilizador (ex: limites de orçamento)"""
        try:
            return _self.conn.read(worksheet="user_profile")
        except:
            return pd.DataFrame()

    def save_transaction(self, new_row_df):
        """
        Adiciona uma nova transação diretamente na folha e limpa o cache.
        Garante que a escrita é direta e a leitura subsequente seja atualizada.
        """
        try:
            # Lemos os dados atuais (sem cache para evitar conflitos de ID)
            existing_data = self.conn.read(worksheet="transactions", ttl=0)
            updated_df = pd.concat([existing_data, new_row_df], ignore_index=True)
            
            # Atualiza a folha no Google Sheets
            self.conn.update(worksheet="transactions", data=updated_df)
            
            # LIMPEZA CRÍTICA: Força o app a esquecer os dados antigos cacheados
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Falha na gravação: {e}")
            return False
        
    @st.cache_data(ttl=3600)
    def get_categories(_self):
        """Retorna a lista bruta de categorias para seletores."""
        return _self.conn.read(worksheet="categories")

    @st.cache_data(ttl=3600)
    def get_methods(_self):
        """Retorna a lista bruta de métodos para seletores."""
        return _self.conn.read(worksheet="payment_methods")