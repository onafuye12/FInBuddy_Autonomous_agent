import os
import yfinance as yf
import pandas as pd
import requests
import json
from openai import OpenAI
import streamlit as st
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  # Alternative news source

class StockAnalyzer:
    def __init__(self):
        self.cache = {}
        self.news_sources = [
            self._get_finnhub_news,
            self._get_yfinance_news,
            self._get_web_news
        ]
    
    def get_stock_data(self, symbol):
        """Get core stock data from Yahoo Finance with validation"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="6mo")
            
            if not info or hist.empty:
                st.warning(f"Incomplete data for {symbol}")
                return None
                
            return {
                'info': info,
                'historical': hist,
                'financials': ticker.financials,
                'balance_sheet': ticker.balance_sheet
            }
        except Exception as e:
            st.error(f"Data fetch error: {str(e)}")
            return None
    
    def _get_finnhub_news(self, symbol):
        """Get news from Finnhub API"""
        if not FINNHUB_API_KEY:
            return []
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"https://finnhub.io/api/v1/company-news?symbol={symbol}"
                f"&from={week_ago}&to={today}&token={FINNHUB_API_KEY}",
                timeout=10
            )
            response.raise_for_status()
            
            news_items = []
            for item in response.json():
                if not item.get('headline'):
                    continue
                    
                news_items.append({
                    'title': item.get('headline', 'No title available').strip(),
                    'url': item.get('url', '#'),
                    'source': item.get('source', 'Finnhub'),
                    'date': self._format_timestamp(item.get('datetime')),
                    'summary': item.get('summary', 'Click to read full article').strip()
                })
                if len(news_items) >= 5:  # Limit to 5 articles per source
                    break
            return news_items
        except Exception as e:
            st.warning(f"Finnhub news error: {str(e)}")
            return []

    def _get_yfinance_news(self, symbol):
        """Get news from Yahoo Finance"""
        try:
            news_items = []
            yf_news = yf.Ticker(symbol).news or []
            
            for item in yf_news:
                if not item.get('title'):
                    continue
                    
                news_items.append({
                    'title': item.get('title', 'No title available').strip(),
                    'url': item.get('link', '#'),
                    'source': item.get('publisher', 'Yahoo Finance'),
                    'date': self._format_timestamp(item.get('providerPublishTime')),
                    'summary': item.get('summary', 'Click to read full article').strip()
                })
                if len(news_items) >= 5:  # Limit to 5 articles per source
                    break
            return news_items
        except Exception as e:
            st.warning(f"Yahoo Finance news error: {str(e)}")
            return []

    def _get_web_news(self, symbol):
        """Get news from web scraping (company-specific)"""
        try:
            if symbol == "AAPL":
                return self._get_apple_news()
            elif symbol == "MSFT":
                return self._get_microsoft_news()
            elif symbol == "AMZN":
                return self._get_amazon_news()
            return []
        except Exception as e:
            st.warning(f"Web news error: {str(e)}")
            return []

    def _get_apple_news(self):
        """Scrape Apple newsroom"""
        try:
            response = requests.get(
                "https://www.apple.com/newsroom/", 
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            for article in soup.select('.article-link'):
                title = article.get_text(strip=True)
                if not title:
                    continue
                    
                news_items.append({
                    'title': title,
                    'url': f"https://www.apple.com{article['href']}",
                    'source': 'Apple Newsroom',
                    'date': '',
                    'summary': 'Official Apple press release'
                })
                if len(news_items) >= 3:  # Limit to 3 articles
                    break
            return news_items
        except:
            return []

    def _get_microsoft_news(self):
        """Scrape Microsoft news"""
        try:
            response = requests.get(
                "https://news.microsoft.com/", 
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            for article in soup.select('.article-title'):
                title = article.get_text(strip=True)
                if not title:
                    continue
                    
                link = article.find('a')
                if not link:
                    continue
                    
                news_items.append({
                    'title': title,
                    'url': link['href'],
                    'source': 'Microsoft News',
                    'date': '',
                    'summary': 'Official Microsoft news'
                })
                if len(news_items) >= 3:  # Limit to 3 articles
                    break
            return news_items
        except:
            return []

    def _get_amazon_news(self):
        """Scrape Amazon news"""
        try:
            response = requests.get(
                "https://www.aboutamazon.com/news", 
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=10
            )
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            for article in soup.select('.post-item'):
                title = article.find('h2')
                if not title:
                    continue
                    
                link = article.find('a')
                if not link:
                    continue
                    
                news_items.append({
                    'title': title.get_text(strip=True),
                    'url': link['href'],
                    'source': 'Amazon News',
                    'date': '',
                    'summary': 'Official Amazon news'
                })
                if len(news_items) >= 3:  # Limit to 3 articles
                    break
            return news_items
        except:
            return []

    def _format_timestamp(self, timestamp):
        """Convert timestamp to readable date"""
        if not timestamp:
            return ''
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            return str(timestamp)
        except:
            return ''

    def get_company_news(self, symbol):
        """Get news from all available sources with deduplication"""
        news_items = []
        seen_titles = set()
        
        for source in self.news_sources:
            try:
                for item in source(symbol):
                    # Basic validation and deduplication
                    title = item.get('title', '').strip()
                    if (title and 
                        title.lower() not in seen_titles and
                        title != 'No title available'):
                        
                        seen_titles.add(title.lower())
                        news_items.append(item)
                        
                        if len(news_items) >= 5:  # Limit to 5 total articles
                            return news_items
            except:
                continue
                
        return news_items[:5]  # Return at most 5 articles

    def generate_report(self, symbol, company_name):
        """Generate comprehensive report using RAG approach"""
        try:
            # Step 1: Retrieve relevant context
            context = self._gather_company_context(symbol, company_name)
            
            if not context:
                return "⚠️ Could not gather enough data to generate report"
            
            # Step 2: Generate report with LLM
            if not client:
                return "OpenAI API key required for report generation"
            
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a professional financial analyst. Generate a comprehensive report using this context:\n" + context
                }, {
                    "role": "user",
                    "content": f"Create a detailed 5-part analysis report for {company_name} ({symbol}):\n"
                               "1) Business Overview\n2) Financial Health\n3) Recent Developments\n"
                               "4) Technical Analysis\n5) Investment Recommendation\n\n"
                               "Use professional tone with markdown formatting including ## headings and bullet points."
                }],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ Report generation error: {str(e)}"
    
    def _gather_company_context(self, symbol, company_name):
        """Retrieve comprehensive context for RAG from multiple sources"""
        context = f"Company: {company_name} ({symbol})\n\n"
        
        # 1. Basic company info
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            context += "## Basic Information\n"
            context += f"- Sector: {info.get('sector', 'N/A')}\n"
            context += f"- Industry: {info.get('industry', 'N/A')}\n"
            context += f"- Market Cap: ${info.get('marketCap', 'N/A'):,}\n"
            context += f"- Employees: {info.get('fullTimeEmployees', 'N/A')}\n\n"
        except:
            pass
        
        # 2. Financial metrics
        try:
            context += "## Financial Metrics\n"
            context += f"- P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
            context += f"- Profit Margin: {info.get('profitMargins', 'N/A')}\n"
            context += f"- Revenue Growth: {info.get('revenueGrowth', 'N/A')}\n"
            context += f"- Debt/Equity: {info.get('debtToEquity', 'N/A')}\n\n"
        except:
            pass
        
        # 3. Recent news highlights
        news = self.get_company_news(symbol)
        if news:
            context += "## Recent News Highlights\n"
            for item in news[:3]:
                context += f"- {item['title']} ({item['source']})\n"
            context += "\n"
        
        # 4. Technical indicators
        try:
            hist = yf.Ticker(symbol).history(period="6mo")
            if not hist.empty:
                sma50 = hist['Close'].rolling(50).mean().iloc[-1]
                sma200 = hist['Close'].rolling(200).mean().iloc[-1]
                context += "## Technical Indicators\n"
                context += f"- Current Price: ${hist['Close'].iloc[-1]:.2f}\n"
                context += f"- 50-day MA: ${sma50:.2f}\n"
                context += f"- 200-day MA: ${sma200:.2f}\n"
                context += f"- Trend: {'Bullish' if sma50 > sma200 else 'Bearish'}\n\n"
        except:
            pass
        
        return context
    
    def prepare_charts(self, historical_data):
        """Create interactive price charts with error handling"""
        try:
            # Price chart
            price_fig = go.Figure(go.Candlestick(
                x=historical_data.index,
                open=historical_data['Open'],
                high=historical_data['High'],
                low=historical_data['Low'],
                close=historical_data['Close'],
                name='Price'
            ))
            price_fig.update_layout(
                title="Price History",
                yaxis_title="Price ($)",
                xaxis_rangeslider_visible=False
            )
            
            # Moving averages chart
            ma_fig = go.Figure()
            ma_fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data['Close'].rolling(50).mean(),
                name='50-day MA',
                line=dict(color='blue')
            ))
            ma_fig.add_trace(go.Scatter(
                x=historical_data.index,
                y=historical_data['Close'].rolling(200).mean(),
                name='200-day MA',
                line=dict(color='orange')
            ))
            ma_fig.update_layout(
                title="Moving Averages",
                yaxis_title="Price ($)"
            )
            
            return {'price': price_fig, 'moving_averages': ma_fig}
        except Exception as e:
            st.error(f"Chart error: {str(e)}")
            return None

def load_stock_data():
    """Load stock data from JSON file with error handling"""
    try:
        with open('us_stocks.json') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: us_stocks.json file not found")
        return None
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON format in us_stocks.json")
        return None
    except Exception as e:
        st.error(f"Error loading stock data: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="FinBuddy Stock Analyzer",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 FinBuddy Stock Analysis")
    
    # Load stock data
    stock_data = load_stock_data()
    if not stock_data:
        st.error("Failed to load stock data. Please check us_stocks.json file.")
        return
    
    with st.sidebar:
        st.header("Stock Selection")
        
        # Sector selection
        sector = st.selectbox(
            "Select Sector",
            list(stock_data.keys()),
            key="sector_select"
        )
        
        # Company selection with search
        companies = list(stock_data[sector].items())
        search_term = st.text_input("Search companies", "", key="company_search")
        
        # Filter companies based on search
        filtered_companies = [
            (name, symbol) for name, symbol in companies
            if search_term.lower() in name.lower()
        ]
        
        if not filtered_companies:
            st.warning("No companies match your search")
            return
        
        selected_company = st.selectbox(
            "Select Company",
            filtered_companies,
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key="company_select"
        )
        
        if st.button("Analyze", type="primary", use_container_width=True):
            st.session_state.run_analysis = True
            st.session_state.selected_symbol = selected_company[1]
            st.session_state.selected_name = selected_company[0]
            st.rerun()
    
    if st.session_state.get('run_analysis', False):
        analyzer = StockAnalyzer()
        
        with st.spinner(f"Analyzing {st.session_state.selected_name}..."):
            # Get all data components
            stock_data = analyzer.get_stock_data(st.session_state.selected_symbol)
            if not stock_data:
                st.error("Failed to fetch stock data")
                return
            
            news = analyzer.get_company_news(st.session_state.selected_symbol)
            report = analyzer.generate_report(
                st.session_state.selected_symbol,
                st.session_state.selected_name
            )
            charts = analyzer.prepare_charts(stock_data['historical'])
            
            # Store results
            st.session_state.result = {
                'name': st.session_state.selected_name,
                'symbol': st.session_state.selected_symbol,
                'report': report,
                'news': news,
                'charts': charts
            }
    
    if 'result' in st.session_state:
        result = st.session_state.result
        
        st.header(f"{result['name']} ({result['symbol']})")
        
        tab1, tab2, tab3 = st.tabs(["Analysis Report", "Price Charts", "Market News"])
        
        with tab1:
            st.markdown(result['report'])
        
        with tab2:
            if result['charts']:
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(result['charts']['price'], use_container_width=True)
                with col2:
                    st.plotly_chart(result['charts']['moving_averages'], use_container_width=True)
            else:
                st.warning("No chart data available")
        
        with tab3:
            st.subheader("Recent Market News")
            
            if not result['news']:
                st.warning("No recent news available for this company")
            else:
                for idx, article in enumerate(result['news'], 1):
                    with st.expander(f"{idx}. {article['title']}"):
                        st.write(f"**Source:** {article['source']}")
                        if article['date']:
                            st.write(f"**Date:** {article['date']}")
                        st.write(article['summary'])
                        if article['url'] != '#':
                            st.markdown(f"[Read full article]({article['url']})")

if __name__ == "__main__":
    main()