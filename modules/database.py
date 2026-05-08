import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

class FinancialDB:
    def __init__(self):
        # Establish the connection using the secrets
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    def get_all_data(self):
        """Fetches all worksheets and returns them as a dictionary of DataFrames"""
        try:
            data = {
                "transactions": self.conn.read(worksheet="transactions"),
                "categories": self.conn.read(worksheet="categories"),
                "methods": self.conn.read(worksheet="payment_methods"),
                "types": self.conn.read(worksheet="transaction_types"),
                "profile": self.conn.read(worksheet="user_profile")
            }
            return data
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None

    def get_master_dataframe(self):
        """Joins all tables into a single Human-Readable DataFrame"""
        data = self.get_all_data()
        if data is None: return None

        # Start with transactions
        df = data["transactions"]

        # Join with categories
        df = df.merge(data["categories"], on="category_id", how="left")

        # Join with methods
        df = df.merge(data["methods"], on="method_id", how="left")

        # Join methods with types (to get Impact: Immediate/Delayed)
        df = df.merge(data["types"], on="type_id", how="left")

        return df

    def save_transaction(self, new_row_df):
        """Appends a new row to the transactions worksheet"""
        existing_data = self.conn.read(worksheet="transactions")
        updated_df = pd.concat([existing_data, new_row_df], ignore_index=True)
        self.conn.update(worksheet="transactions", data=updated_df)
        st.cache_data.clear() # Clear cache so the new data shows up