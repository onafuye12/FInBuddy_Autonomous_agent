# 📊 FinBuddy Stock Analyzer

**AI-powered stock analysis tool** that combines real-time market data, news aggregation, and GPT-4-powered insights in an interactive Streamlit dashboard.

![Demo Screenshot](https://via.placeholder.com/800x400?text=FinBuddy+Stock+Analyzer+Dashboard) *(Replace with actual screenshot)*

## 🌟 Features

- **Comprehensive Stock Analysis**
  - Real-time price data via Yahoo Finance
  - Financial statements (income, balance sheet)
  - Technical indicators (50/200-day moving averages)

- **Multi-Source News Aggregation**
  - Yahoo Finance news API
  - Finnhub company news (with API key)
  - Web scraping for Apple/MSFT/Amazon press releases

- **AI-Powered Reports**
  - GPT-4 generated analysis (5-part reports)
  - Business overview, financial health, recommendations
  - RAG (Retrieval-Augmented Generation) architecture

- **Interactive Visualization**
  - Plotly candlestick charts
  - Moving average trends
  - Responsive Streamlit UI

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [OpenAI API key](https://platform.openai.com/api-keys)
- (Optional) [Finnhub API key](https://finnhub.io)

### Installation
```bash
git clone https://github.com/yourusername/FinBuddy_Autonomous_agent.git
cd FinBuddy_Autonomous_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt