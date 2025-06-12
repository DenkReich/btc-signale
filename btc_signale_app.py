import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(page_title="📈 Krypto Daytrading Signale", layout="centered")
st.title("📉 Krypto Daytrading Signale (BTC / ETH / SOL)")
st.markdown("Live-Signale für **BTC**, **ETH** und **SOL** mit direkter Handelsempfehlung")

coin = st.selectbox("🔍 Wähle ein Asset:", ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"])
symbol = {"Bitcoin (BTC)": "BTC-USD", "Ethereum (ETH)": "ETH-USD", "Solana (SOL)": "SOL-USD"}[coin]

df = yf.download(symbol, interval="5m", period="1d")
df.dropna(inplace=True)
df.columns = [str(col).lower() for col in df.columns]

# Technische Indikatoren
df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
df['ema_fast'] = ta.trend.EMAIndicator(close=df['close'], window=9).ema_indicator()
df['ema_slow'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()

# Signal-Logik mit Preisempfehlung
def get_signal(row):
    if row['rsi'] < 30 and row['ema_fast'] > row['ema_slow']:
        return "buy"
    elif row['rsi'] > 70 and row['ema_fast'] < row['ema_slow']:
        return "sell"
    return "neutral"

df['signal'] = df.apply(get_signal, axis=1)
df['sl'] = df['close'] * 0.98
df['tp_up'] = df['close'] * 1.02
df['tp_down'] = df['close'] * 0.98

latest = df.iloc[-1]

st.subheader(f"Aktuelles Signal für {coin}:")

if latest['signal'] == "buy":
    st.success(f"📥 Jetzt **KAUFEN** bei **{latest['close']:.2f} USD**")
    st.write(f"➡️ Ziel (TP): **{latest['tp_up']:.2f} USD** | SL: **{latest['sl']:.2f} USD**")
elif latest['signal'] == "sell":
    st.error(f"📤 Jetzt **VERKAUFEN** bei **{latest['close']:.2f} USD**")
    st.write(f"➡️ Rückkauf bei (TP): **{latest['tp_down']:.2f} USD** | SL: **{latest['tp_up']:.2f} USD**")
else:
    st.info(f"⏸️ Neutral bei Preis **{latest['close']:.2f} USD**")
    st.write(f"SL: {latest['sl']:.2f} USD  |  TP: {latest['tp_up']:.2f} USD")

# Chart anzeigen
st.line_chart(df[['close', 'ema_fast', 'ema_slow']].dropna())
