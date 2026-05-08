
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="S&P 500 Sector Heatmap", layout="wide")

API_KEY = st.secrets["FMP_API_KEY"]

sector_etfs = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Materials": "XLB",
    "Real Estate": "XLRE",
}

indexes = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Russell 2000": "^RUT",
}

def get_quote(symbol):
url = f"https://financialmodelingprep.com/stable/quote?symbol={symbol}&apikey={API_KEY}"
    r = requests.get(url, timeout=20)
    data = r.json()
    return data[0] if data else {}

def get_etf_holdings(symbol):
    url = f"https://financialmodelingprep.com/api/v3/etf-holder/{symbol}?apikey={API_KEY}"
    r = requests.get(url, timeout=20)
    return r.json()[:5]

st.title("📊 S&P 500 Sector Heatmap Dashboard")

st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("🔄 Actualizar datos ahora"):
    st.rerun()

st.subheader("Índices principales")

cols = st.columns(3)

for i, (name, ticker) in enumerate(indexes.items()):
    try:
        q = get_quote(ticker)
        change = q.get("changesPercentage", 0)
        cols[i].metric(
            label=name,
            value=f"{q.get('price', 'N/A')}",
            delta=f"{round(change,2)}%"
        )
    except:
        cols[i].metric(label=name, value="Error")

st.divider()

st.subheader("Sectores GICS")

cards = []

for sector, etf in sector_etfs.items():
    try:
        q = get_quote(etf)
        cards.append({
            "Sector": sector,
            "ETF": etf,
            "Precio": q.get("price"),
            "Cambio %": round(q.get("changesPercentage", 0), 2),
            "Market Cap": q.get("marketCap"),
        })
    except:
        pass

df = pd.DataFrame(cards)

sort_option = st.selectbox(
    "Ordenar por",
    ["Cambio %", "Precio", "Market Cap"]
)

df = df.sort_values(by=sort_option, ascending=False)

st.dataframe(df, use_container_width=True)

st.divider()

for _, row in df.iterrows():
    with st.expander(f"{row['Sector']} ({row['ETF']})"):
        st.write(f"ETF: {row['ETF']}")
        st.write(f"Performance: {row['Cambio %']}%")

        try:
            holdings = get_etf_holdings(row['ETF'])
            if holdings:
                hdf = pd.DataFrame(holdings)[["asset", "weightPercentage"]]
                hdf.columns = ["Holding", "Peso %"]
                st.write("Top Holdings")
                st.dataframe(hdf, use_container_width=True)
        except:
            st.warning("No se pudieron cargar holdings.")
