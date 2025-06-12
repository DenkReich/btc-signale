import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(page_title="btc-signale", layout="centered")
st.title("📈 Krypto Daytrading Signale (BTC / ETH / SOL)")
st.markdown("Live-Signale für **BTC**, **ETH** und **SOL** mit Kauf/Verkauf, SL & TP")

symbols = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD"
}

selected = st.selectbox("🔍 Wähle ein Asset:", list(symbols.keys()))
symbol = symbols[selected]

# Daten abrufen
df = yf.download(symbol, interval="5m", period="1d")
df.dropna(inplace=True)

# RSI & EMA berechnen
df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
ema_fast = ta.trend.EMAIndicator(df["Close"], window=9).ema_indicator()
ema_slow = ta.trend.EMAIndicator(df["Close"], window=21).ema_indicator()

# Signal-Logik
last_rsi = df["rsi"].iloc[-1]
last_price = df["Close"].iloc[-1]
signal = "⚪️ Neutral"
sl = tp = None

if last_rsi < 30 and ema_fast.iloc[-1] > ema_slow.iloc[-1]:
    signal = "🟢 Kauf"
    sl = round(last_price * 0.98, 2)
    tp = round(last_price * 1.03, 2)
elif last_rsi > 70 and ema_fast.iloc[-1] < ema_slow.iloc[-1]:
    signal = "🔴 Verkauf"
    sl = round(last_price * 1.02, 2)
    tp = round(last_price * 0.97, 2)

# Anzeige
st.metric("📊 Letzter Preis", f"${last_price:.2f}")
st.metric("📍 RSI", f"{last_rsi:.2f}")
st.metric("📣 Signal", signal)

if sl and tp:
    st.write(f"💣 **Stop-Loss**: `${sl}`")
    st.write(f"🎯 **Take-Profit**: `${tp}`")
