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

# Technische Indikatoren
df.columns = [col.lower() for col in df.columns]  # Spaltennamen in Kleinbuchstaben
df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
df['ema_fast'] = ta.trend.EMAIndicator(df['Close'], window=9).ema_indicator()
df['ema_slow'] = ta.trend.EMAIndicator(df['Close'], window=21).ema_indicator()

# Signal-Logik
def get_signal(row):
    if row['rsi'] < 30 and row['ema_fast'] > row['ema_slow']:
        return "📈 Kauf"
    elif row['rsi'] > 70 and row['ema_fast'] < row['ema_slow']:
        return "📉 Verkauf"
    return "⏸️ Neutral"

df['Signal'] = df.apply(get_signal, axis=1)

# SL & TP setzen (vereinfachtes Beispiel)
df['Stop-Loss'] = df['Close'] * 0.98
df['Take-Profit'] = df['Close'] * 1.02

# Nur letztes Signal anzeigen
latest = df.iloc[-1]

st.subheader(f"Aktuelles Signal für {coin}:")
st.markdown(f"**{latest['Signal']}** bei Preis **{latest['Close']:.2f} USD**")
st.write(f"SL: {latest['Stop-Loss']:.2f} USD  |  TP: {latest['Take-Profit']:.2f} USD")

st.line_chart(df[['Close', 'ema_fast', 'ema_slow']].dropna())
