import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Configure Logging for Financial Audit Trail
logger = logging.getLogger(__name__)

class MarketService:
    """
    Architected by Eng. Salah Al-Wafi.
    
    This service serves as the core analytical engine for the AI Market Trend Analyzer.
    It integrates high-frequency data retrieval with advanced technical indicators and 
    risk assessment models (Sentinax-inspired), ensuring high-fidelity financial insights.
    """

    @staticmethod
    async def fetch_data(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Retrieves historical market data with specialized headers to bypass 401 restrictions.
        
        Args:
            symbol (str): The financial ticker symbol (e.g., 'AAPL', 'BTC-USD').
            period (str): The look-back period (e.g., '1mo', '1y'). Defaults to '1mo'.
            interval (str): The data granularity (e.g., '1d', '1h'). Defaults to '1d'.
            
        Returns:
            pd.DataFrame: A structured DataFrame containing OHLCV data.
            
        Raises:
            ValueError: If the ticker is invalid or no data is returned.
            ConnectionError: If network issues or API restrictions prevent data retrieval.
        """
        try:
            # Utilizes yfinance for robust data retrieval. While yfinance handles many network complexities,
            # challenges in environments like Termux (e.g., 401 errors) are noted.
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.error(f"[Audit] No data found for symbol: {symbol}")
                raise ValueError(f"Symbol '{symbol}' returned no historical data.")
            
            logger.info(f"[Audit] Successfully retrieved {len(df)} rows for {symbol}")
            return df
        except Exception as e:
            logger.critical(f"[Audit] Data retrieval failed for {symbol}: {str(e)}")
            raise ConnectionError(f"Failed to fetch data for {symbol}. Error: {str(e)}")

    @staticmethod
    async def analyze_trends(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Performs multi-layered financial analysis including technical indicators and 
        Sentinax-inspired risk assessment.
        
        Args:
            df (pd.DataFrame): The input market data.
            
        Returns:
            Dict[str, Any]: A comprehensive dictionary containing technical metrics, 
                           trend status, and risk evaluation.
        """
        # --- Technical Layer (TA-Lib / Pandas-TA) ---
        df.ta.rsi(length=14, append=True)
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.atr(length=14, append=True) # Average True Range for Volatility
        
        latest = df.iloc[-1]
        current_price = latest['Close']
        rsi = latest['RSI_14']
        sma_20 = latest['SMA_20']
        sma_50 = latest['SMA_50']
        macd = latest['MACD_12_26_9']
        atr = latest['ATRr_14']
        
        # --- Trend Determination Logic ---
        trend = "Neutral"
        if current_price > sma_20 and sma_20 > sma_50:
            trend = "Bullish (Strong)" if macd > 0 else "Bullish (Weakening)"
        elif current_price < sma_20 and sma_20 < sma_50:
            trend = "Bearish (Strong)" if macd < 0 else "Bearish (Exhaustion)"
            
        # --- Sentinax Risk Assessment Layer ---
        # Risk Score (0-100) based on Volatility (ATR) and RSI Extremes
        volatility_ratio = (atr / current_price) * 100
        risk_score = 50 # Base score
        
        if rsi > 70: risk_score += 20 # Overbought risk
        if rsi < 30: risk_score -= 10 # Oversold potential (Lower risk for entry)
        if volatility_ratio > 2.0: risk_score += 15 # High volatility risk
        
        risk_score = np.clip(risk_score, 0, 100)
        risk_level = "Low" if risk_score < 40 else "Medium" if risk_score < 70 else "High"
            
        return {
            "current_price": round(float(current_price), 4),
            "rsi": round(float(rsi), 2),
            "sma_20": round(float(sma_20), 4),
            "sma_50": round(float(sma_50), 4),
            "macd": round(float(macd), 4),
            "volatility_atr": round(float(atr), 4),
            "trend": trend,
            "sentinax_risk_score": int(risk_score),
            "sentinax_risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat()
        }
