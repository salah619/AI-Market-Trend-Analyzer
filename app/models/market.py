from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MarketData(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    high: float
    low: float
    volume: float

class AnalysisResult(BaseModel):
    symbol: str
    current_price: float
    rsi: float
    sma_20: float
    sma_50: float
    trend: str
    ai_summary: str
    timestamp: datetime = datetime.now()

class AnalysisRequest(BaseModel):
    symbol: str
    period: str = "1mo"
    interval: str = "1d"
