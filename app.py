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

    # แปลงช่วงเวลากราฟเป็น parameter สำหรับ yfinance interval
    interval_map = {
        "1 เดือน": ("1d", "1mo"),
        "3 เดือน": ("1d", "3mo"),
        "6 เดือน": ("1d", "6mo"),
        "1 ปี": ("1d", "1y"),
    }
    
    # หากเลือก Timeframe รายชั่วโมงหรือรายสัปดาห์จากเมนูด้านบน สามารถปรับเปลี่ยนตัวแปรดึงข้อมูลได้ตามต้องการ
    # ในที่นี้จะดึงข้อมูลตามช่วงเวลาที่เลือกใน chart_period เพื่อให้เส้น EMA คำนวณสดตามแท่งเทียนในช่วงเวลานั้นๆ
    yf_interval, yf_period = interval_map[chart_period]
    
    # ดึงข้อมูลตามช่วงเวลาที่เลือก
    plot_data = stock.history(period=yf_period, interval=yf_interval)

    if not plot_data.empty:
      # คำนวณค่า EMA จากชุดข้อมูลที่ถูกกรองตาม Timeframe ที่เลือกโดยตรง
      plot_data["EMA_35"] = plot_data["Close"].ewm(span=35, adjust=False).mean()
      plot_data["EMA_50"] = plot_data["Close"].ewm(span=50, adjust=False).mean()
      plot_data["EMA_89"] = plot_data["Close"].ewm(span=89, adjust=False).mean()
      plot_data["EMA_200"] = plot_data["Close"].ewm(span=200, adjust=False).mean()

      # ดึงค่าราคาล่าสุดของแต่ละเส้น EMA ตามไทม์เฟรมปัจจุบัน
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
          label="Close Price",
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
