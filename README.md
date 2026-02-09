# LiquidityHunter: Estimated Liquidity Heatmap

LiquidityHunter is a Python-based analytical tool designed to visualize **Market Structure** and estimate high-probability **Liquidation Zones** (Liquidity Pools) for cryptocurrencies.

Unlike paid services that use exchange-specific proprietary data, this tool uses an algorithmic approach based on **Price Action Theory** to simulate where retail stop-losses and high-leverage liquidation points are likely clustered.

## 🧠 The Logic: Magnet Theory
Market price is often attracted to areas of high liquidity ("Liquidity Pools") to facilitate large order execution.

1.  **Swing Analysis:** The algorithm identifies key local maxima (Swing Highs) and minima (Swing Lows) using `scipy.signal`.
2.  **Leverage Simulation:** It projects liquidation levels for 25x, 50x, and 100x leverage based on these swing points.
3.  **Heatmap Visualization:** These levels are overlaid on the chart with low opacity. Areas where multiple liquidation levels overlap create "Hot Zones" (Darker Red/Green areas).

## 🚀 Features
* **Swing Point Detection:** Automatically finds structural support/resistance.
* **Leverage Modeling:** Simulates liquidation prices for Longs (below support) and Shorts (above resistance).
* **Interactive Heatmap:** Visualizes liquidity density using Plotly.

## 🛠 Tech Stack
* **Python**
* **Streamlit** (UI)
* **Plotly** (Financial Charting)
* **Scipy** (Signal Processing/Extrema Detection)

## ⚠️ Disclaimer
This tool provides **estimations** based on mathematical models, not real-time exchange order book data. It is intended for educational purposes and research into market microstructure.

---
*Author: [Hamit Buyukguzel]*
