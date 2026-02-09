import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import argrelextrema

# Page Config
st.set_page_config(page_title="LiquidityHunter: Heatmap Estimator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1 { color: #FF4B4B; font-family: 'Arial', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 LiquidityHunter: Estimated Liquidation Heatmap")
st.markdown("""
This tool visualizes **potential liquidation levels** (liquidity pools) based on market structure. 
It operates on the logic that high-leverage stops and liquidations are clustered around key **Swing Highs** and **Swing Lows**.
""")

# Sidebar
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Asset Ticker", value="BTC-USD")
period = st.sidebar.selectbox("Data Period", ["1mo", "3mo", "6mo"], index=1)
interval = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"], index=2)

leverage_tiers = st.sidebar.multiselect(
    "Simulate Liquidation Levels for Leverage:",
    ["10x", "25x", "50x", "100x"],
    default=["25x", "50x"]
)

# --- Functions ---

def get_market_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval, progress=False)
    data.reset_index(inplace=True)
    return data

def find_swing_points(df, order=5):
    """Identifies local peaks (Swing Highs) and troughs (Swing Lows)."""
    # Find local maxima
    df['Swing_High'] = df.iloc[argrelextrema(df['High'].values, np.greater_equal, order=order)[0]]['High']
    # Find local minima
    df['Swing_Low'] = df.iloc[argrelextrema(df['Low'].values, np.less_equal, order=order)[0]]['Low']
    return df

def calculate_liquidation_zones(df, leverages):
    """
    Estimates where liquidations might occur based on swing points.
    Logic: If a Swing Low is broken, Longs are liquidated.
    Liquidation Price ≈ Entry Price * (1 - 1/Leverage)
    """
    zones = []
    
    # Process Long Liquidations (Below Swing Lows)
    swing_lows = df['Swing_Low'].dropna().values
    for price in swing_lows:
        for lev in leverages:
            lev_val = int(lev.replace('x', ''))
            # Assumption: Traders entered LONG at the Swing Low support
            # Liquidation roughly: Price - (Price / Leverage)
            liq_price = price - (price * (1 / lev_val))
            zones.append({'Price': liq_price, 'Type': 'Long Liq', 'Strength': lev_val})

    # Process Short Liquidations (Above Swing Highs)
    swing_highs = df['Swing_High'].dropna().values
    for price in swing_highs:
        for lev in leverages:
            lev_val = int(lev.replace('x', ''))
            # Assumption: Traders entered SHORT at the Swing High resistance
            # Liquidation roughly: Price + (Price / Leverage)
            liq_price = price + (price * (1 / lev_val))
            zones.append({'Price': liq_price, 'Type': 'Short Liq', 'Strength': lev_val})
            
    return pd.DataFrame(zones)

# --- Main Execution ---

if st.sidebar.button("Generate Heatmap"):
    with st.spinner("Calculating market structure & liquidity zones..."):
        df = get_market_data(ticker, period, interval)
        
        if df is not None and not df.empty:
            df = find_swing_points(df)
            
            # Calculate Zones
            liq_df = calculate_liquidation_zones(df, leverage_tiers)
            
            # Get Current Price
            current_price = df['Close'].iloc[-1]
            
            # Filter Zones close to current price for better visualization (e.g., +/- 10%)
            if not liq_df.empty:
                range_mask = (liq_df['Price'] > current_price * 0.85) & (liq_df['Price'] < current_price * 1.15)
                liq_df_filtered = liq_df[range_mask]
            else:
                liq_df_filtered = liq_df

            # --- Visualization ---
            fig = go.Figure()

            # 1. Candlestick Chart
            fig.add_trace(go.Candlestick(
                x=df['Date'], open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Price Action"
            ))

            # 2. Liquidity Heatmap (Horizontal Lines)
            # We use opacity to create a "Heatmap" effect. More overlapping lines = Darker/Hotter zone.
            if not liq_df_filtered.empty:
                for _, row in liq_df_filtered.iterrows():
                    color = "red" if row['Type'] == 'Short Liq' else "green"
                    fig.add_hrect(
                        y0=row['Price'] * 0.998, # Small buffer for thickness
                        y1=row['Price'] * 1.002,
                        fillcolor=color, opacity=0.02, # Very low opacity to stack
                        line_width=0, layer="below"
                    )

            # Layout Improvements
            fig.update_layout(
                title=f"{ticker} Liquidity Magnet Map (Estimated)",
                height=700,
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                paper_bgcolor="#0E1117"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insight Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.info("""
                **🟢 Green Zones (Long Liquidations):** Areas below Swing Lows. If price drops here, Long positions get liquidated, potentially causing a 'Long Squeeze' (Price bounces up).
                """)
            with col2:
                st.info("""
                **🔴 Red Zones (Short Liquidations):** Areas above Swing Highs. If price rises here, Short positions get liquidated, potentially causing a 'Short Squeeze' (Price shoots higher).
                """)

        else:
            st.error("Could not fetch data.")

else:
    st.info("Click 'Generate Heatmap' to visualize potential liquidity clusters.")
