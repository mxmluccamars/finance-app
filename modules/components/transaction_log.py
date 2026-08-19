import streamlit as st
import pandas as pd
from modules.utils import THEME

def render(df_data, title="Recent Activity"):
    """
    Componente Estanque: Renderiza uma lista de transações (extrato).
    Pode ser reaproveitado em qualquer View do ecossistema.
    """
    st.write(f"### {title}")
    
    if df_data.empty:
        st.info("No telemetry recorded for this stint.")
        return

    # 1. Injeção de CSS com escopo rígido e prefixo exclusivo (.rbr-log-)
    st.markdown(f"""
        <style>
        .rbr-log-container {{
            width: 100% !important;
            margin-top: 10px !important;
        }}
        .rbr-log-row {{
            display: flex !important; 
            justify-content: space-between !important; 
            align-items: center !important; 
            padding: 14px 0 !important; 
            border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        }}
        .rbr-log-left {{ 
            display: flex !important; 
            align-items: center !important; 
            gap: 14px !important; 
        }}
        .rbr-log-icon {{ 
            font-size: 26px !important; 
            font-family: 'Material Symbols Outlined' !important; 
            font-weight: normal !important; 
        }}
        .rbr-log-title {{ 
            font-weight: 500 !important; 
            font-size: 15px !important; 
            color: #FFFFFF !important; 
        }}
        .rbr-log-meta {{ 
            font-size: 11px !important; 
            color: #888888 !important; 
            margin-top: 2px !important; 
        }}
        .rbr-log-value {{ 
            font-weight: bold !important; 
            font-size: 15px !important; 
            font-family: 'Courier New', monospace !important; 
        }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="rbr-log-container">', unsafe_allow_html=True)

    # 2. Varredura e Renderização das Linhas de Histórico
    for _, row in df_data.iterrows():
        # Captura e higieniza as propriedades vindo da nossa engine corrigida
        cat_color = row['color_cat'] if pd.notna(row.get('color_cat')) else "#FFFFFF"
        cat_icon = row['icon'] if pd.notna(row.get('icon')) else "payments"
        method_name = row['name'] if pd.notna(row.get('name')) else "Unknown"
        
        is_income = row['real_amount'] >= 0
        
        # Cores e Sinais padrão de telemetria
        impact_color = "#00D18E" if is_income else THEME['accent_2']
        prefix = "+" if is_income else "-"
        
        # CORREÇÃO CRÍTICA: Injetando as variáveis locais tratadas (cat_color e cat_icon)
        st.markdown(f"""
            <div class="rbr-log-row">
                <div class="rbr-log-left">
                    <span class="rbr-log-icon" style="color: {cat_color} !important;">{cat_icon}</span>
                    <div>
                        <div class="rbr-log-title">{row['desc']}</div>
                        <div class="rbr-log-meta">{row['date'].strftime('%d %b')} • {method_name}</div>
                    </div>
                </div>
                <div class="rbr-log-value" style="color: {impact_color} !important;">
                    {prefix} R$ {row['amount']:,.2f}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)