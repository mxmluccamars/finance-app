# imports
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from modules.utils import THEME

class FinancialDB: # centralization of the data base interactions
    def __init__(self):
        # establish connection to Google Sheets using streamlit_gsheets
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    @st.cache_data(ttl=600) # cache the data for 10 minutes to improve performance
    def get_full_telemetry(_self):
        # protect from errors
        try:
            # spreadsheets reading
            df_trans = _self.conn.read(worksheet="transactions")
            df_methods = _self.conn.read(worksheet="payment_methods")
            df_cats = _self.conn.read(worksheet="categories")
            df_types = _self.conn.read(worksheet="payment_types")

            # data processing
            df = df_trans.merge(df_methods, # right table
                                left_on="method_id", # looking at the method_id column in transactions
                                right_on="id", # find the corresponding id in payments_methods
                                suffixes=("", "_meth")) # add suffixes to differentiate columns with the same name
            # same for types and categories
            df = df.merge(df_types,
                            left_on="type_id",
                            right_on="id",
                            suffixes=("", "_type"))
            
            df = df.merge(df_cats,
                          left_on="cat_id",
                          right_on="id",
                          suffixes=("", "_cat"))
            
            # date formatting
            df["date"] = pd.to_datetime(df["date"]) # convert date column (str) to datetime format

            # amount formatting
            df["real_amount"] = df.apply(
                lambda x: x["amount"] if str(x.get("impact", "out")).strip().lower() == "in" else -x["amount"], axis=1
            ) # convert the amount to negative if it's an "out" transaction, and keep it positive if it's an "in" transaction

            print(df.head()) # print the first 5 rows of the dataframe to check if everything is correct
            return df
            
        except Exception as e:
            st.error(f"Error loading data: {e}")
            print(f"Error loading data: {e}")
            return pd.DataFrame()


