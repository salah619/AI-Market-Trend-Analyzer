from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.market import AnalysisRequest, AnalysisResult
from app.services.market_service import MarketService
from app.services.ai_service import AIService
from app.services.report_service import ReportService
from datetime import datetime
import os

router = APIRouter()
ai_service = AIService()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_market(request: AnalysisRequest):
    try:
        # 1. Fetch Data
        df = await MarketService.fetch_data(request.symbol, request.period, request.interval)
        
        # 2. Technical Analysis
        analysis = await MarketService.analyze_trends(df)
        
        # 3. AI Summary
        summary = await ai_service.generate_market_summary(request.symbol, analysis)
        
        result = AnalysisResult(
            symbol=request.symbol,
            current_price=analysis['current_price'],
            rsi=analysis['rsi'],
            sma_20=analysis['sma_20'],
            sma_50=analysis['sma_50'],
            trend=analysis['trend'],
            ai_summary=summary,
            timestamp=datetime.now()
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/report/{symbol}")
async def get_report(symbol: str):
    try:
        # Perform analysis first
        df = await MarketService.fetch_data(symbol)
        analysis = await MarketService.analyze_trends(df)
        summary = await ai_service.generate_market_summary(symbol, analysis)
        
        data = {
            "symbol": symbol,
            "current_price": analysis['current_price'],
            "rsi": analysis['rsi'],
            "sma_20": analysis['sma_20'],
            "sma_50": analysis['sma_50'],
            "trend": analysis['trend'],
            "ai_summary": summary,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        report_path = f"data/{symbol}_report.pdf"
        ReportService.generate_pdf(data, report_path)
        
        return FileResponse(report_path, filename=f"{symbol}_report.pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
