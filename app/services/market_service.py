import yfinance as yf
import pandas as pd
import pandas_ta as ta
from typing import Dict, Any
from app.models.market import AnalysisResult
from datetime import datetime

class MarketService:
    @staticmethod
    async def fetch_data(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
        return df

    @staticmethod
    async def analyze_trends(df: pd.DataFrame) -> Dict[str, Any]:
        # Calculate Technical Indicators
        df.ta.rsi(length=14, append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        
        latest = df.iloc[-1]
        rsi = latest['RSI_14']
        sma_20 = latest['SMA_20']
        sma_50 = latest['SMA_50']
        current_price = latest['Close']
        
        # Determine Trend
        trend = "Neutral"
        if current_price > sma_20 and sma_20 > sma_50:
            trend = "Bullish"
        elif current_price < sma_20 and sma_20 < sma_50:
            trend = "Bearish"
            
        return {
            "current_price": float(current_price),
            "rsi": float(rsi),
            "sma_20": float(sma_20),
            "sma_50": float(sma_50),
            "trend": trend
        }
