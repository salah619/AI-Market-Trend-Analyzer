from openai import OpenAI
from app.core.config import settings
import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# ChromaDB Integration for Vector Memory
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class AIService:
    """
    Architected by Eng. Salah Al-Wafi.
    
    The AIService orchestrates the intelligence layer of the system. 
    It leverages OpenAI's LLMs for natural language summarization and 
    ChromaDB for long-term vector memory of financial insights.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"))
        self.db_path = os.path.join(os.getcwd(), "chroma_db")
        
        if CHROMA_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(path=self.db_path)
                self.collection = self.chroma_client.get_or_create_collection(
                    name="market_insights",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("[Audit] ChromaDB Vector Memory initialized successfully.")
            except Exception as e:
                logger.error(f"[Audit] ChromaDB initialization failed: {str(e)}")
                self.collection = None
        else:
            logger.warning("[Audit] ChromaDB not installed. Vector memory disabled.")
            self.collection = None

    async def generate_market_summary(self, symbol: str, analysis_data: dict) -> str:
        """
        Generates a professional market summary by combining current technical data 
        with historical insights retrieved from Vector Memory (ChromaDB).
        
        Args:
            symbol (str): The financial ticker symbol.
            analysis_data (dict): Current technical analysis results.
            
        Returns:
            str: A comprehensive AI-generated market report.
        """
        # --- Retrieve Historical Context from Vector Memory ---
        historical_context = ""
        if self.collection:
            try:
                # Query for similar past insights for this symbol
                results = self.collection.query(
                    query_texts=[f"Market trend and risk for {symbol}"],
                    n_results=2,
                    where={"symbol": symbol}
                )
                if results['documents'] and results['documents'][0]:
                    historical_context = "\n### Historical Insights (Memory Retrieval):\n" + \
                                         "\n".join(results['documents'][0])
            except Exception as e:
                logger.error(f"[Audit] Failed to query ChromaDB: {str(e)}")

        # --- Construct Intelligence Prompt ---
        prompt = f"""
        Role: Senior Financial Analyst & Risk Strategist (Sentinax-inspired).
        Task: Provide a high-fidelity market summary for {symbol}.
        
        Current Market Snapshot (Technical & Risk):
        - Current Price: {analysis_data['current_price']}
        - RSI (14): {analysis_data['rsi']:.2f}
        - SMA 20/50: {analysis_data['sma_20']:.2f} / {analysis_data['sma_50']:.2f}
        - MACD: {analysis_data['macd']:.4f}
        - Volatility (ATR): {analysis_data['volatility_atr']:.4f}
        - Trend Signal: {analysis_data['trend']}
        - Sentinax Risk Score: {analysis_data['sentinax_risk_score']}/100 ({analysis_data['sentinax_risk_level']})
        
        {historical_context}
        
        Instruction: 
        1. Analyze the confluence of technical indicators.
        2. Evaluate the Sentinax risk profile.
        3. If historical context is present, compare the current trend with past insights.
        4. Provide actionable, professional commentary on the short-term outlook.
        
        Format: Professional, concise, and technical.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional financial market analyst and risk strategist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=450,
                temperature=0.7
            )
            summary = response.choices[0].message.content.strip()
            
            # --- Store Current Insight into Vector Memory for Future Comparison ---
            if self.collection:
                try:
                    insight_id = f"{symbol}_{datetime.utcnow().timestamp()}"
                    self.collection.add(
                        documents=[summary],
                        metadatas=[{"symbol": symbol, "timestamp": datetime.utcnow().isoformat()}],
                        ids=[insight_id]
                    )
                    logger.info(f"[Audit] New insight for {symbol} stored in Vector Memory.")
                except Exception as e:
                    logger.error(f"[Audit] Failed to store insight in ChromaDB: {str(e)}")
                    
            return summary
            
        except Exception as e:
            logger.critical(f"[Audit] AI Generation failed for {symbol}: {str(e)}")
            return f"Strategic Summary unavailable: {str(e)}"
