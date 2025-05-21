import streamlit as st
import pandas as pd
import yfinance as yf
import json
from datetime import datetime

st.title("Sistema de Gerenciamento de Criptomoedas")

try:
    with open("investments.json", "r") as file:
        investments = json.load(file)
except FileNotFoundError:
    investments = []

#   Criptomoedas disponíveis
with open("data.json", "r") as file:
    crypto_data = json.load(file)
    crypto_dict = dict(zip(crypto_data["crypto_names"], crypto_data["crypto_symbols"]))


st.sidebar.header("Adicionar Investimento")
with st.sidebar.form("add_investment"):
    crypto = st.selectbox("Criptomoeda", options=crypto_dict.keys())
    purchase_date = st.date_input("Data da compra")
    purchase_price = st.number_input("Preço de compra (USD)", min_value=0.0, step=0.01)
    amount = st.number_input("Quantidade comprada", min_value=0.0, step=0.01)

    if st.form_submit_button("Salvar"):
        new_investment = {
            "id": len(investments) + 1,
            "crypto": crypto,
            "symbol": crypto_dict[crypto],
            "purchase_date": str(purchase_date),
            "purchase_price": purchase_price,
            "amount": amount
        }
        investments.append(new_investment)
        with open("investments.json", "w") as file:
            json.dump(investments, file, indent=4)
        st.success("Investimento registrado!")

st.header("Meus Investimentos")
if not investments:
    st.warning("Nenhum investimento registrado.")
else:
    # Calcula investimento
    for inv in investments:
        symbol = inv["symbol"] + "-USD"
        current_price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
        total_invested = inv["purchase_price"] * inv["amount"]
        current_value = current_price * inv["amount"]
        profit_loss = current_value - total_invested
        percent_change = (profit_loss / total_invested) * 100

        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{inv['crypto']} - Compra em {inv['purchase_date']}")
            st.write(f"**Quantidade:** {inv['amount']} | **Preço de compra:** ${inv['purchase_price']:.2f}")
            st.write(f"**Valor investido:** ${total_invested:.2f} | **Valor atual:** ${current_value:.2f}")

        with col2:
            if profit_loss >= 0:
                st.success(f"Lucro: ${profit_loss:.2f} ({percent_change:.2f}%)")
            else:
                st.error(f"Prejuízo: ${abs(profit_loss):.2f} ({percent_change:.2f}%)")

        st.markdown("---")

#   Update/Delete
if investments:
    st.header("Editar/Excluir Investimentos")
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
                    json.dump(investments, file, indent=4)
                st.success("Dados atualizados!")

    with col2:
        if st.button("Excluir Investimento"):
            investments = [inv for inv in investments if inv["id"] != invest_id]
            with open("investments.json", "w") as file:
                json.dump(investments, file, indent=4)
            st.success("Investimento removido!")

# GRÁFICO
if investments:
    st.header("Historico de Precos")
    selected_crypto = st.selectbox(
        "Selecione uma criptomoeda para visualizar o historico",
        options=list(set([inv["crypto"] for inv in investments]))
    )

    symbol = crypto_dict[selected_crypto] + "-USD"
    df_history = yf.Ticker(symbol).history(period="1y")["Close"]

    st.line_chart(df_history)