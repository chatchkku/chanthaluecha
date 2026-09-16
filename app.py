import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

# --- ตั้งค่าหน้าเว็บให้เป็นแบบ Wide Mode ---
st.set_page_config(
    page_title="Chanthaluecha Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ส่วนหัวของแอป ---
st.title("📈 Chanthaluecha Intelligence Dashboard")
st.markdown("ระบบวิเคราะห์ข้อมูลหุ้นและการลงทุนแบบครบวงจร")

# รับค่าชื่อหุ้นจากผู้ใช้งาน
ticker_input = st.text_input(
    "🔍 พิมพ์ชื่อย่อหุ้น (เช่น BDMS, TCAP, IVV):", "BDMS"
)

if ticker_input:
  ticker_symbol = ticker_input.strip().upper()
  if not ticker_symbol.endswith(".BK") and ticker_symbol not in [
      "IVV",
      "VT",
      "SPY",
      "QQQ",
      "AAPL",
      "MSFT",
      "NVDA",
      "TSLA",
      "BTC-USD",
  ]:
    # หากเป็นหุ้นไทยแต่ไม่ได้พิมพ์ .BK ให้เติมให้อัตโนมัติ
    if len(ticker_symbol) <= 5:
      ticker_symbol = ticker_symbol + ".BK"

  with st.spinner(f"กำลังดึงข้อมูลของหุ้น {ticker_symbol}..."):
    try:
      stock = yf.Ticker(ticker_symbol)
      df = stock.history(period="1y")

      if df.empty:
        st.error(f"ไม่พบข้อมูลสำหรับหุ้น {ticker_symbol} กรุณาตรวจสอบใหม่อีกครั้ง")
      else:
        info = stock.info

        # --- แสดงข้อมูลพื้นฐาน (Fundamentals) ---
        st.subheader("📊 ข้อมูลพื้นฐานทางการเงิน")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
          pe = info.get("trailingPE", "N/A")
          st.metric(
              "P/E Ratio", f"{pe:.2f}" if isinstance(pe, (int, float)) else pe
          )
        with col2:
          pb = info.get("priceToBook", "N/A")
          st.metric(
              "P/BV Ratio", f"{pb:.2f}" if isinstance(pb, (int, float)) else pb
          )
        with col3:
          roe = info.get("returnOnEquity", None)
          roe_val = f"{roe * 100:.2f}%" if roe else "N/A"
          st.metric("ROE", roe_val)
        with col4:
          div = info.get("dividendYield", None)
          div_val = f"{div * 100:.2f}%" if div else "N/A"
          st.metric("Dividend Yield", div_val)

        st.divider()

        # --- กราฟราคาและการวิเคราะห์ทางเทคนิค ---
        st.subheader("📉 กราฟราคาและเส้นค่าเฉลี่ย (EMA)")

        # คำนวณเส้น EMA 35, 50, 89, 200
        df["EMA35"] = df["Close"].ewm(span=35, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA89"] = df["Close"].ewm(span=89, adjust=False).mean()
        df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

        # วาดกราฟด้วย Matplotlib
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(
            df.index,
            df["Close"],
            label="Close Price",
            color="black",
            alpha=0.6,
        )
        ax.plot(
            df.index, df["EMA35"], label="EMA 35", color="purple", linewidth=1
        )
        ax.plot(
            df.index, df["EMA50"], label="EMA 50", color="blue", linewidth=1
        )
        ax.plot(
            df.index, df["EMA89"], label="EMA 89", color="orange", linewidth=1
        )
        ax.plot(
            df.index,
            df["EMA200"],
            label="EMA 200",
            color="red",
            linewidth=1.5,
        )

        ax.set_title(
            f"Price Chart & EMA for {ticker_symbol}", fontsize=14, fontweight="bold"
        )
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend(loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig)

        st.divider()

        # --- ส่วนบันทึกการลงทุน (Trade Journal) ---
        st.subheader("📝 บันทึกการลงทุนและแผนกลยุทธ์")
        with st.form("journal_form"):
          st.checkbox("📈 วิเคราะห์แนวโน้มหลักและโครงสร้างราคาเรียบร้อย")
          st.checkbox("🎯 ตรวจสอบจุดแนวรับ-แนวต้านและแผน DCA แล้ว")
          note = st.text_area(
              "บันทึกข้อความ / แผนการเทรด:",
              placeholder="ระบุเหตุผลในการเข้าซื้อ หรือแผนระยะยาว...",
          )
          submitted = st.form_submit_button("💾 บันทึกข้อมูล")
          if submitted:
            st.success("บันทึกข้อมูลสำเร็จเรียบร้อยครับ!")

    except Exception as e:
      st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
