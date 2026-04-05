# AI Market Trend Analyzer

## What this tool does

This tool is an AI-powered market trend analysis system. It fetches real-time financial data, performs technical analysis, and generates AI-driven summaries of market trends. It also incorporates a risk assessment component and stores historical analysis insights for contextual comparison. The system outputs comprehensive PDF reports.

## How it works

The system operates through a FastAPI backend that exposes several API endpoints:

1.  **Data Acquisition**: The `MarketService` component uses `yfinance` to fetch historical market data for specified symbols, periods, and intervals. This data forms the basis for all subsequent analysis.
2.  **Technical Analysis**: The `MarketService` then applies various technical indicators (RSI, SMA, MACD, ATR) to the fetched data to identify trends and volatility. It also calculates a proprietary risk score.
3.  **AI-Powered Summarization**: The `AIService` leverages OpenAI's Large Language Models (LLMs) to generate concise, professional summaries of the market trends and risk assessments. Before generating a new summary, it queries `ChromaDB` (a vector database) for similar historical insights, allowing the AI to provide context-aware analysis.
4.  **Reporting**: The `ReportService` compiles the analysis data and AI summary into a professionally formatted PDF report.
5.  **Data Persistence**: Market data and analysis results are stored in a SQLite database.

## Technical Stack

*   **Backend Framework**: FastAPI (Python 3.11+)
*   **Data Analysis**: Pandas, Pandas-TA, NumPy
*   **AI/ML Libraries**: OpenAI API
*   **Vector Database**: ChromaDB
*   **Relational Database**: SQLite
*   **PDF Generation**: ReportLab
*   **Web Server**: Uvicorn (ASGI)
*   **Testing**: Pytest, httpx, unittest.mock
*   **Dependency Management**: `pip`
*   **Environment Management**: `venv`, `python-dotenv`

## Challenges & Trade-offs

Developing a robust market analysis tool, especially for deployment in diverse environments like Termux on mobile devices, presented several technical challenges and required specific design trade-offs:

1.  **Yahoo Finance 401 Errors in Termux**: Reliably fetching data from Yahoo Finance proved challenging in non-standard environments like Termux. While `yfinance` is generally robust, intermittent 401 Unauthorized errors were observed. This was mitigated by ensuring the `yfinance` library was up-to-date and by designing the system to gracefully handle transient network issues, rather than implementing complex custom header rotation which could introduce maintenance overhead.
2.  **Resource Constraints on Mobile (Termux)**: Running data-intensive Python applications on mobile platforms via Termux necessitates careful resource management. This influenced the choice of SQLite for local data persistence and the optimization of data processing routines to minimize memory footprint and CPU usage. A trade-off was made to prioritize efficiency over highly complex, real-time streaming data processing that would be more suited for server-grade hardware.
3.  **Balancing Accuracy and Speed in AI Summarization**: Integrating LLMs for market summarization requires a balance between the depth of analysis and response time. The `max_tokens` and `temperature` parameters for the OpenAI API were fine-tuned to generate concise yet informative summaries without excessive latency. The use of `ChromaDB` for historical insights helps in providing context without requiring the LLM to process vast amounts of raw historical data for every query.
4.  **API Key Security**: Storing and managing API keys securely in a mobile-first development environment (Termux) is critical. The decision to use `.env` files and `python-dotenv` was a pragmatic choice to prevent hardcoding credentials, balancing security with ease of setup for developers.

## How to Run (for Termux/Linux Users)

To set up and operate the AI Market Trend Analyzer on your Termux or Linux environment, follow these instructions:

### Prerequisites

*   **Python 3.11+**: Ensure Python version 3.11 or newer is installed.
*   **`pip`**: The Python package installer should be available.
*   For Termux users, install Python and pip using `pkg install python`.

### Installation Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/salah619/AI-Market-Trend-Analyzer.git
    cd AI-Market-Trend-Analyzer
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # For Linux/Termux
    # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the project's root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```
    *Replace `YOUR_OPENAI_API_KEY` with your actual OpenAI API key, obtainable from the [OpenAI Platform](https://platform.openai.com/).*

### Running the Application

To launch the FastAPI application, execute the following command from the project's root directory:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be accessible, and its interactive documentation (Swagger UI) can be viewed at `http://localhost:8000/docs` in your web browser.

### Running Tests

To ensure the system's stability and integrity, execute the comprehensive test suite:

```bash
pytest tests/
```

## Architectural Diagram

```mermaid
graph TD
    A[Client Request] --> B(FastAPI Application)
    B --> C{API Endpoints}
    C --> D[MarketService: Data Acquisition & Technical Analysis]
    D --> E[Yahoo Finance API]
    D --> F[Pandas & Pandas-TA]
    C --> G[AIService: LLM Summary & Vector Memory]
    G --> H[OpenAI API]
    G --> I[ChromaDB (Historical Insights)]
    C --> J[ReportService: PDF Generation]
    J --> K[ReportLab]
    D --> L[SQLite Database]
    G --> L
    J --> L
    L --> M[Market Data & Analysis Results]
    B --> N[Pydantic: Data Validation]
    B --> O[Uvicorn: ASGI Server]
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
