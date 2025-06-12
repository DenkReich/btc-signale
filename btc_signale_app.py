import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(page_title="📈 Krypto Daytrading Signale", layout="centered")

st.title("📉 Krypto Daytrading Signale (BTC / ETH / SOL)")
st.markdown("Live-Signale für **BTC**, **ETH** und **SOL** mit Kauf/Verkauf, SL & TP")

coin = st.selectbox("🔍 Wähle ein Asset:", ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"])
symbol = {"Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD"}[coin]

# Daten abrufen
df = yf.download(symbol, interval="5m", period="1d")
df.dropna(inplace=True)

# MultiIndex anpassen (Spaltennamen sind z. B. ('Close', 'btc-usd'))
# Einfacher Zugriff vorbereiten
df.columns = [tuple(str(col).lower().replace(" ", "").replace("-", "") for col in col) if isinstance(col, tuple) else col.lower() for col in df.columns]

# Zugriff auf Spalten korrekt setzen
close_col = ('close', 'btcusd')
open_col = ('open', 'btcusd')

# RSI & EMA berechnen mit richtigen Spalten
df['rsi'] = ta.momentum.RSIIndicator(close=df[close_col]).rsi()
df['ema_fast'] = ta.trend.EMAIndicator(close=df[close_col], window=9).ema_indicator()
df['ema_slow'] = ta.trend.EMAIndicator(close=df[close_col], window=21).ema_indicator()

# Signal-Logik
def get_signal(row):
    if row['rsi'] < 30 and row['ema_fast'] > row['ema_slow']:
        return "📈 Kauf"
    elif row['rsi'] > 70 and row['ema_fast'] < row['ema_slow']:
        return "📉 Verkauf"
    return "⏸️ Neutral"

df['Signal'] = df.apply(get_signal, axis=1)

# SL & TP
df['Stop-Loss'] = df[close_col] * 0.98
df['Take-Profit'] = df[close_col] * 1.02

# Letztes Signal
latest = df.iloc[-1]

st.subheader(f"Aktuelles Signal für {coin}:")
st.markdown(f"**{latest['Signal']}** bei Preis **{df[close_col].iloc[-1]:.2f} USD**")
st.write(f"SL: {latest['Stop-Loss']:.2f} USD  |  TP: {latest['Take-Profit']:.2f} USD")

# Chart anzeigen
chart_df = pd.DataFrame({
    'Close': df[close_col],
    'EMA Fast': df['ema_fast'],
    'EMA Slow': df['ema_slow']
}).dropna()

st.line_chart(chart_df)
