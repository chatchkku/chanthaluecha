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
    initial_sidebar_state="expanded",
)

# --- Custom CSS รองรับทุกหน้าจอ (Mobile, Tablet, Desktop) ---
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

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #f1f5f9;
            border-right: 1px solid rgba(0, 0, 0, 0.08);
        }
        [data-testid="stSidebar"] .stMarkdown {
            color: #0f172a !important;
        }
        [data-testid="stSidebar"] label {
            color: #1e3a8a !important;
            font-weight: 600;
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
        .stTextInput input, .stSelectbox select {
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

# --- จัดการระบบหุ้นโปรด (Favorites) ---
if "favorites" not in st.session_state:
  st.session_state.favorites = [
      "BDMS",
      "TCAP",
      "TTB",
      "GULF",
      "CBG",
      "AOT",
      "WHA",
  ]

# ตัวแปรเก็บค่ารหัสหุ้นที่ถูกเลือก
if "active_ticker" not in st.session_state:
  st.session_state.active_ticker = "BDMS"

# --- ส่วนหัวของแอปพลิเคชัน (Hero Header พร้อมช่องค้นหาด่วนด้านบน) ---
st.markdown(
    """
    <div class="main-header">
        <h1>📈 Chanthaluecha Intelligence Dashboard</h1>
        <p>ระบบวิเคราะห์ข้อมูลหลักทรัพย์ ทางเทคนิคเชิงลึก EMA, แนวรับ-แนวต้าน, Fibonacci และระบบบันทึกกลยุทธ์ส่วนบุคคล</p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- แผงค้นหาหุ้นด่วนด้านบนสุด (Search Bar ด้านบน) ---
search_col1, search_col2, search_col3 = st.columns([3, 1, 1], gap="small")
with search_col1:
  quick_search = st.text_input(
      "🔍 ค้นหารหัสหุ้นด่วน (พิมพ์ชื่อหุ้นได้ทันที ไม่ต้องใส่ .BK):",
      value="",
      placeholder="เช่น PTT, PTTEP, AAPL, IVV",
  )
with search_col2:
  st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
  search_btn = st.button("🔎 ค้นหา", use_container_width=True)
with search_col3:
  st.markdown("<div style='height: 27px;'></div>", unsafe_allow_html=True)
  clear_btn = st.button("🔄 รีเซ็ต", use_container_width=True)

if clear_btn:
  st.session_state.active_ticker = "BDMS"
  st.rerun()

if search_btn and quick_search.strip() != "":
  st.session_state.active_ticker = quick_search.strip().upper()

# --- ส่วนที่ 1: แถบด้านข้าง (Sidebar) ---
with st.sidebar:
  st.markdown("### ⚙️ ควบคุมพอร์ตและหุ้นโปรด")
  st.markdown("---")

  st.markdown("⭐ **รายชื่อหุ้นโปรดของคุณ**")
  if st.session_state.favorites:
    selected_fav = st.selectbox(
        "เลือกหุ้นจากรายการโปรด:",
        st.session_state.favorites,
        key="fav_selectbox",
    )
    # ถ้ามีการเลือกจาก selectbox ให้สลับมาเป็นตัวนี้
    if selected_fav:
      st.session_state.active_ticker = selected_fav
  else:
    st.info("ยังไม่มีหุ้นในรายการโปรด")

  st.markdown("---")
  col_f1, col_f2 = st.columns(2)
  with col_f1:
    if st.button("⭐ เพิ่มหุ้นนี้", use_container_width=True):
      clean_fav = (
          st.session_state.active_ticker.upper()
          .replace(".BK", "")
          .strip()
      )
      if clean_fav not in st.session_state.favorites:
        st.session_state.favorites.append(clean_fav)
        st.success(f"เพิ่ม {clean_fav} แล้ว!")
        st.rerun()
  with col_f2:
    if st.button("🗑️ ลบหุ้นนี้", use_container_width=True):
      clean_fav = (
          st.session_state.active_ticker.upper()
          .replace(".BK", "")
          .strip()
      )
      if clean_fav in st.session_state.favorites:
        st.session_state.favorites.remove(clean_fav)
        st.warning(f"ลบ {clean_fav} แล้ว!")
        st.rerun()

  st.markdown("---")
  st.caption("💡 *ระบบประมวลผลข้อมูล Real-time ผ่าน Yahoo Finance*")

# --- แปลงรหัสหุ้นให้อยู่ในรูปแบบที่ถูกต้อง (Smart Ticker) ---
raw_clean = st.session_state.active_ticker.strip().upper()
if "." in raw_clean:
  ticker_symbol = raw_clean
else:
  # หากพิมพ์สั้นๆ ให้เติม .BK สำหรับหุ้นไทย
  ticker_symbol = raw_clean + ".BK"


# --- ฟังก์ชันดึงข้อมูลหุ้น (พร้อมระบบสำรองกรณีหุ้นต่างประเทศ) ---
@st.cache_data(ttl=600)
def load_stock_data(ticker):
  stock_obj = yf.Ticker(ticker)
  hist = stock_obj.history(period="1y")

  if hist.empty and ticker.endswith(".BK"):
    fallback_ticker = ticker.replace(".BK", "")
    stock_obj = yf.Ticker(fallback_ticker)
    hist = stock_obj.history(period="1y")
    if not hist.empty:
      return hist, stock_obj.info, stock_obj.news, fallback_ticker

  return hist, stock_obj.info, stock_obj.news, ticker


# ฟังก์ชันคำนวณแนวรับ-แนวต้าน
def calculate_support_resistance(ticker, interval, period):
  try:
    df = yf.download(
        ticker, period=period, interval=interval, progress=False, auto_adjust=True
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
    df = yf.download(
        ticker, period=period, interval=interval, progress=False, auto_adjust=True
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

    display_ticker_label = ticker_symbol.replace(".BK", "")
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
      st.markdown(
          """<div class='metric-card-mobile'>""", unsafe_allow_html=True
      )
      st.markdown("**⏱️ 1 ชั่วโมง (1H)**")
      st.markdown(f"🟢 รับ: **{f'{sup_1h:,.2f}' if sup_1h else 'N/A'}**")
      st.markdown(f"🔴 ต้าน: **{f'{res_1h:,.2f}' if res_1h else 'N/A'}**")
      st.markdown("</div>", unsafe_allow_html=True)

    with sr_col2:
      st.markdown(
          """<div class='metric-card-mobile'>""", unsafe_allow_html=True
      )
      st.markdown("**⏱️ 4 ชั่วโมง (4H)**")
      st.markdown(f"🟢 รับ: **{f'{sup_4h:,.2f}' if sup_4h else 'N/A'}**")
      st.markdown(f"🔴 ต้าน: **{f'{res_4h:,.2f}' if res_4h else 'N/A'}**")
      st.markdown("</div>", unsafe_allow_html=True)

    with sr_col3:
      st.markdown(
          """<div class='metric-card-mobile'>""", unsafe_allow_html=True
      )
      st.markdown("**📅 รายวัน (Daily)**")
      st.markdown(f"🟢 รับ: **{f'{sup_d:,.2f}' if sup_d else 'N/A'}**")
      st.markdown(f"🔴 ต้าน: **{f'{res_d:,.2f}' if res_d else 'N/A'}**")
      st.markdown("</div>", unsafe_allow_html=True)

    with sr_col4:
      st.markdown(
          """<div class='metric-card-mobile'>""", unsafe_allow_html=True
      )
      st.markdown("**📆 รายสัปดาห์ (Weekly)**")
      st.markdown(f"🟢 รับ: **{f'{sup_w:,.2f}' if sup_w else 'N/A'}**")
      st.markdown(f"🔴 ต้าน: **{f'{res_w:,.2f}' if res_w else 'N/A'}**")
      st.markdown("</div>", unsafe_allow_html=True)

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
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 1], gap="small")
    with ctrl_col1:
      chart_period = st.radio(
          "ช่วงเวลากราฟ:",
          ["1 เดือน", "3 เดือน", "6 เดือน", "1 ปี"],
          index=1,
          horizontal=True,
      )
    with ctrl_col2:
      sr_overlay_tf = st.selectbox(
          "แสดงเส้นแนวรับ/ต้าน:",
          [
              "รายวัน (Daily)",
              "ราย 1 ชั่วโมง (1H)",
              "ราย 4 ชั่วโมง (4H)",
              "รายสัปดาห์ (Weekly)",
          ],
          index=0,
      )
    with ctrl_col3:
      st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
      show_fib_lines = st.checkbox(
          "เปิดแสดงเส้น Fibonacci บนกราฟ", value=False
      )

    period_map = {
        "1 เดือน": "1mo",
        "3 เดือน": "3mo",
        "6 เดือน": "6mo",
        "1 ปี": "1y",
    }
    hist_filtered = stock.history(period=period_map[chart_period])

    if not hist_filtered.empty:
      full_hist = stock.history(period="2y")
      full_hist["EMA_35"] = full_hist["Close"].ewm(span=35, adjust=False).mean()
      full_hist["EMA_50"] = full_hist["Close"].ewm(span=50, adjust=False).mean()
      full_hist["EMA_89"] = full_hist["Close"].ewm(span=89, adjust=False).mean()
      full_hist["EMA_200"] = (
          full_hist["Close"].ewm(span=200, adjust=False).mean()
      )

      plot_data = full_hist.loc[
          full_hist.index.intersection(hist_filtered.index)
      ]
      if plot_data.empty:
        plot_data = hist_filtered

      plt.style.use("default")
      fig, ax = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
      fig.patch.set_facecolor("#ffffff")
      ax.set_facecolor("#f8fafc")

      ax.plot(
          plot_data.index,
          plot_data["Close"],
          color="#0284c7",
          linewidth=1.8,
          label="Close Price",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_35"],
          color="#d97706",
          linewidth=1.2,
          linestyle="--",
          label="EMA 35",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_50"],
          color="#059669",
          linewidth=1.2,
          linestyle="--",
          label="EMA 50",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_89"],
          color="#7c3aed",
          linewidth=1.2,
          linestyle="--",
          label="EMA 89",
      )
      ax.plot(
          plot_data.index,
          plot_data["EMA_200"],
          color="#dc2626",
          linewidth=1.8,
          label="EMA 200",
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
          f"Technical Chart with {tf_label} S/R & Fibonacci -"
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
      st.warning("ไม่พบข้อมูลกราฟในช่วงเวลานี้")

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # --- ข่าวสาร และ บทวิเคราะห์ ---
    col_news, col_analysis = st.columns(2, gap="medium")

    with col_news:
      st.markdown("#### 📰 ข่าวสารและประกาศสำคัญ")
      is_thai_stock = ticker_symbol.endswith(".BK")

      if is_thai_stock:
        clean_symbol = display_ticker_label.upper()
        settrade_url = (
            f"https://www.settrade.com/th/equities/quote/{clean_symbol}/news"
        )
        st.info(
            "🇹🇭 ศูนย์รวมข้อมูลและข่าวสารตลาดหลักทรัพย์ไทยแบบเรียลไทม์:"
            f" \n\n👉 **[เปิดหน้าข่าวหลักทรัพย์จาก SETTRADE ({clean_symbol})]"
            f"({settrade_url})**"
        )

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
          for news_date, item in filtered_news[:4]:
            title = item.get("title", "No Title")
            publisher = item.get("publisher", "Unknown Source")
            link = item.get("link", "#")

            st.markdown(f"🔹 **[{title}]({link})**")
            st.caption(f"สำนักข่าว: {publisher}")
            st.markdown("---")
        else:
          if not is_thai_stock:
            st.info("ไม่พบข่าวสารในช่วง 90 วันล่าสุด")
      else:
        if not is_thai_stock:
          st.info("ไม่มีรายงานข่าวสำหรับสินทรัพย์นี้ในระบบขณะนี้")

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
