from openai import OpenAI
from app.core.config import settings
import os

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))

    async def generate_market_summary(self, symbol: str, analysis_data: dict) -> str:
        prompt = f"""
        As a Senior Financial Analyst, provide a concise summary for {symbol}.
        Current Data:
        - Price: {analysis_data['current_price']}
        - RSI (14): {analysis_data['rsi']:.2f}
        - SMA 20: {analysis_data['sma_20']:.2f}
        - SMA 50: {analysis_data['sma_50']:.2f}
        - Overall Trend: {analysis_data['trend']}
        
        Please explain what these indicators mean for the short-term outlook in a professional yet human-like manner.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional financial market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI Summary unavailable: {str(e)}"
