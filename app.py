import streamlit as st
import pandas as pd
import yfinance as yf
import json
import plotly.express as px
from datetime import datetime

st.title("Investimentos em Criptomoedas")

# Dados salvos
try:
    with open("investments.json", "r") as file:
        investments = json.load(file)
except FileNotFoundError:
    investments = []
# Dados
with open("data.json", "r") as file:
    crypto_data = json.load(file)
    crypto_dict = dict(zip(crypto_data["crypto_names"], crypto_data["crypto_symbols"]))

#   Adicionar investimento
st.sidebar.header("Adicionar Investimento")
with st.sidebar.form("add_investment"):
    crypto_selected = st.selectbox("Criptomoeda", options=crypto_dict.keys())
    purchase_date = st.date_input("Data da compra")
    purchase_price = st.number_input("Preço de compra (USD)", min_value=0.0, step=0.01)
    amount = st.number_input("Quantidade comprada", min_value=0.0, step=0.01)
    
    if st.form_submit_button("Salvar Investimento"):
        new_investment = {
            "id": len(investments) + 1,
            "crypto": crypto_selected,
            "symbol": crypto_dict[crypto_selected],
            "purchase_date": str(purchase_date),
            "purchase_price": purchase_price,
            "amount": amount
        }
        investments.append(new_investment)
        with open("investments.json", "w") as file:
            json.dump(investments, file)
        st.success("Investimento registrado!")

#   Visualizar investimentos
st.header("Meus Investimentos")
if not investments:
    st.warning("Nenhum investimento registrado.")
else:
    df_investments = pd.DataFrame(investments)
    st.dataframe(df_investments)

#   Editar
if investments:
    st.header("Gerenciar Investimentos")
    invest_id = st.selectbox(
        "Selecione o investimento para editar/excluir",
        options=[inv["id"] for inv in investments]
    )
    
    selected_invest = next(inv for inv in investments if inv["id"] == invest_id)
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("edit_investment"):
            st.write(f"Editando: {selected_invest['crypto']}")
            new_amount = st.number_input("Nova quantidade", value=selected_invest["amount"])
            new_price = st.number_input("Novo preço", value=selected_invest["purchase_price"])
            
            if st.form_submit_button("Atualizar"):
                selected_invest["amount"] = new_amount
                selected_invest["purchase_price"] = new_price
                with open("investments.json", "w") as file:
                    json.dump(investments, file)
                st.success("Atualizado com sucesso!")
    
    with col2:
        if st.button("Excluir Investimento"):
            investments = [inv for inv in investments if inv["id"] != invest_id]
            with open("investments.json", "w") as file:
                json.dump(investments, file)
            st.success("Investimento removido!")

# Gráfico
if investments:
    st.header("Desempenho dos Investimentos")
    selected_crypto = st.selectbox(
        "Selecione uma criptomoeda para análise",
        options=list(set([inv["crypto"] for inv in investments]))
    )
    
    #   Dados históricos
    symbol = crypto_dict[selected_crypto] + "-USD"
    df_history = yf.Ticker(symbol).history(period="2y")["Close"].reset_index()
    
    #   Investimentos na criptomoeda selecionada
    crypto_investments = [inv for inv in investments if inv["crypto"] == selected_crypto]
    
    #   Gráfico
    fig = px.line(df_history, x="Date", y="Close", title=f"Histórico de {selected_crypto}")
    
    #   Marcador
    for inv in crypto_investments:
        purchase_date = datetime.strptime(inv["purchase_date"], "%Y-%m-%d").date()
        fig.add_vline(x=purchase_date, line_dash="dash", line_color="red")
    
    st.plotly_chart(fig)