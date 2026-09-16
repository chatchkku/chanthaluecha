import streamlit as st
import traceback

st.set_page_config(page_title="Debug App", layout="wide")
st.title("🛠️ กำลังตรวจสอบข้อผิดพลาด...")

try:
    import pandas as pd
    import yfinance as yf
    import plotly.graph_objects as go
    st.success("✅ โหลดไลบรารีพื้นฐานทั้งหมดสำเร็จ!")
    
    # ทดสอบดึงข้อมูลหุ้น
    ticker_input = st.text_input("🔍 ลองพิมพ์ชื่อหุ้น:", "BDMS")
    
    if ticker_input:
        ticker = ticker_input.strip().upper()
        stock_obj = yf.Ticker(ticker if "." in ticker else ticker + ".BK")
        hist = stock_obj.history(period="6m")
        info = stock_obj.info
        
        if not hist.empty:
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            st.success(f"✅ ดึงข้อมูลสำเร็จ! ราคาปิดล่าสุด: {hist['Close'].iloc[-1]:.2f}")
            
            # วาดกราฟทดสอบ
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
            fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ ไม่พบข้อมูลราคาหุ้นตัวนี้")

except Exception as e:
    st.error("❌ พบข้อผิดพลาด (Error Details):")
    st.code(traceback.format_exc())
