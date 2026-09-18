import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- ตั้งค่าหน้าจอ Streamlit ---
st.set_page_config(
    page_title="Investment Dashboard & Watchlist Radar",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Investment & DCA Tracking Dashboard")
st.markdown("ระบบติดตามพอร์ตลงทุนและการสแกนหาจังหวะสะสมหุ้น (Oversold RSI $\le$ 35 & Multi-EMA Radar)")

# --- 1. CONFIGURATION & WATCHLIST ---
# รายชื่อหุ้นที่คุณสนใจ (หุ้นไทย และ ETF ต่างประเทศ)
default_watchlist = ["BDMS.BK", "TCAP.BK", "TTB.BK", "GULF.BK", "CBG.BK", "IVV", "VT"]

st.sidebar.header("⚙️ ตั้งค่าพอร์ตและตัวกรอง")
selected_tickers = st.sidebar.multiselect(
    "เลือกหุ้น/ETF ใน Watchlist:",
    options=default_watchlist,
    default=default_watchlist
)

# --- 2. TOP FEATURE: EXACT SPAN EMA WATCHLIST RADAR (OVERSOLD RSI <= 35 FILTER) ---
st.markdown("### 🔔 Watchlist Radar: หาจังหวะหุ้นย่อตัวโซน Oversold (RSI $\le$ 35)")

@st.cache_data(ttl=900)
def scan_exact_span_ema_radar(tickers):
    matched_results = []
    ema_spans = [35, 89, 200]

    for t in tickers:
        clean_name = t.replace(".BK", "").upper()
        
        # 1. สแกนไทม์เฟรม Daily (1d)
        try:
            df_d = yf.download(t, period="2y", interval="1d", progress=False, auto_adjust=True)
            if isinstance(df_d.columns, pd.MultiIndex):
                df_d.columns = df_d.columns.get_level_values(0)
            
            if not df_d.empty and len(df_d) >= 30:
                delta = df_d["Close"].diff()
                gain = delta.clip(lower=0)
                loss = -1 * delta.clip(upper=0)
                avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                rs = avg_gain / avg_loss
                df_d["RSI"] = 100 - (100 / (1 + rs))

                close_d = df_d["Close"].iloc[-1]
                rsi_d = df_d["RSI"].iloc[-1]

                for span in ema_spans:
                    if len(df_d) >= span:
                        ema_val = df_d["Close"].ewm(span=span, adjust=False).mean().iloc[-1]
                        diff_d = ((close_d - ema_val) / ema_val) * 100
                        
                        # เงื่อนไข: ราคาอยู่ใกล้เส้น EMA (-3% ถึง +3%) และ RSI อยู่ในโซน Oversold (<= 35)
                        if -3.0 <= diff_d <= 3.0 and rsi_d <= 35:
                            matched_results.append({
                                "Ticker": clean_name,
                                "Timeframe": "Daily (1D)",
                                "EMA Level": f"EMA {span}",
                                "Price": round(float(close_d), 2),
                                "EMA Value": round(float(ema_val), 2),
                                "Distance (%)": round(float(diff_d), 2),
                                "RSI": round(float(rsi_d), 2)
                            })
        except Exception as e:
            pass

        # 2. สแกนไทม์เฟรม 1 ชั่วโมง (60m)
        try:
            for span in ema_spans:
                req_period = "10d" if span == 35 else ("30d" if span == 89 else "120d")
                df_1h = yf.download(t, period=req_period, interval="60m", progress=False, auto_adjust=True)
                if isinstance(df_1h.columns, pd.MultiIndex):
                    df_1h.columns = df_1h.columns.get_level_values(0)
                
                if not df_1h.empty and len(df_1h) >= span:
                    delta = df_1h["Close"].diff()
                    gain = delta.clip(lower=0)
                    loss = -1 * delta.clip(upper=0)
                    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
                    rs = avg_gain / avg_loss
                    df_1h["RSI"] = 100 - (100 / (1 + rs))

                    close_1h = df_1h["Close"].iloc[-1]
                    rsi_1h = df_1h["RSI"].iloc[-1]
                    ema_val = df_1h["Close"].ewm(span=span, adjust=False).mean().iloc[-1]
                    diff_1h = ((close_1h - ema_val) / ema_val) * 100
                    
                    # เงื่อนไข 1H: ราคาใกล้เส้น EMA (-1.5% ถึง +1.5%) และ RSI <= 35
                    if -1.5 <= diff_1h <= 1.5 and rsi_1h <= 35:
                        matched_results.append({
                            "Ticker": clean_name,
                            "Timeframe": "1 Hour (60M)",
                            "EMA Level": f"EMA {span}",
                            "Price": round(float(close_1h), 2),
                            "EMA Value": round(float(ema_val), 2),
                            "Distance (%)": round(float(diff_1h), 2),
                            "RSI": round(float(rsi_1h), 2)
                        })
        except Exception as e:
            pass

    return matched_results

if st.button("🚀 เริ่มสแกนหารอบ Oversold (RSI <= 35)", type="primary"):
    if not selected_tickers:
        st.warning("กรุณาเลือกหุ้นใน Watchlist อย่างน้อย 1 ตัวจากเมนูด้านข้าง")
    else:
        with st.spinner("กำลังประมวลผลข้อมูลราคาและคำนวณอินดิเคเตอร์..."):
            scan_data = scan_exact_span_ema_radar(selected_tickers)
            
            if scan_data:
                df_scan = pd.DataFrame(scan_data)
                st.success(f"พบหุ้นเข้าเงื่อนไข Oversold (RSI $\le$ 35) ทั้งหมด {len(df_scan)} รายการ!")
                st.dataframe(df_scan, use_container_width=True)
            else:
                st.info("ยังไม่พบหุ้นใน Watchlist ที่ย่อตัวลงมาแตะโซน Oversold (RSI <= 35) ณ ช่วงเวลานี้ ลองใหม่อีกครั้งภายหลังครับ")

st.markdown("---")

# --- 3. OVERVIEW & PRICE TRACKING SECTION ---
st.markdown("### 📊 ข้อมูลราคาปัจจุบันและกราฟทางเทคนิคเบื้องต้น")

selected_stock = st.selectbox("เลือกหุ้นเพื่อดูรายละเอียดเชิงลึก:", options=selected_tickers)

if selected_stock:
    try:
        df_stock = yf.download(selected_stock, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if isinstance(df_stock.columns, pd.MultiIndex):
            df_stock.columns = df_stock.columns.get_level_values(0)
            
        if not df_stock.empty:
            # คำนวณเส้น EMA และ RSI สำรองไว้แสดงผล
            df_stock["EMA_35"] = df_stock["Close"].ewm(span=35, adjust=False).mean()
            df_stock["EMA_89"] = df_stock["Close"].ewm(span=89, adjust=False).mean()
            
            delta = df_stock["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -1 * delta.clip(upper=0)
            avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
            rs = avg_gain / avg_loss
            df_stock["RSI"] = 100 - (100 / (1 + rs))
            
            cur_price = float(df_stock["Close"].iloc[-1])
            cur_rsi = float(df_stock["RSI"].iloc[-1])
            cur_ema35 = float(df_stock["EMA_35"].iloc[-1])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("ราคาปัจจุบัน", f"{cur_price:.2f}")
            col2.metric("ค่า RSI (14)", f"{cur_rsi:.2f}", delta="Oversold Zone (<=35)" if cur_rsi <= 35 else "Normal", delta_color="inverse" if cur_rsi <= 35 else "off")
            col3.metric("EMA 35", f"{cur_ema35:.2f}")
            
            st.markdown("#### กราฟราคาปิดย้อนหลัง 6 เดือน")
            st.line_chart(df_stock[["Close", "EMA_35", "EMA_89"]])
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลของ {selected_stock} ได้: {e}")
