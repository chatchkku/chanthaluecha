import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

# --- ตั้งค่าหน้าเว็บให้เป็นแบบ Wide Mode และรองรับ Mobile Responsive ---
st.set_page_config(
    page_title="Chanthaluecha Intelligence Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS รองรับทุกหน้าจอ (ซ่อน Sidebar ถาวร) ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="st"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #0f172a !important;
        }

        .main {
            background-color: #f8fafc;
            color: #0f172a;
        }

        /* ซ่อน Sidebar และปุ่มเปิด-ปิด */
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }

        /* Hero Header สำหรับทุกขนาดหน้าจอ */
        .main-header {
            background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
            padding: 20px 25px;
            border-radius: 16px;
            color: #1e1b4b;
            margin-bottom: 20px;
            border: 1px solid rgba(79, 70, 229, 0.2);
            box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.15);
        }
        .main-header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 6px;
            color: #1e1b4b !important;
            letter-spacing: -0.5px;
        }
        .main-header p {
            color: #312e81 !important;
            font-size: 0.95rem;
            margin: 0;
        }

        @media (min-width: 768px) {
            .main-header {
                padding: 30px 35px;
            }
            .main-header h1 {
                font-size: 2.4rem;
            }
            .main-header p {
                font-size: 1.05rem;
            }
        }

        /* Buttons Touch-Friendly สำหรับมือถือ */
        .stButton button {
            border-radius: 10px;
            font-weight: 600;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            border: none;
            padding: 0.6rem 1rem;
            min-height: 42px;
            transition: all 0.2s ease-in-out;
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            transform: translateY(-1px);
        }

        /* Text Inputs & Selectboxes */
        .stTextInput input {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border-radius: 10px !important;
            border: 1px solid rgba(30, 58, 138, 0.2) !important;
            min-height: 42px;
        }
        
        h4, h3, h2, h1 {
            color: #1e3a8a !important;
            font-weight: 700 !important;
            letter-spacing: -0.3px;
        }

        p, span, label, div {
            color: #1e293b;
        }

        .metric-card-mobile {
            background: #ffffff;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- จัดการสถานะ Active Ticker ---
if "active_ticker" not in st.session_state:
  st.session_state.active_ticker = "BDMS"

# --- ส่วนหัวของแอปพลิเคชัน ---
st.markdown(
    """
    <div class="main-header">
        <h1>📈 Chanthaluecha Intelligence Dashboard</h1>
        <p>ระบบวิเคราะห์ข้อมูลหลักทรัพย์ ทางเทคนิคเชิงลึก EMA, แนวรับ-แนวต้าน, Fibonacci และระบบบันทึกกลยุทธ์ส่วนบุคคล</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- แผงค้นหาหุ้นอิสระ ---
search_col1, search_col2, search_col3 = st.columns([3, 1, 1], gap="small")

with search_col1:
  user_typed_ticker = st.text_input(
      "🔍 พิมพ์รหัสหุ้นที่ต้องการค้นหา (เช่น BDMS, PTT, IVV, VT, AAPL):",
      value=st.session_state.active_ticker.replace(".BK", ""),
      placeholder="พิมพ์รหัสหุ้นแล้วกด Enter...",
      key="free_stock_input",
  )

with search_col2:
  st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
  if st.button("🔍 ค้นหาข้อมูล", use_container_width=True):
    if user_typed_ticker.strip():
      st.session_state.active_ticker = user_typed_ticker.strip().upper()
      st.rerun()

with search_col3:
  st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
  if st.button("🔄 รีเซ็ตค่า", use_container_width=True):
    st.session_state.active_ticker = "BDMS"
    st.rerun()

if user_typed_ticker.strip():
  cleaned_input = user_typed_ticker.strip().upper()
  if cleaned_input != st.session_state.active_ticker.replace(".BK", ""):
    st.session_state.active_ticker = cleaned_input

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
]
if "." in raw_clean or raw_clean in us_market_indicators or len(raw_clean) > 5:
  ticker_symbol = raw_clean
else:
  ticker_symbol = raw_clean


# --- ฟังก์ชันดึงข้อมูลหุ้น ---
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


# ฟังก์ชันคำนวณแนวรับ-แนวต้าน
def calculate_support_resistance(ticker, interval, period):
  try:
    if interval == "240m":
      df = yf.download(
          ticker, period="60d", interval="60m", progress=False, auto_adjust=True
      )
      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
      if df.empty or len(df) < 5:
        return None, None
      df = (
          df.resample("4h")
          .agg(
              {
                  "Open": "first",
                  "High": "max",
                  "Low": "min",
                  "Close": "last",
                  "Volume": "sum",
              }
          )
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


# ฟังก์ชันคำนวณ Fibonacci Retracement Levels
def calculate_fibonacci_levels(ticker, interval, period):
  try:
    if interval == "240m":
      df = yf.download(
          ticker, period="60d", interval="60m", progress=False, auto_adjust=True
      )
      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
      if df.empty or len(df) < 5:
        return None
      df = (
          df.resample("4h")
          .agg(
              {
                  "Open": "first",
                  "High": "max",
                  "Low": "min",
                  "Close": "last",
                  "Volume": "sum",
              }
          )
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


# --- ส่วนประมวลผลหลัก ---
try:
  with st.spinner(f"กำลังโหลดข้อมูล {ticker_symbol.upper()}..."):
    hist, info, news, ticker_symbol = load_stock_data(ticker_symbol)
    stock = yf.Ticker(ticker_symbol)

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
        f"### 📊 ภาพรวมหลักทรัพย์: **{company_name}** (`{display_ticker_label}`)"
    )

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="small")
    with col1:
      st.metric(
          "ราคาปัจจุบัน",
          f"{current_price:,.2f}"
          if isinstance(current_price, (int, float))
          else "N/A",
          f"{price_change:+.2f} ({percent_change:+.2f}%)",
      )
    with col2:
      market_cap = info.get("marketCap", "N/A")
      formatted_cap = (
          f"{market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"
      )
      st.metric("มูลค่าตลาด (Market Cap)", formatted_cap)
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

    # --- คำนวณแนวรับ-แนวต้านครบ 4 กรอบเวลา ---
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

    st.markdown(
        "#### 🎯 วิเคราะห์แนวรับ - แนวต้าน (Support & Resistance - 4 Timeframes)"
    )
    sr_col1, sr_col2, sr_col3, sr_col4 = st.columns(4, gap="small")

    with sr_col1:
      sup_text = f"{sup_1h:,.2f}" if sup_1h else "N/A"
      res_text = f"{res_1h:,.2f}" if res_1h else "N/A"
      st.markdown(
          f"""
            <div class='metric-card-mobile'>
                <strong>⏱️ 1 ชั่วโมง (1H)</strong><br>
                🟢 รับ: <b>{sup_text}</b><br>
                🔴 ต้าน: <b>{res_text}</b>
            </div>
        """,
          unsafe_allow_html=True,
      )

    with sr_col2:
      sup_text = f"{sup_4h:,.2f}" if sup_4h else "N/A"
      res_text = f"{res_4h:,.2f}" if res_4h else "N/A"
      st.markdown(
          f"""
            <div class='metric-card-mobile'>
                <strong>⏱️ 4 ชั่วโมง (4H)</strong><br>
                🟢 รับ: <b>{sup_text}</b><br>
                🔴 ต้าน: <b>{res_text}</b>
            </div>
        """,
          unsafe_allow_html=True,
      )

    with sr_col3:
      sup_text = f"{sup_d:,.2f}" if sup_d else "N/A"
      res_text = f"{res_d:,.2f}" if res_d else "N/A"
      st.markdown(
          f"""
            <div class='metric-card-mobile'>
                <strong>📅 รายวัน (Daily)</strong><br>
                🟢 รับ: <b>{sup_text}</b><br>
                🔴 ต้าน: <b>{res_text}</b>
            </div>
        """,
          unsafe_allow_html=True,
      )

    with sr_col4:
      sup_text = f"{sup_w:,.2f}" if sup_w else "N/A"
      res_text = f"{res_w:,.2f}" if res_w else "N/A"
      st.markdown(
          f"""
            <div class='metric-card-mobile'>
                <strong>📆 รายสัปดาห์ (Weekly)</strong><br>
                🟢 รับ: <b>{sup_text}</b><br>
                🔴 ต้าน: <b>{res_text}</b>
            </div>
        """,
          unsafe_allow_html=True,
      )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # --- ส่วน Fibonacci ---
    st.markdown("#### 🌀 วิเคราะห์ระดับ Fibonacci Retracement")
    fib_choice = st.selectbox(
        "เลือกกรอบเวลาเพื่อคำนวณ Fibonacci:",
        [
            "รายวัน (Daily - 6mo)",
            "ราย 1 ชั่วโมง (1H - 14d)",
            "ราย 4 ชั่วโมง (4H - 60d)",
            "รายสัปดาห์ (Weekly - 1y)",
        ],
        index=0,
    )

    if "1 ชั่วโมง" in fib_choice:
      active_fib = calculate_fibonacci_levels(
          ticker_symbol, interval="60m", period="14d"
      )
    elif "4 ชั่วโมง" in fib_choice:
      active_fib = calculate_fibonacci_levels(
          ticker_symbol, interval="240m", period="60d"
      )
    elif "รายสัปดาห์" in fib_choice:
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
            f"<div class='metric-card-mobile'>🔸 <b>{items[0][0]}</b><br>`{items[0][1]:,.2f}`<br><br>🔸 <b>{items[1][0]}</b><br>`{items[1][1]:,.2f}`</div>",
            unsafe_allow_html=True,
        )
      with f_col2:
        st.markdown(
            f"<div class='metric-card-mobile'>🔸 <b>{items[2][0]}</b><br>`{items[2][1]:,.2f}`<br><br>🔸 <b>{items[3][0]}</b><br>`{items[3][1]:,.2f}`</div>",
            unsafe_allow_html=True,
        )
      with f_col3:
        st.markdown(
            f"<div class='metric-card-mobile' style='border-color: #3b82f6;'>⭐ <b>{items[4][0]}</b><br><b>`{items[4][1]:,.2f}`</b></div>",
            unsafe_allow_html=True,
        )
      with f_col4:
        st.markdown(
            f"<div class='metric-card-mobile'>🔸 <b>{items[5][0]}</b><br>`{items[5][1]:,.2f}`</div>",
            unsafe_allow_html=True,
        )
      with f_col5:
        st.markdown(
            f"<div class='metric-card-mobile'>🔸 <b>{items[6][0]}</b><br>`{items[6][1]:,.2f}`</div>",
            unsafe_allow_html=True,
        )
    else:
      st.info("ไม่สามารถคำนวณ Fibonacci ได้ในขณะนี้")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # --- กราฟทางเทคนิค ---
    st.markdown(
        "#### 📉 กราฟวิเคราะห์ทางเทคนิค (Price, EMA, S/R & Fibonacci Overlay)"
    )
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(
        4, gap="small"
    )

    with ctrl_col1:
      chart_timeframe_interval = st.selectbox(
          "ไทม์เฟรมแท่งเทียน:",
          [
              "ราย 1 ชั่วโมง (1H)",
              "ราย 4 ชั่วโมง (4H)",
              "รายวัน (1D)",
              "รายสัปดาห์ (1W)",
          ],
          index=2,
          key="chart_tf_interval_selectbox",
      )

    with ctrl_col2:
      chart_history_period = st.selectbox(
          "ช่วงเวลากราฟย้อนหลัง:",
          ["1 เดือน", "3 เดือน", "6 เดือน", "1 ปี", "3 ปี", "5 ปี"],
          index=3,
          key="chart_history_period_selectbox",
      )

    with ctrl_col3:
      sr_overlay_tf = st.selectbox(
          "แสดงเส้นแนวรับ/ต้าน:",
          [
              "รายวัน (Daily)",
              "ราย 1 ชั่วโมง (1H)",
              "ราย 4 ชั่วโมง (4H)",
              "รายสัปดาห์ (Weekly)",
          ],
          index=0,
          key="sr_overlay_selectbox",
      )

    with ctrl_col4:
      st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
      show_fib_lines = st.checkbox(
          "เปิดแสดงเส้น Fibonacci บนกราฟ", value=False
      )


    # ฟังก์ชันดึงข้อมูลกราฟและคำนวณ EMA ตามจำนวนแท่งเทียนของไทม์เฟรมนั้นๆ
    def get_chart_plot_data(ticker_str, tf_label, period_choice):
      interval_map = {
          "ราย 1 ชั่วโมง (1H)": "60m",
          "ราย 4 ชั่วโมง (4H)": "240m",
          "รายวัน (1D)": "1d",
          "รายสัปดาห์ (1W)": "1wk",
      }
      yf_interval = interval_map.get(tf_label, "1d")

      period_map = {
          "1 เดือน": "1mo",
          "3 เดือน": "3mo",
          "6 เดือน": "6mo",
          "1 ปี": "1y",
          "3 ปี": "3y",
          "5 ปี": "5y",
      }
      yf_period = period_map.get(period_choice, "1y")

      if yf_interval == "60m":
        yf_period = "max" if yf_period in ["1mo"] else yf_period
      elif yf_interval == "240m":
        yf_period = (
            "max" if yf_period in ["1mo", "3mo", "6mo"] else yf_period
        )

      try:
        if yf_interval == "240m":
          df = yf.download(
              ticker_str,
              period="max",
              interval="60m",
              progress=False,
              auto_adjust=True,
          )
          if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
          if not df.empty:
            df = (
                df.resample("4h")
                .agg(
                    {
                        "Open": "first",
                        "High": "max",
                        "Low": "min",
                        "Close": "last",
                        "Volume": "sum",
                    }
                )
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

          days_delta_map = {
              "1 เดือน": timedelta(days=31),
              "3 เดือน": timedelta(days=92),
              "6 เดือน": timedelta(days=184),
              "1 ปี": timedelta(days=365),
              "3 ปี": timedelta(days=1095),
              "5 ปี": timedelta(days=1825),
          }
          if period_choice in days_delta_map and not df.empty:
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

      plt.style.use("default")
      fig, ax = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
      fig.patch.set_facecolor("#ffffff")
      ax.set_facecolor("#f8fafc")

      ax.plot(
          plot_data.index,
          plot_data["Close"],
          color="#0284c7",
          linewidth=1.8,
          label=f"Close Price",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_35"],
          color="#d97706",
          linewidth=1.2,
          linestyle="--",
          label=f"EMA 35 ({ema_35_last:,.2f})",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_50"],
          color="#059669",
          linewidth=1.2,
          linestyle="--",
          label=f"EMA 50 ({ema_50_last:,.2f})",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_89"],
          color="#7c3aed",
          linewidth=1.2,
          linestyle="--",
          label=f"EMA 89 ({ema_89_last:,.2f})",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_200"],
          color="#dc2626",
          linewidth=1.8,
          label=f"EMA 200 ({ema_200_last:,.2f})",
      )

      if "1 ชั่วโมง" in sr_overlay_tf:
        active_sup, active_res, tf_label = sup_1h, res_1h, "1H"
      elif "4 ชั่วโมง" in sr_overlay_tf:
        active_sup, active_res, tf_label = sup_4h, res_4h, "4H"
      elif "รายสัปดาห์" in sr_overlay_tf:
        active_sup, active_res, tf_label = sup_w, res_w, "Weekly"
      else:
        active_sup, active_res, tf_label = sup_d, res_d, "Daily"

      if active_sup:
        ax.axhline(
            y=active_sup,
            color="#059669",
            linestyle="-.",
            linewidth=2.0,
            alpha=0.9,
            label=f"{tf_label} Support: {active_sup:,.2f}",
        )
      if active_res:
        ax.axhline(
            y=active_res,
            color="#dc2626",
            linestyle="-.",
            linewidth=2.0,
            alpha=0.9,
            label=f"{tf_label} Resistance: {active_res:,.2f}",
        )

      if show_fib_lines and active_fib:
        fib_colors = [
            "#475569",
            "#0284c7",
            "#d97706",
            "#7c3aed",
            "#db2777",
            "#2563eb",
            "#64748b",
        ]
        for i, (k, v) in enumerate(active_fib.items()):
          ax.axhline(
              y=v,
              color=fib_colors[i % len(fib_colors)],
              linestyle=":",
              linewidth=1.2,
              alpha=0.7,
              label=f"{k}: {v:,.2f}",
          )

      ax.set_title(
          f"Technical Chart [{active_tf_label} | ย้อนหลัง {chart_tf_label}] -"
          f" {display_ticker_label}",
          fontsize=11,
          fontweight="bold",
          color="#1e3a8a",
      )
      ax.grid(True, linestyle=":", alpha=0.3, color="#cbd5e1")
      ax.legend(
          loc="upper left",
          frameon=True,
          facecolor="#ffffff",
          edgecolor="#cbd5e1",
          fontsize=7,
          labelcolor="#0f172a",
      )

      ax.spines["top"].set_visible(False)
      ax.spines["right"].set_visible(False)
      ax.spines["left"].set_color("#cbd5e1")
      ax.spines["bottom"].set_color("#cbd5e1")
      ax.tick_params(colors="#0f172a")

      st.pyplot(fig)
    else:
      st.warning("ไม่พบข้อมูลกราฟในช่วงเวลาหรือไทม์เฟรมนี้")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # --- ข่าวสาร และ บทวิเคราะห์ ---
    col_news, col_analysis = st.columns(2, gap="medium")

    with col_news:
      st.markdown("#### 📰 ข่าวสารและประกาศสำคัญจากเว็บยอดนิยม")
      is_thai_stock = ticker_symbol.endswith(".BK")
      clean_symbol = display_ticker_label.upper()

      if is_thai_stock:
        settrade_url = (
            f"https://www.settrade.com/th/equities/quote/{clean_symbol}/news"
        )
        set_url = f"https://www.set.or.th/th/market/product/stock/quote/{clean_symbol}/news"
        thunhoon_url = f"https://thunhoon.com/search?keyword={clean_symbol}"
        trader_url = f"https://www.efinancethai.com/LastestNews/LatestNewsMain.aspx?ref=symbol&id={clean_symbol}"

        st.markdown(
            "🇹🇭 **ศูนย์รวมข่าวสารหลักทรัพย์ไทย (คลิกเปิดเว็บไซต์):**"
        )
        st.markdown(
            f"👉 **[1. ข่าวทันหุ้น (Thunhoon): ค้นหาข่าว {clean_symbol}]({thunhoon_url})**"
        )
        st.markdown(
            f"👉 **[2. ข่าวตลาดหลักทรัพย์และงบการเงิน (SET.or.th)]({set_url})**"
        )
        st.markdown(
            f"👉 **[3. หน้าข่าวและการซื้อขายเรียลไทม์ (Settrade)]({settrade_url})**"
        )
        st.markdown(
            f"👉 **[4. บทวิเคราะห์เจาะลึกหุ้น {clean_symbol} (eFinanceThai)]({trader_url})**"
        )
        st.markdown("---")
      else:
        yahoo_news_url = (
            f"https://finance.yahoo.com/quote/{clean_symbol}/news/"
        )
        seeking_alpha_url = f"https://seekingalpha.com/symbol/{clean_symbol}"
        st.markdown(
            "🇺🇸 **ศูนย์รวมข่าวสารหลักทรัพย์/ETF สากล (คลิกเปิดเว็บไซต์):**"
        )
        st.markdown(
            f"👉 **[1. ข่าวสารล่าสุดจาก Yahoo Finance ({clean_symbol})]"
            f"({yahoo_news_url})**"
        )
        st.markdown(
            f"👉 **[2. บทวิเคราะห์มุมมองนักลงทุน (Seeking Alpha)]({seeking_alpha_url})**"
        )
        st.markdown("---")

      if news:
        cutoff_date = datetime.now() - timedelta(days=90)
        filtered_news = []
        for item in news:
          pub_time = item.get("providerPublishTime")
          if pub_time:
            news_date = datetime.fromtimestamp(pub_time)
            if news_date >= cutoff_date:
              filtered_news.append((news_date, item))
          else:
            filtered_news.append((datetime.now(), item))

        if not filtered_news and news:
          for item in news:
            filtered_news.append((datetime.now(), item))

        if filtered_news:
          filtered_news.sort(key=lambda x: x[0], reverse=True)
          st.markdown(
              "<span style='font-size: 0.85rem; color: #64748b;'>หัวข้อข่าวอัปเดตล่าสุด:</span>",
              unsafe_allow_html=True,
          )
          for news_date, item in filtered_news[:3]:
            title = item.get("title", "No Title")
            publisher = item.get("publisher", "Unknown Source")
            link = item.get("link", "#")

            st.markdown(f"🔹 **[{title}]({link})**")
            st.caption(f"สำนักข่าว: {publisher}")
            st.markdown("---")

    with col_analysis:
      st.markdown("#### ✍️ บันทึกบทวิเคราะห์และแผนการลงทุน")
      st.markdown(
          "<span style='color: #334155; font-size: 0.9rem;'>จดบันทึกมุมมองพื้นฐาน"
          " สัญญาณเทคนิค หรือแผน DCA ส่วนตัวของคุณ:</span>",
          unsafe_allow_html=True,
      )

      if "analysis_notes" not in st.session_state:
        st.session_state.analysis_notes = {}

      current_note = st.session_state.analysis_notes.get(
          display_ticker_label,
          f"บทวิเคราะห์สำหรับ {display_ticker_label}:\n- มุมมองพื้นฐาน/ปันผล:\n- สัญญาณทางเทคนิค (EMA 35/50/89/200):\n- แผนการลงทุน/DCA:",
      )

      user_analysis = st.text_area(
          "พื้นที่เขียนบทวิเคราะห์",
          current_note,
          height=230,
          label_visibility="collapsed",
      )

      if st.button("💾 บันทึกบทวิเคราะห์นี้", use_container_width=True):
        st.session_state.analysis_notes[display_ticker_label] = user_analysis
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

except Exception as e:
  st.error(
      f"⚠️ เกิดข้อผิดพลาดในการโหลดข้อมูลหลักทรัพย์ `{raw_clean}`"
      " หรือระบบอินเทอร์เน็ตขัดข้อง"
  )
  st.exception(e)
