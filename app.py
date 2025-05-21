import streamlit as st
import pandas as pd
import yfinance as yf
import json
import plotly.express as px

# Carrega dados
with open("data.json", "r") as _json:
    data_string = _json.read()

obj = json.loads(data_string)
crypto_dict = dict(zip(obj["crypto_names"], obj["crypto_symbols"]))

# Seleção cripto
crypto_selected = st.selectbox(
    label='Selecione sua moeda',
    options=crypto_dict.keys()
)

_symbol = crypto_dict[crypto_selected] + '-USD'
ticker = yf.Ticker(_symbol)
df = ticker.history(interval='1d', period='2y')

#lucro/prejuízo
st.subheader("Calculadora de Lucro/Prejuízo")

#ano da compra
year_list = list(range(df.index.min().year, df.index.max().year + 1))
purchase_year = st.selectbox(
    "Ano de compra",
    options=year_list,
    index=len(year_list)-1  # Seleciona o último ano por padrão
)

# Preço de compra
purchase_price = st.number_input(
    "Preço de compra (USD)",
    min_value=0.0,
    value=float(df['Close'].iloc[-1]),  # Preço atual como valor padrão
    step=0.01
)

# Calcula o resultado
current_price = df['Close'].iloc[-1]
profit_loss = (current_price - purchase_price)
percent_change = ((current_price - purchase_price) / purchase_price) * 100

# Exibe os resultados
col1, col2 = st.columns(2)
with col1:
    st.metric("Preço atual", f"${current_price:,.2f}")
with col2:
    st.metric("Variação", f"{percent_change:,.2f}%")

if profit_loss >= 0:
    st.success(f"Lucro: ${profit_loss:,.2f} ({percent_change:,.2f}%)")
else:
    st.error(f"Prejuízo: ${abs(profit_loss):,.2f} ({percent_change:,.2f}%)")

# Gráfico principal
st.subheader(f"Histórico de {crypto_selected}")
columns_selected = st.multiselect(
    label='Selecione as colunas para o gráfico:',
    options=df.columns,
    default=['Close']
)

fig = px.line(
    df,
    x=df.index,
    y=columns_selected,
    title=f'Valores de {crypto_selected}'
)
st.plotly_chart(fig)