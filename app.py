import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. ตั้งค่าหน้าเพจ
# ==========================================
st.set_page_config(page_title="My Smart Investment App", layout="wide", page_icon="📈")

# ==========================================
# 2. ฟังก์ชันดึงข้อมูลหุ้น (ระบบเติม .BK อัตโนมัติ)
# ==========================================
@st.cache_data(ttl=600)
def load_stock_data(ticker):
    ticker = ticker.strip().upper()
    
    # รายชื่อหุ้นสากล/ETF ยอดนิยม (เช่น IVV, VT ที่คุณสนใจ)
    global_symbols = ["IVV", "VT", "SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "BTC-USD"]
    
    if "." in ticker or ticker in global_symbols:
        stock_obj = yf.Ticker(ticker)
        hist = stock_obj.history(period="1y")
        if not hist.empty:
            return hist, stock_obj.info, ticker

    # ถ้าไม่มีจุด ลองค้นหาแบบหุ้นไทย (.BK) ก่อน
    thai_ticker = ticker if ticker.endswith(".BK") else ticker + ".BK"
    stock_obj = yf.Ticker(thai_ticker)
    hist = stock_obj.history(period="1y")
    
    if not hist.empty:
        return hist, stock_obj.info, thai_ticker

    # ถ้าหุ้นไทยไม่มี ลองหาแบบหุ้นสากลปกติ
    stock_obj = yf.Ticker(ticker)
    hist = stock_obj.history(period="1y")
    if not hist.empty:
        return hist, stock_obj.info, ticker

    return pd.DataFrame(), {}, ticker

# ==========================================
# 3. ส่วนแสดงผลหลัก (UI)
# ==========================================
st.title("📈 Smart Investment Dashboard")
st.markdown("ระบบวิเคราะห์หุ้น: พื้นฐาน + เทคนิค + วินัยการลงทุน")

# ช่องค้นหาหุ้น
ticker_input = st.text_input("🔍 พิมพ์ชื่อหุ้น (เช่น BDMS, TCAP, IVV, AAPL):", "BDMS")

if ticker_input:
    with st.spinner('กำลังดึงข้อมูล...'):
        hist, info, resolved_ticker = load_stock_data(ticker_input)
        
    if hist.empty:
        st.error(f"❌ ไม่พบข้อมูลสำหรับหุ้น {ticker_input} กรุณาลองใหม่อีกครั้ง")
    else:
        st.success(f"✅ พบข้อมูลหุ้น: {resolved_ticker} (อัปเดตล่าสุด: {hist.index[-1].strftime('%Y-%m-%d')})")
        
        # --- ส่วนที่ 1: อัตราส่วนทางการเงินพื้นฐาน (Fundamental Ratios) ---
        st.subheader("📊 1. อัตราส่วนทางการเงินพื้นฐาน (Fundamentals)")
        
        pe_ratio = info.get("trailingPE", "N/A")
        pb_ratio = info.get("priceToBook", "N/A")
        roe = info.get("returnOnEquity", None)
        roe_str = f"{roe * 100:.2f}%" if roe else "N/A"
        div_yield = info.get("dividendYield", None)
        div_yield_str = f"{div_yield * 100:.2f}%" if div_yield else "N/A"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="P/E Ratio", value=f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio, help="ไม่ควรสูงเกินไป (ขึ้นอยู่กับกลุ่มอุตสาหกรรม)")
        with col2:
            st.metric(label="P/BV Ratio", value=f"{pb_ratio:.2f}" if isinstance(pb_ratio, (int, float)) else pb_ratio, help="เทียบมูลค่าทางบัญชี (เหมาะกับ TCAP, TTB เป็นต้น)")
        with col3:
            st.metric(label="ROE", value=roe_str, help="ความสามารถในการทำกำไร ยิ่งสูงยิ่งดี")
        with col4:
            st.metric(label="Dividend Yield", value=div_yield_str, help="เงินปันผลตอบแทน (เหมาะกับสาย DCA สะสมปันผล)")
            
        st.divider()

        # --- ส่วนที่ 2: กราฟเทคนิค และ แนวรับ-แนวต้าน ---
        st.subheader("📉 2. การวิเคราะห์ทางเทคนิค (Technical Analysis)")
        
        # คำนวณ Pivot Point จากราคาวันก่อนหน้า
        last_day = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
        H, L, C = last_day['High'], last_day['Low'], last_day['Close']
        PP = (H + L + C) / 3
        R1 = (2 * PP) - L
        S1 = (2 * PP) - H
        
        st.markdown(f"**จุดหมุน (Pivot):** {PP:.2f} | **แนวต้าน (R1):** <span style='color:red;'>{R1:.2f}</span> | **แนวรับ (S1):** <span style='color:green;'>{S1:.2f}</span>", unsafe_allow_html=True)
        
        # สร้างกราฟ Candlestick ด้วย Plotly
        fig = go.Figure()
        
        # ใส่แท่งเทียน
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'))
        
        # ใส่เส้น EMA 50 และ 200
        hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
        hist['EMA200'] = hist['Close'].ewm(span=200, adjust=False).mean()
        
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA50'], line=dict(color='blue', width=1.5), name='EMA 50'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA200'], line=dict(color='orange', width=2), name='EMA 200'))
        
        # ใส่เส้นแนวรับแนวต้านแนวนอน (เฉพาะช่วง 30 วันล่าสุดเพื่อให้กราฟดูง่าย)
        recent_dates = hist.index[-30:]
        fig.add_trace(go.Scatter(x=recent_dates, y=[R1]*len(recent_dates), line=dict(color='red', width=2, dash='dash'), name='Resistance (R1)'))
        fig.add_trace(go.Scatter(x=recent_dates, y=[S1]*len(recent_dates), line=dict(color='green', width=2, dash='dash'), name='Support (S1)'))
        
        fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

        # --- ส่วนที่ 3: เช็กลิสต์และบันทึกการตัดสินใจ (Trade Journal) ---
        st.subheader("📝 3. บันทึกการลงทุน (Trade Journal & Checklist)")
        
        with st.form("trade_journal_form"):
            st.markdown("**Checklist ก่อนตัดสินใจซื้อ/ขาย:**")
            col_ck1, col_ck2 = st.columns(2)
            with col_ck1:
                c1 = st.checkbox("📈 ธุรกิจแข็งแกร่ง มีกำไร/ปันผลรองรับ")
                c2 = st.checkbox("🎯 ราคาหุ้นลงมาทดสอบแนวรับสำคัญ")
            with col_ck2:
                c3 = st.checkbox("📊 เทรนด์ใหญ่ยังเป็นขาขึ้น (ยืนเหนือ EMA 200)")
                c4 = st.checkbox("🗓️ สอดคล้องกับแผน DCA ระยะยาว")
            
            st.markdown("**เหตุผลในการตัดสินใจ (Trade Thesis):**")
            note = st.text_area("บันทึกเหตุผลของคุณ เช่น ทุนเดิมอยู่ที่เท่าไหร่, จะซื้อไม้ต่อไปที่ราคาไหน, ตัดขาดทุนตรงไหน", 
                                placeholder="ตัวอย่าง: ซื้อสะสม BDMS ไม้ที่ 3 เพราะราคาลงมาแตะแนวรับ S1 และมีปันผลรองรับ...")
            
            submit_button = st.form_submit_button(label="💾 บันทึกลงในความทรงจำ (บันทึกจำลอง)")
            
            if submit_button:
                st.success("บันทึกข้อมูลเรียบร้อยแล้ว! (ในเวอร์ชันต่อยอด คุณสามารถเขียนโค้ดบันทึกค่าเหล่านี้ลงใน Google Sheets หรือ Database ได้เลยครับ)")
