import streamlit as st
from dotenv import load_dotenv
import snowflake.connector
import os
import pandas as pd
import plotly.express as px

load_dotenv()

SNOWFLAKE_ACCOUNT_ID = os.getenv("SNOWFLAKE_ACCOUNT_ID")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PRIVATE_KEY_PATH = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")

st.set_page_config(page_title="Stock Data Pipeline Dashboard", layout="wide")

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT_ID,
        user=SNOWFLAKE_USER,
        private_key_file=SNOWFLAKE_PRIVATE_KEY_PATH,
        warehouse="compute_wh",
        database="stock_pipeline",
        schema="marts"
    )

@st.cache_data(ttl=600)
def load_data():
    conn = get_connection()
    query = "SELECT * FROM fct_daily_prices ORDER BY trade_date DESC"
    return pd.read_sql(query, conn)

df = load_data()

st.title("Stock Data Pipeline — Dashboard")
st.caption("Data sourced via Alpha Vantage → S3 → Snowflake, incrementally merged daily via Airflow")

# --- Filters ---
tickers = sorted(df["SYMBOL"].unique())
selected = st.multiselect("Select tickers", tickers, default=tickers)
filtered = df[df["SYMBOL"].isin(selected)]

# --- Scorecards ---
col1, col2, col3 = st.columns(3)
col1.metric("Tickers tracked", len(tickers))
col2.metric("Total trading days", df["TRADE_DATE"].nunique())
col3.metric("Latest data date", str(df["TRADE_DATE"].max()))

# --- Price trend chart ---
st.subheader("Closing price over time")
fig_price = px.line(filtered, x="TRADE_DATE", y="CLOSE", color="SYMBOL")
st.plotly_chart(fig_price, width='stretch')

# --- Volume chart ---
st.subheader("Trading volume over time")
fig_vol = px.bar(filtered, x="TRADE_DATE", y="VOLUME", color="SYMBOL")
st.plotly_chart(fig_vol, width='stretch')

# --- Raw data table ---
st.subheader("Raw data")
st.dataframe(filtered.sort_values("TRADE_DATE", ascending=False), width='stretch')

