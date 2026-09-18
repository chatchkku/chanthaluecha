import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

# --- 1. SETPAGE CONFIG ---
st.set_page_config(
    page_title="Chanthaluecha Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 2. CUSTOM CSS (FIXED SLIM & CLEAN BUTTONS) ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* Global Theme Settings */
        html, body, [class*="st"], [data-testid="stAppViewContainer"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #f1f5f9 !important;
            background-color: #070b12 !important;
        }

        .stApp {
            background: linear-gradient(135deg, #070b12 0%, #0b1329 100%) !important;
        }

        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none;
        }

        /* Header Styling */
        .app-header {
            background: rgba(13, 25, 48, 0.85);
            padding: 24px 30px;
            border-radius: 16px;
            border: 1px solid rgba(0, 240, 255, 0.3);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.15);
            backdrop-filter: blur(10px);
            margin-bottom: 24px;
        }
        .app-header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #00f0ff !important;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
            margin-bottom: 6px;
        }
        .app-header p {
            color: #94a3b8 !important;
            font-size: 0.95rem;
            margin: 0;
        }

        /* Metric Cards */
        .metric-card {
            background: rgba(15, 23, 42, 0.75);
            padding: 18px;
            border-radius: 14px;
            border: 1px solid rgba(0, 240, 255, 0.2);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            transition: all 0.3s ease;
            height: 100%;
        }
        .metric-card:hover {
            border-color: #00f0ff;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
            transform: translateY(-2px);
        }

        /* Fixed Slim & Clean Modern Buttons */
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            color: #ffffff !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 8px !important;
            padding: 0.4rem 1rem !important;
            min-height: 40px !important;
            width: 100% !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stButton"] > button * {
            background: transparent !important;
            background-color: transparent !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            border-color: #60a5fa !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
        }

        /* Text Input Fields */
        .stTextInput input {
            background-color: #0b1329 !important;
            color: #00f0ff !important;
            border-radius: 10px !important;
            border: 1px solid rgba(0, 240, 255, 0.3) !important;
        }
        .stTextInput input:focus {
            border-color: #00f0ff !important;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
        }

        /* Dropdown & Selectbox Override */
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"],
        div[data-baseweb="select"] input {
            background-color: #0b1329 !important;
            border-color: rgba(0, 240, 255, 0.4) !important;
            border-radius: 10px !important;
            color: #00f0ff !important;
        }
        div[data-baseweb="select"] * {
            color: #00f0ff !important;
            fill: #00f0ff !important;
        }
        
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"],
        ul[role="listbox"],
        li[role="option"] {
            background-color: #0b1329 !important;
            background: #0b1329 !important;
            border-color: rgba(0, 240, 255, 0.4) !important;
            color: #f1f5f9 !important;
        }
        li[role="option"]:hover,
        li[aria-selected="true"],
        div[role="option"]:hover {
            background-color: rgba(0, 240, 255, 0.25) !important;
            color: #00f0ff !important;
        }

        /* Checkbox Styling */
        [data-testid="stCheckbox"] {
            display: flex;
            align-items: center;
        }
        [data-testid="stCheckbox"] div[role="checkbox"] {
            background-color: #0b1329 !important;
            border: 2px solid #ef4444 !important;
            border-radius: 6px !important;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.4) !important;
            transition: all 0.2s ease-in-out;
        }
        [data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] {
            background-color: #00f0ff !important;
            border-color: #ef4444 !important;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.6) !important;
        }
        [data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] svg {
            fill: #070b12 !important;
            stroke: #070b12 !important;
            stroke-width: 2px !important;
        }
        [data-testid="stCheckbox"] label span {
            color: #f1f5f9 !important;
            font-weight: 600 !important;
        }

        /* Textarea */
        .stTextArea textarea {
            background-color: #0b1329 !important;
            color: #f1f5f9 !important;
            border: 1px solid rgba(0, 240, 255, 0.3) !important;
            border-radius: 10px !important;
        }

        /* Streamlit Expander Dark Theme */
        div[data-testid="stExpander"] {
            background-color: #0b1329 !important;
            border: 1px solid rgba(0, 240, 255, 0.2) !important;
            border-radius: 10px !important;
        }
        div[data-testid="stExpander"] details summary {
            color: #00f0ff !important;
            background-color: #0b1329 !important;
        }

        /* Headings & Metrics */
        h4 {
            color: #00f0ff !important;
            font-weight: 700 !important;
            font-size: 1.15rem !important;
            margin-top: 15px !important;
            margin-bottom: 12px !important;
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
        }
        [data-testid="stMetricValue"] {
            color: #00f0ff !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 3. SESSION STATE ---
if "active_ticker" not in st.session_state:
    st.session_state.active_ticker = "BDMS.BK"

# --- 4. HEADER ---
st.markdown(
    """
    <div class="app-header">
        <h1>📈 Chanthaluecha Intelligence Dashboard</h1>
        <p>Advanced Technical Analysis, Broker Consensus & Strategy System</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- 5. SEARCH PANEL ---
search_col1, search_col2, search_col3 = st.columns([3, 1, 1], gap="small")

with search_col1:
    user_typed_ticker = st.text_input(
        "🔍 ค้นหารหัสหลักทรัพย์ (เช่น BDMS, PTT, TCAP, GULF, IVV):",
        value=st.session_state.active_ticker.replace(".BK", ""),
        placeholder="พิมพ์รหัสหุ้น...",
        key="free_stock_input",
    )

with search_col2:
    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
    if st.button("🔍 ค้นหา", use_container_width=True):
        if user_typed_ticker.strip():
            st.session_state.active_ticker = user_typed_ticker.strip().upper()
            st.rerun()

with search_col3:
    st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 รีเซ็ต", use_container_width=True):
        st.session_state.active_ticker = "BDMS.BK"
        st.rerun()

raw_clean = st.session_state.active_ticker.strip().upper()
us_market_indicators = [
    "IVV",
    "VT",
    "AAPL",
    "TSLA",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "SPY",
    "QQQ",
    "QQQM",
    "QQQi",
    "IREN",
    "SOFI",
    "NOW",
    "MU",
    "INTC",
    "NBIS",
    "RKLB",
    "ASTS",
    "SMR",
    "EOSE",
    "NVO",
    "ORCL",
    "AVGO",
    "VXUS",
    "VOO",
    "SCHG",
    "SCHD",
    "NASA",
    "GRID",
    "SMH",
    "JEPQ",
]

if "." in raw_clean or raw_clean in us_market_indicators or len(raw_clean) > 5:
    ticker_symbol = raw_clean
else:
    ticker_symbol = raw_clean + ".BK"


# --- 6. HELPER FUNCTIONS (CACHED SAFELY WITHOUT Ticker OBJECT) ---
@st.cache_data(ttl=600)
def load_stock_data(ticker):
    stock_obj = yf.Ticker(ticker)
    hist = stock_obj.history(period="5y")

    if hist.empty and not ticker.endswith(".BK"):
        fallback_ticker = ticker + ".BK"
        stock_obj = yf.Ticker(fallback_ticker)
        hist = stock_obj.history(period="5y")
        if not hist.empty:
            return hist, stock_obj.info, stock_obj.news, fallback_ticker

    return hist, stock_obj.info, stock_obj.news, ticker


def calculate_support_resistance(ticker, interval, period):
    try:
        if interval == "15m":
            df = yf.download(
                ticker, period="5d", interval="15m", progress=False, auto_adjust=True
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        elif interval == "240m":
            df = yf.download(
                ticker, period="60d", interval="60m", progress=False, auto_adjust=True
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty or len(df) < 5:
                return None, None
            df = (
                df.resample("4h")
                .agg({
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last",
                    "Volume": "sum",
                })
                .dropna()
            )
        else:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True,
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

        if df.empty or len(df) < 5:
            return None, None

        high = df["High"].max()
        low = df["Low"].min()
        close = df["Close"].iloc[-1]

        pivot = (high + low + close) / 3
        resistance = (2 * pivot) - low
        support = (2 * pivot) - high

        return support, resistance
    except Exception:
        return None, None


def calculate_fibonacci_levels(ticker, interval, period):
    try:
        if interval == "15m":
            df = yf.download(
                ticker, period="5d", interval="15m", progress=False, auto_adjust=True
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        elif interval == "240m":
            df = yf.download(
                ticker, period="60d", interval="60m", progress=False, auto_adjust=True
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty or len(df) < 5:
                return None
            df = (
                df.resample("4h")
                .agg({
                    "Open": "first",
                    "High": "max",
                    "Low": "min",
                    "Close": "last",
                    "Volume": "sum",
                })
                .dropna()
            )
        else:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True,
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

        if df.empty or len(df) < 5:
            return None

        max_high = df["High"].max()
        min_low = df["Low"].min()
        diff = max_high - min_low

        levels = {
            "High (100%)": max_high,
            "Fib 78.6%": max_high - diff * 0.786,
            "Fib 61.8% (Golden)": max_high - diff * 0.618,
            "Fib 50.0%": max_high - diff * 0.500,
            "Fib 38.2%": max_high - diff * 0.382,
            "Fib 23.6%": max_high - diff * 0.236,
            "Low (0%)": min_low,
        }
        return levels
    except Exception:
        return None


# --- 7. MAIN APPLICATION LOGIC ---
try:
    with st.spinner(f"กำลังโหลดข้อมูล {ticker_symbol.upper()}..."):
        hist, info, news, ticker_symbol = load_stock_data(ticker_symbol)
        stock_obj = yf.Ticker(ticker_symbol)

    if hist is None or hist.empty:
        st.error(
            f"⚠️ ไม่พบข้อมูลราคาสำหรับ `{raw_clean}` กรุณาตรวจสอบรหัสใหม่อีกครั้ง"
        )
    else:
        company_name = info.get("longName", ticker_symbol)
        current_price = info.get(
            "currentPrice",
            info.get(
                "regularMarketPrice",
                hist["Close"].iloc[-1] if not hist.empty else "N/A",
            ),
        )
        previous_close = info.get(
            "previousClose",
            hist["Close"].iloc[-2] if len(hist) > 1 else current_price,
        )

        if isinstance(current_price, (int, float)) and isinstance(
            previous_close, (int, float)
        ):
            price_change = current_price - previous_close
            percent_change = (price_change / previous_close) * 100
        else:
            price_change, percent_change = 0, 0

        display_ticker_label = (
            ticker_symbol.replace(".BK", "").upper()
            if ticker_symbol.endswith(".BK")
            else ticker_symbol.upper()
        )
        st.markdown(
            f"### 📊 Security Overview: **{company_name}** (`{display_ticker_label}`)"
        )

        # Overview Metrics
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            st.metric(
                "Current Price",
                (
                    f"{current_price:,.2f}"
                    if isinstance(current_price, (int, float))
                    else "N/A"
                ),
                f"{price_change:+.2f} ({percent_change:+.2f}%)",
            )
        with col2:
            market_cap = info.get("marketCap", "N/A")
            formatted_cap = (
                f"{market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"
            )
            st.metric("Market Cap", formatted_cap)
        with col3:
            high_52 = info.get("fiftyTwoWeekHigh", "N/A")
            st.metric(
                "52 Week High",
                f"{high_52:,.2f}" if isinstance(high_52, (int, float)) else "N/A",
            )
        with col4:
            low_52 = info.get("fiftyTwoWeekLow", "N/A")
            st.metric(
                "52 Week Low",
                f"{low_52:,.2f}" if isinstance(low_52, (int, float)) else "N/A",
            )

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Key Financial Statistics with Safe Fallbacks & Dividend Yield Filter
        st.markdown("#### 📊 ค่าสถิติที่สำคัญ (Key Financial Statistics)")

        try:
            financials = stock_obj.financials
            balance_sheet = stock_obj.balance_sheet
        except Exception:
            financials, balance_sheet = pd.DataFrame(), pd.DataFrame()

        # 1. ROE (Return on Equity)
        roe = info.get("returnOnEquity")
        if (
            roe is None
            and not financials.empty
            and not balance_sheet.empty
            and "Net Income" in financials.index
            and "Stockholders Equity" in balance_sheet.index
        ):
            try:
                roe = (
                    financials.loc["Net Income"].iloc[0]
                    / balance_sheet.loc["Stockholders Equity"].iloc[0]
                )
            except Exception:
                roe = None

        # 2. ROA (Return on Assets)
        roa = info.get("returnOnAssets")
        if (
            roa is None
            and not financials.empty
            and not balance_sheet.empty
            and "Net Income" in financials.index
            and "Total Assets" in balance_sheet.index
        ):
            try:
                roa = (
                    financials.loc["Net Income"].iloc[0]
                    / balance_sheet.loc["Total Assets"].iloc[0]
                )
            except Exception:
                roa = None

        # 3. D/E Ratio
        de_ratio = info.get("debtToEquity")
        if (
            de_ratio is None
            and not balance_sheet.empty
            and "Total Debt" in balance_sheet.index
            and "Stockholders Equity" in balance_sheet.index
        ):
            try:
                de_ratio = (
                    balance_sheet.loc["Total Debt"].iloc[0]
                    / balance_sheet.loc["Stockholders Equity"].iloc[0]
                )
            except Exception:
                de_ratio = None

        # 4. EPS, PE, PB & Filtered Dividend Yield
        pe_ratio = info.get("trailingPE", info.get("forwardPE", "N/A"))
        pb_ratio = info.get("priceToBook", "N/A")
        eps = info.get(
            "trailingEps",
            info.get("forwardEps", info.get("epsTrailingTwelveMonths", "N/A")),
        )

        # Safe Dividend Yield Calculation with Cap / Filter
        raw_div = info.get("dividendYield")
        if raw_div is None:
            raw_div = info.get("trailingAnnualDividendYield", "N/A")

        if isinstance(raw_div, (int, float)):
            if raw_div < 1:
                calculated_div = raw_div * 100
            else:
                calculated_div = raw_div

            if calculated_div > 25:
                div_yield_str = "N/A (ข้อมูลดิบคาดเคลื่อน)"
            else:
                div_yield_str = f"{calculated_div:.2f}%"
        else:
            div_yield_str = "N/A"

        roe_str = (
            f"{roe * 100:.2f}%"
            if isinstance(roe, (int, float)) and abs(roe) < 2
            else (
                f"{roe:.2f}%"
                if isinstance(roe, (int, float))
                else "N/A (คำนวณซ้ำ)"
            )
        )
        roa_str = (
            f"{roa * 100:.2f}%"
            if isinstance(roa, (int, float)) and abs(roa) < 2
            else (
                f"{roa:.2f}%"
                if isinstance(roa, (int, float))
                else "N/A (คำนวณซ้ำ)"
            )
        )
        de_str = (
            f"{de_ratio / 100:.2f}"
            if isinstance(de_ratio, (int, float)) and de_ratio > 10
            else (
                f"{de_ratio:.2f}" if isinstance(de_ratio, (int, float)) else "N/A"
            )
        )

        s_col1, s_col2, s_col3, s_col4 = st.columns(4, gap="small")
        with s_col1:
            st.markdown(
                f"""<div class='metric-card'>🎯 <b style='color:#94a3b8;'>ROE</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #00f0ff;'>{roe_str}</span></div>""",
                unsafe_allow_html=True,
            )
        with s_col2:
            st.markdown(
                f"""<div class='metric-card'>🏢 <b style='color:#94a3b8;'>ROA</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #ffffff;'>{roa_str}</span></div>""",
                unsafe_allow_html=True,
            )
        with s_col3:
            st.markdown(
                f"""<div class='metric-card'>📈 <b style='color:#94a3b8;'>P/E Ratio</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #ffffff;'>{f'{pe_ratio:,.2f}' if isinstance(pe_ratio, (int, float)) else 'N/A'}</span></div>""",
                unsafe_allow_html=True,
            )
        with s_col4:
            st.markdown(
                f"""<div class='metric-card'>📘 <b style='color:#94a3b8;'>P/BV Ratio</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #ffffff;'>{f'{pb_ratio:,.2f}' if isinstance(pb_ratio, (int, float)) else 'N/A'}</span></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

        s_col5, s_col6, s_col7, s_col8 = st.columns(4, gap="small")
        with s_col5:
            st.markdown(
                f"""<div class='metric-card'>⚖️ <b style='color:#94a3b8;'>D/E Ratio</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #ffffff;'>{de_str}</span></div>""",
                unsafe_allow_html=True,
            )
        with s_col6:
            st.markdown(
                f"""<div class='metric-card'>💵 <b style='color:#94a3b8;'>EPS (กำไรต่อหุ้น)</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #ffffff;'>{f'{eps:,.2f}' if isinstance(eps, (int, float)) else 'N/A'}</span></div>""",
                unsafe_allow_html=True,
            )
        with s_col7:
            st.markdown(
                f"""<div class='metric-card'>💰 <b style='color:#94a3b8;'>Dividend Yield</b><br><span style='font-size: 1.2rem; font-weight: 700; color: #10b981;'>{div_yield_str}</span></div>""",
                unsafe_allow_html=True,
            )
        with s_col8:
            beta = info.get("beta", "N/A")
            st.markdown(
                f"""<div class='metric-card'>⚡ <b style='color:#94a3b8;'>Beta (ความผันผวน)</b><br><span style='font-size: 1.3rem; font-weight: 700; color: #f59e0b;'>{f'{beta:,.2f}' if isinstance(beta, (int, float)) else 'N/A'}</span></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        with st.expander("📖 คำอธิบาย", expanded=False):
            st.markdown("""
                * **ROE (Return on Equity)**: วัดความสามารถของบริษัทในการนำเงินลงทุนของผู้ถือหุ้นไปทำให้งอกเงย ควรมี **ROE > 15%**
                * **ROA (Return on Assets)**: วัดความสามารถในการทำกำไรจากสินทรัพย์ของบริษัท ควรมี **ROA > 5%**
                * **P/E (Price to Earnings)**: วัดจำนวนปีที่จะคืนทุน ยิ่งต่ำยิ่งดีเมื่อเทียบกับอุตสาหกรรม
                * **P/BV (Price to Book Value)**: วัดความถูกแพงเมื่อเทียบกับมูลค่าทางบัญชี
                * **D/E (Debt to Equity)**: อัตราส่วนหนี้สินต่อทุน ยิ่งต่ำยิ่งปลอดภัยจากภาระหนี้
                * **EPS (Earnings Per Share)**: กำไรสุทธิต่อหุ้น ยิ่งเติบโตต่อเนื่องยิ่งดี
                * **Dividend Yield**: อัตราส่วนเงินปันผลตอบแทนเปรียบเทียบกับราคาหุ้นปัจจุบัน
                """)

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Broker Consensus Section
        st.markdown("#### 🏛️ Broker Consensus & Target Price (มุมมองโบรกเกอร์)")

        target_mean = info.get("targetMeanPrice", "N/A")
        target_high = info.get("targetHighPrice", "N/A")
        target_low = info.get("targetLowPrice", "N/A")
        recommendation_key = str(
            info.get("recommendationKey", "N/A")
        ).upper()
        num_analysts = info.get("numberOfAnalystOpinions", "N/A")

        if isinstance(target_mean, (int, float)) and isinstance(
            current_price, (int, float)
        ):
            upside = ((target_mean - current_price) / current_price) * 100
            upside_str = f"{upside:+.2f}%"
        else:
            upside_str = "N/A"

        b_col1, b_col2, b_col3, b_col4 = st.columns(4, gap="small")
        with b_col1:
            st.markdown(
                f"""
                <div class='metric-card'>
                    🎯 <b style='color:#94a3b8;'>Target Price (Avg)</b><br>
                    <span style='font-size: 1.4rem; font-weight: 700; color: #00f0ff;'>{f'{target_mean:,.2f}' if isinstance(target_mean, (int,float)) else 'N/A'}</span><br>
                    <small style='color: #64748b;'>Upside Potential: <b style='color:#00f0ff;'>{upside_str}</b></small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b_col2:
            rec_color = (
                "#10b981"
                if "BUY" in recommendation_key
                else ("#ef4444" if "SELL" in recommendation_key else "#f59e0b")
            )
            st.markdown(
                f"""
                <div class='metric-card'>
                    📢 <b style='color:#94a3b8;'>Consensus Recommendation</b><br>
                    <span style='font-size: 1.3rem; font-weight: 700; color: {rec_color};'>{recommendation_key}</span><br>
                    <small style='color: #64748b;'>Coverage Analysts: <b style='color:#ffffff;'>{num_analysts} ราย</b></small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b_col3:
            st.markdown(
                f"""
                <div class='metric-card'>
                    🚀 <b style='color:#94a3b8;'>Highest Target Price</b><br>
                    <span style='font-size: 1.2rem; font-weight: 600; color: #10b981;'>{f'{target_high:,.2f}' if isinstance(target_high, (int,float)) else 'N/A'}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b_col4:
            st.markdown(
                f"""
                <div class='metric-card'>
                    🛡️ <b style='color:#94a3b8;'>Lowest Target Price</b><br>
                    <span style='font-size: 1.2rem; font-weight: 600; color: #ef4444;'>{f'{target_low:,.2f}' if isinstance(target_low, (int,float)) else 'N/A'}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Support & Resistance (5 Timeframes)
        sup_15m, res_15m = calculate_support_resistance(
            ticker_symbol, interval="15m", period="5d"
        )
        sup_1h, res_1h = calculate_support_resistance(
            ticker_symbol, interval="60m", period="14d"
        )
        sup_4h, res_4h = calculate_support_resistance(
            ticker_symbol, interval="240m", period="60d"
        )
        sup_d, res_d = calculate_support_resistance(
            ticker_symbol, interval="1d", period="6mo"
        )
        sup_w, res_w = calculate_support_resistance(
            ticker_symbol, interval="1wk", period="1y"
        )

        st.markdown("#### 🎯 Support & Resistance (5 Timeframes)")
        sr_col1, sr_col2, sr_col3, sr_col4, sr_col5 = st.columns(5, gap="small")
        with sr_col1:
            st.markdown(
                f"<div class='metric-card'><strong>⏱️ 15 Mins</strong><br><br>🟢 Support:"
                f" <b style='color:#10b981;'>{f'{sup_15m:,.2f}' if sup_15m else 'N/A'}</b><br>🔴"
                " Resistance:"
                f" <b style='color:#ef4444;'>{f'{res_15m:,.2f}' if res_15m else 'N/A'}</b></div>",
                unsafe_allow_html=True,
            )
        with sr_col2:
            st.markdown(
                f"<div class='metric-card'><strong>⏱️ 1 Hour</strong><br><br>🟢 Support:"
                f" <b style='color:#10b981;'>{f'{sup_1h:,.2f}' if sup_1h else 'N/A'}</b><br>🔴"
                " Resistance:"
                f" <b style='color:#ef4444;'>{f'{res_1h:,.2f}' if res_1h else 'N/A'}</b></div>",
                unsafe_allow_html=True,
            )
        with sr_col3:
            st.markdown(
                f"<div class='metric-card'><strong>⏱️ 4 Hours</strong><br><br>🟢 Support:"
                f" <b style='color:#10b981;'>{f'{sup_4h:,.2f}' if sup_4h else 'N/A'}</b><br>🔴"
                " Resistance:"
                f" <b style='color:#ef4444;'>{f'{res_4h:,.2f}' if res_4h else 'N/A'}</b></div>",
                unsafe_allow_html=True,
            )
        with sr_col4:
            st.markdown(
                f"<div class='metric-card'><strong>📅 Daily</strong><br><br>🟢 Support:"
                f" <b style='color:#10b981;'>{f'{sup_d:,.2f}' if sup_d else 'N/A'}</b><br>🔴"
                " Resistance:"
                f" <b style='color:#ef4444;'>{f'{res_d:,.2f}' if res_d else 'N/A'}</b></div>",
                unsafe_allow_html=True,
            )
        with sr_col5:
            st.markdown(
                f"<div class='metric-card'><strong>📆 Weekly</strong><br><br>🟢 Support:"
                f" <b style='color:#10b981;'>{f'{sup_w:,.2f}' if sup_w else 'N/A'}</b><br>🔴"
                " Resistance:"
                f" <b style='color:#ef4444;'>{f'{res_w:,.2f}' if res_w else 'N/A'}</b></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Fibonacci Section
        st.markdown("#### 🌀 Fibonacci Retracement Analysis")
        fib_choice = st.selectbox(
            "Select Timeframe for Fibonacci Calculation:",
            [
                "15 Mins (15m - 5d)",
                "1 Hour (1H - 14d)",
                "4 Hours (4H - 60d)",
                "Daily (Daily - 6mo)",
                "Weekly (Weekly - 1y)",
            ],
            index=3,
        )

        if "15 Mins" in fib_choice:
            active_fib = calculate_fibonacci_levels(
                ticker_symbol, interval="15m", period="5d"
            )
        elif "1 Hour" in fib_choice:
            active_fib = calculate_fibonacci_levels(
                ticker_symbol, interval="60m", period="14d"
            )
        elif "4 Hours" in fib_choice:
            active_fib = calculate_fibonacci_levels(
                ticker_symbol, interval="240m", period="60d"
            )
        elif "Weekly" in fib_choice:
            active_fib = calculate_fibonacci_levels(
                ticker_symbol, interval="1wk", period="1y"
            )
        else:
            active_fib = calculate_fibonacci_levels(
                ticker_symbol, interval="1d", period="6mo"
            )

        if active_fib:
            f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5, gap="small")
            items = list(active_fib.items())
            with f_col1:
                st.markdown(
                    f"<div class='metric-card'>🔸 <b>{items[0][0]}</b><br><code style='color:#00f0ff;'>{items[0][1]:,.2f}</code><br><br>🔸"
                    f" <b>{items[1][0]}</b><br><code style='color:#00f0ff;'>{items[1][1]:,.2f}</code></div>",
                    unsafe_allow_html=True,
                )
            with f_col2:
                st.markdown(
                    f"<div class='metric-card'>🔸 <b>{items[2][0]}</b><br><code style='color:#00f0ff;'>{items[2][1]:,.2f}</code><br><br>🔸"
                    f" <b>{items[3][0]}</b><br><code style='color:#00f0ff;'>{items[3][1]:,.2f}</code></div>",
                    unsafe_allow_html=True,
                )
            with f_col3:
                st.markdown(
                    "<div class='metric-card' style='border-color: #00f0ff;"
                    " background: rgba(0, 240, 255, 0.1);'>⭐"
                    f" <b>{items[4][0]}</b><br><b style='color:#00f0ff;'><code>{items[4][1]:,.2f}</code></b></div>",
                    unsafe_allow_html=True,
                )
            with f_col4:
                st.markdown(
                    f"<div class='metric-card'>🔸 <b>{items[5][0]}</b><br><code style='color:#00f0ff;'>{items[5][1]:,.2f}</code></div>",
                    unsafe_allow_html=True,
                )
            with f_col5:
                st.markdown(
                    f"<div class='metric-card'>🔸 <b>{items[6][0]}</b><br><code style='color:#00f0ff;'>{items[6][1]:,.2f}</code></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Technical Chart Section
        st.markdown(
            "#### 📉 Technical Chart (Price, EMA, Volume, RSI & MACD)"
        )
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3, gap="small")
        with ctrl_col1:
            chart_timeframe_interval = st.selectbox(
                "Candle Timeframe:",
                ["15 Mins (15m)", "1 Hour (1H)", "4 Hours (4H)", "Daily (1D)", "Weekly (1W)"],
                index=3,
            )
        with ctrl_col2:
            chart_history_period = st.selectbox(
                "Chart History Period:",
                ["5 Days", "1 Month", "3 Months", "6 Months", "1 Year", "3 Years", "5 Years"],
                index=4,
            )
        with ctrl_col3:
            sr_overlay_tf = st.selectbox(
                "S/R Overlay Timeframe:",
                ["Daily", "15 Mins", "1 Hour", "4 Hours", "Weekly"],
                index=0,
            )

        opt_col1, opt_col2 = st.columns([1, 2], gap="small")
        with opt_col1:
            show_fib_lines = st.checkbox("Show Fibonacci Lines on Chart", value=True)
        with opt_col2:
            selected_sub_indicator = st.selectbox(
                "Indicator (Subplot 3):", ["RSI (14)", "MACD (12, 26, 9)"], index=0
            )

        def get_chart_plot_data(ticker_str, tf_label, period_choice):
            interval_map = {
                "15 Mins (15m)": "15m",
                "1 Hour (1H)": "60m",
                "4 Hours (4H)": "240m",
                "Daily (1D)": "1d",
                "Weekly (1W)": "1wk",
            }
            yf_interval = interval_map.get(tf_label, "1d")

            period_map = {
                "5 Days": "5d",
                "1 Month": "1mo",
                "3 Months": "3mo",
                "6 Months": "6mo",
                "1 Year": "1y",
                "3 Years": "3y",
                "5 Years": "5y",
            }
            yf_period = period_map.get(period_choice, "1y")

            try:
                if yf_interval == "15m":
                    df = yf.download(
                        ticker_str,
                        period="5d",
                        interval="15m",
                        progress=False,
                        auto_adjust=True,
                    )
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                elif yf_interval == "240m":
                    df = yf.download(
                        ticker_str,
                        period="60d",
                        interval="60m",
                        progress=False,
                        auto_adjust=True,
                    )
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    if not df.empty:
                        df = (
                            df.resample("4h")
                            .agg({
                                "Open": "first",
                                "High": "max",
                                "Low": "min",
                                "Close": "last",
                                "Volume": "sum",
                            })
                            .dropna()
                        )
                else:
                    df = yf.download(
                        ticker_str,
                        period=yf_period,
                        interval=yf_interval,
                        progress=False,
                        auto_adjust=True,
                    )
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                if not df.empty:
                    df["EMA_35"] = df["Close"].ewm(span=35, adjust=False).mean()
                    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
                    df["EMA_89"] = df["Close"].ewm(span=89, adjust=False).mean()
                    df["EMA_200"] = df["Close"].ewm(span=200, adjust=False).mean()

                    delta = df["Close"].diff()
                    gain = delta.clip(lower=0)
                    loss = -1 * delta.clip(upper=0)
                    avg_gain = gain.ewm(
                        alpha=1 / 14, min_periods=14, adjust=False
                    ).mean()
                    avg_loss = loss.ewm(
                        alpha=1 / 14, min_periods=14, adjust=False
                    ).mean()
                    rs = avg_gain / avg_loss
                    df["RSI"] = 100 - (100 / (1 + rs))

                    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
                    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
                    df["MACD"] = ema12 - ema26
                    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
                    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

                    days_delta_map = {
                        "5 Days": timedelta(days=5),
                        "1 Month": timedelta(days=31),
                        "3 Months": timedelta(days=92),
                        "6 Months": timedelta(days=184),
                        "1 Year": timedelta(days=365),
                        "3 Years": timedelta(days=1095),
                        "5 Years": timedelta(days=1825),
                    }
                    if period_choice in days_delta_map and not df.empty and period_choice != "5 Days":
                        cutoff_time = df.index[-1] - days_delta_map[period_choice]
                        df = df[df.index >= cutoff_time]

                return df, tf_label, period_choice
            except Exception:
                return pd.DataFrame(), tf_label, period_choice

        plot_data, active_tf_label, chart_tf_label = get_chart_plot_data(
            ticker_symbol, chart_timeframe_interval, chart_history_period
        )

        if not plot_data.empty:
            ema_35_last = plot_data["EMA_35"].iloc[-1]
            ema_50_last = plot_data["EMA_50"].iloc[-1]
            ema_89_last = plot_data["EMA_89"].iloc[-1]
            ema_200_last = plot_data["EMA_200"].iloc[-1]

            plt.style.use("dark_background")
            fig, (ax1, ax2, ax3) = plt.subplots(
                3,
                1,
                figsize=(10, 8),
                sharex=True,
                gridspec_kw={"height_ratios": [3, 1, 1.2]},
                constrained_layout=True,
            )
            fig.patch.set_facecolor("#070b12")

            ax1.set_facecolor("#0b1329")
            ax1.plot(
                plot_data.index,
                plot_data["Close"],
                color="#00f0ff",
                linewidth=1.8,
                label="Close Price",
            )
            ax1.plot(
                plot_data.index,
                plot_data["EMA_35"],
                color="#f59e0b",
                linewidth=1.2,
                linestyle="--",
                label=f"EMA 35 ({ema_35_last:,.2f})",
            )
            ax1.plot(
                plot_data.index,
                plot_data["EMA_50"],
                color="#10b981",
                linewidth=1.2,
                linestyle="--",
                label=f"EMA 50 ({ema_50_last:,.2f})",
            )
            ax1.plot(
                plot_data.index,
                plot_data["EMA_89"],
                color="#a855f7",
                linewidth=1.2,
                linestyle="--",
                label=f"EMA 89 ({ema_89_last:,.2f})",
            )
            ax1.plot(
                plot_data.index,
                plot_data["EMA_200"],
                color="#ef4444",
                linewidth=1.8,
                label=f"EMA 200 ({ema_200_last:,.2f})",
            )

            if "15 Mins" in sr_overlay_tf:
                active_sup, active_res, sup_res_tf_label = sup_15m, res_15m, "15m"
            elif "1 Hour" in sr_overlay_tf:
                active_sup, active_res, sup_res_tf_label = sup_1h, res_1h, "1H"
            elif "4 Hours" in sr_overlay_tf:
                active_sup, active_res, sup_res_tf_label = sup_4h, res_4h, "4H"
            elif "Weekly" in sr_overlay_tf:
                active_sup, active_res, sup_res_tf_label = sup_w, res_w, "Weekly"
            else:
                active_sup, active_res, sup_res_tf_label = sup_d, res_d, "Daily"

            if active_sup:
                ax1.axhline(
                    y=active_sup,
                    color="#10b981",
                    linestyle="-.",
                    linewidth=2.0,
                    alpha=0.9,
                    label=f"{sup_res_tf_label} Support: {active_sup:,.2f}",
                )
            if active_res:
                ax1.axhline(
                    y=active_res,
                    color="#ef4444",
                    linestyle="-.",
                    linewidth=2.0,
                    alpha=0.9,
                    label=f"{sup_res_tf_label} Resistance: {active_res:,.2f}",
                )

            if show_fib_lines and active_fib:
                fib_colors = [
                    "#94a3b8",
                    "#38bdf8",
                    "#fbbf24",
                    "#c084fc",
                    "#f472b6",
                    "#60a5fa",
                    "#cbd5e1",
                ]
                for i, (k, v) in enumerate(active_fib.items()):
                    ax1.axhline(
                        y=v,
                        color=fib_colors[i % len(fib_colors)],
                        linestyle=":",
                        linewidth=1.2,
                        alpha=0.7,
                        label=f"{k}: {v:,.2f}",
                    )

            ax1.set_title(
                f"Technical Chart [{active_tf_label} | Period:"
                f" {chart_history_period}] - {display_ticker_label}",
                fontsize=11,
                fontweight="bold",
                color="#00f0ff",
            )
            ax1.grid(True, linestyle=":", alpha=0.2, color="#00f0ff")
            ax1.legend(
                loc="upper left",
                frameon=True,
                facecolor="#0f172a",
                edgecolor="#00f0ff",
                fontsize=6.5,
                labelcolor="#f1f5f9",
            )
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            ax1.spines["left"].set_color("#00f0ff4d")
            ax1.spines["bottom"].set_color("#00f0ff4d")
            ax1.tick_params(colors="#94a3b8")

            ax2.set_facecolor("#0b1329")
            price_diff = plot_data["Close"].diff()
            vol_colors = ["#10b981" if diff >= 0 else "#ef4444" for diff in price_diff]
            ax2.bar(
                plot_data.index,
                plot_data["Volume"],
                color=vol_colors,
                alpha=0.6,
                width=0.8,
            )
            ax2.set_ylabel("Volume", fontsize=8, color="#00f0ff", fontweight="bold")
            ax2.grid(True, linestyle=":", alpha=0.2, color="#00f0ff")
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            ax2.spines["left"].set_color("#00f0ff4d")
            ax2.spines["bottom"].set_color("#00f0ff4d")
            ax2.tick_params(colors="#94a3b8")

            ax3.set_facecolor("#0b1329")
            if "RSI" in selected_sub_indicator:
                rsi_last = (
                    plot_data["RSI"].iloc[-1] if "RSI" in plot_data.columns else 0
                )
                ax3.plot(
                    plot_data.index,
                    plot_data["RSI"],
                    color="#a855f7",
                    linewidth=1.5,
                    label=f"RSI 14 ({rsi_last:.1f})",
                )
                ax3.axhline(
                    70, color="#ef4444", linestyle="--", linewidth=1.0, alpha=0.7
                )
                ax3.axhline(
                    30, color="#10b981", linestyle="--", linewidth=1.0, alpha=0.7
                )
                ax3.fill_between(plot_data.index, 70, 30, color="#1e293b", alpha=0.4)
                ax3.set_ylim(0, 100)
                ax3.set_ylabel(
                    "RSI (14)", fontsize=8, color="#00f0ff", fontweight="bold"
                )
            else:
                macd_last = (
                    plot_data["MACD"].iloc[-1] if "MACD" in plot_data.columns else 0
                )
                signal_last = (
                    plot_data["MACD_Signal"].iloc[-1]
                    if "MACD_Signal" in plot_data.columns
                    else 0
                )
                ax3.plot(
                    plot_data.index,
                    plot_data["MACD"],
                    color="#38bdf8",
                    linewidth=1.4,
                    label=f"MACD ({macd_last:.2f})",
                )
                ax3.plot(
                    plot_data.index,
                    plot_data["MACD_Signal"],
                    color="#f59e0b",
                    linewidth=1.2,
                    linestyle="--",
                    label=f"Signal ({signal_last:.2f})",
                )

                hist_colors = [
                    "#10b981" if val >= 0 else "#ef4444"
                    for val in plot_data["MACD_Hist"]
                ]
                ax3.bar(
                    plot_data.index,
                    plot_data["MACD_Hist"],
                    color=hist_colors,
                    alpha=0.5,
                    width=0.8,
                    label="Histogram",
                )
                ax3.axhline(0, color="#64748b", linestyle="-", linewidth=0.8, alpha=0.7)
                ax3.set_ylabel("MACD", fontsize=8, color="#00f0ff", fontweight="bold")

            ax3.grid(True, linestyle=":", alpha=0.2, color="#00f0ff")
            ax3.legend(
                loc="upper left",
                frameon=True,
                facecolor="#0f172a",
                edgecolor="#00f0ff",
                fontsize=6.5,
                labelcolor="#f1f5f9",
            )
            ax3.spines["top"].set_visible(False)
            ax3.spines["right"].set_visible(False)
            ax3.spines["left"].set_color("#00f0ff4d")
            ax3.spines["bottom"].set_color("#00f0ff4d")
            ax3.tick_params(colors="#94a3b8")

            st.pyplot(fig)
        else:
            st.warning("ไม่พบข้อมูลกราฟในช่วงเวลาหรือไทม์เฟรมนี้")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Settrade Direct Links
        st.markdown("#### 📰 ลิงก์ตรง Settrade")
        settrade_quote_url = f"https://www.settrade.com/th/equities/quote/{display_ticker_label}/overview"
        settrade_news_url = f"https://www.settrade.com/th/equities/quote/{display_ticker_label}/news"

        link_col1, link_col2 = st.columns(2, gap="small")
        with link_col1:
            st.link_button(
                f"🔗 ดูภาพรวม {display_ticker_label} บน Settrade",
                settrade_quote_url,
                use_container_width=True,
            )
        with link_col2:
            st.link_button(
                f"📰 ดูข่าวทั้งหมดของ {display_ticker_label} (Settrade)",
                settrade_news_url,
                use_container_width=True,
            )

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Personal Strategy & Portfolio Notes
        st.markdown("#### ✍️ Personal Strategy & Portfolio Notes")
        st.markdown(
            "<span style='color: #94a3b8; font-size: 0.9rem;'>บันทึกแผน DCA"
            " หรือความเห็นส่วนตัวเปรียบเทียบกับ Broker Target:</span>",
            unsafe_allow_html=True,
        )

        if "analysis_notes" not in st.session_state:
            st.session_state.analysis_notes = {}

        current_note = st.session_state.analysis_notes.get(
            display_ticker_label,
            f"Notes for {display_ticker_label}:\n- DCA / Dividend Yield Target:\n- Entry/Exit Action Plan:",
        )

        user_analysis = st.text_area(
            "Personal Note Editor",
            current_note,
            height=200,
            label_visibility="collapsed",
        )

        if st.button("💾 Save Strategy Notes", use_container_width=True):
            st.session_state.analysis_notes[display_ticker_label] = user_analysis
            st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

except Exception as e:
    st.error(
        f"⚠️ เกิดข้อผิดพลาดในการโหลดข้อมูลหลักทรัพย์ `{raw_clean}`"
        " หรือระบบอินเทอร์เน็ตขัดข้อง"
    )
    st.exception(e)
