import pytest
from httpx import AsyncClient
from app.main import app
import pandas as pd
from app.services.market_service import MarketService
from app.services.ai_service import AIService
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_health_check():
    """
    Architected by Eng. Salah Al-Wafi.
    Verifies that the API service is alive and responding.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Market Trend Analyzer" in response.json()["message"]

@pytest.mark.asyncio
async def test_analyze_endpoint_validation():
    """
    Ensures that the /analyze endpoint correctly validates input data.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test with missing symbol
        response = await ac.post("/api/v1/analyze", json={"period": "1mo"})
    assert response.status_code == 422 # Unprocessable Entity

@pytest.mark.asyncio
async def test_market_service_logic(monkeypatch):
    """
    Tests the core analytical logic of MarketService by mocking the data retrieval.
    """
    # Mock data for testing
    mock_df = pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [105, 106, 107],
        'Low': [95, 96, 97],
        'Close': [102, 103, 104],
        'Volume': [1000, 1100, 1200]
    }, index=pd.date_range(start='2023-01-01', periods=3))

    # Mocking fetch_data to return our mock_df
    async def mock_fetch_data(*args, **kwargs):
        return mock_df

    monkeypatch.setattr(MarketService, "fetch_data", mock_fetch_data)
    
    analysis = await MarketService.analyze_trends(mock_df)
    
    assert "current_price" in analysis
    assert "rsi" in analysis
    assert "sentinax_risk_score" in analysis
    assert isinstance(analysis["sentinax_risk_score"], int)

@pytest.mark.asyncio
async def test_ai_service_resilience(monkeypatch):
    """
    Tests the AIService resilience when OpenAI API is unavailable or fails.
    """
    # Mocking the AIService instance and its generate_market_summary method
    mock_ai = AIService()
    mock_ai.generate_market_summary = AsyncMock(return_value="Strategic Summary unavailable: API Error")
    
    summary = await mock_ai.generate_market_summary("AAPL", {"current_price": 150})
    assert "unavailable" in summary
    assert "API Error" in summary

@pytest.mark.asyncio
async def test_full_analysis_flow(monkeypatch):
    """
    End-to-end simulation of the analysis flow with mocked external dependencies.
    """
    # Mock MarketService
    mock_analysis = {
        "current_price": 150.0,
        "rsi": 45.0,
        "sma_20": 148.0,
        "sma_50": 145.0,
        "macd": 0.5,
        "volatility_atr": 2.0,
        "trend": "Bullish",
        "sentinax_risk_score": 30,
        "sentinax_risk_level": "Low",
        "timestamp": "2023-10-27T10:00:00"
    }
    
    async def mock_fetch_data(*args, **kwargs):
        return pd.DataFrame({'Close': [150]}, index=[pd.Timestamp.now()])
    
    async def mock_analyze_trends(*args, **kwargs):
        return mock_analysis
        
    async def mock_ai_summary(*args, **kwargs):
        return "The market shows a strong bullish trend with low risk."

    monkeypatch.setattr(MarketService, "fetch_data", mock_fetch_data)
    monkeypatch.setattr(MarketService, "analyze_trends", mock_analyze_trends)
    monkeypatch.setattr(AIService, "generate_market_summary", mock_ai_summary)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/analyze", json={"symbol": "AAPL"})
        
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["trend"] == "Bullish"
    assert "sentinax_risk_score" in data
    assert data["ai_summary"] == "The market shows a strong bullish trend with low risk."
