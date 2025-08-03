import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Nasdaq Gap-Up Dashboard", layout="wide")

# Disclaimer Section in UI
st.markdown("""
⚠️ **Disclaimer:** This dashboard is for educational purposes only and is **not intended for real trading**. 
If you choose to use it for trading, you do so at your own discretion and are fully responsible for your actions. 
By using this page, you accept that the owners of this content are **not liable for any losses or issues of any kind**, 
and you release the owners from all forms of liability at all times and locations.
""")

st.title("📈 Nasdaq Gap-Up Prediction Dashboard")

# Sidebar controls
st.sidebar.header("Controls")
selected_symbols = st.sidebar.multiselect("Select Tickers", ["AAPL", "MSFT", "GOOG", "AMZN"], default=["AAPL"])

# Placeholder: simulated prediction results
data = pd.DataFrame({
    "Symbol": selected_symbols,
    "Gap-Up Probability": [75, 62, 85, 55][:len(selected_symbols)],
    "RSI": [65, 48, 72, 50][:len(selected_symbols)],
    "MACD": [1.2, -0.5, 2.1, 0.3][:len(selected_symbols)]
})

# Heatmap
st.subheader("Heatmap of Gap-Up Probabilities")
fig_heatmap = px.imshow([data["Gap-Up Probability"]],
                        labels=dict(x="Ticker", y="Probability", color="Gap-Up %"),
                        x=data["Symbol"],
                        y=[""],
                        color_continuous_scale="RdYlGn")
st.plotly_chart(fig_heatmap, use_container_width=True)

# Candlestick chart example for first symbol
st.subheader("Candlestick Chart")
fig_candle = go.Figure(data=[go.Candlestick(x=pd.date_range(start="2025-07-01", periods=10),
                                            open=[100,102,101,103,104,106,107,108,107,109],
                                            high=[102,103,102,104,105,107,108,109,108,110],
                                            low=[99,101,100,102,103,105,106,107,106,108],
                                            close=[101,102,103,104,106,107,108,107,109,110])])
st.plotly_chart(fig_candle, use_container_width=True)

# Table of predictions
st.subheader("Prediction Table")
st.dataframe(data)

# PDF generation with Disclaimer included
def generate_pdf(df, heatmap_fig, candle_fig):
    tmp_heatmap = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp_candle = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    heatmap_fig.write_image(tmp_heatmap.name)
    candle_fig.write_image(tmp_candle.name)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Nasdaq Gap-Up Prediction Report", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, "⚠️ Disclaimer: This report is for educational purposes only and is not intended for real trading. If you choose to use it for trading, you do so at your own discretion and are fully responsible for your actions. By using this report, you accept that the owners of this content are not liable for any losses or issues of any kind, and you release the owners from all forms of liability at all times and locations.")
    pdf.ln(5)

    pdf.set_font("Arial", '', 12)
    for idx, row in df.iterrows():
        pdf.cell(200, 10, f"{row['Symbol']}: Gap-Up Probability {row['Gap-Up Probability']}% | RSI {row['RSI']} | MACD {row['MACD']}", ln=True)
    pdf.add_page()
    pdf.cell(200, 10, "Heatmap", ln=True, align='C')
    pdf.image(tmp_heatmap.name, x=10, y=30, w=180)
    pdf.add_page()
    pdf.cell(200, 10, "Candlestick Chart", ln=True, align='C')
    pdf.image(tmp_candle.name, x=10, y=30, w=180)

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmpfile.name)
    return tmpfile.name

st.subheader("📄 Download Reports")
report_csv = data.to_csv(index=False).encode("utf-8")
st.download_button(label="Download CSV", data=report_csv, file_name="gapup_report.csv", mime="text/csv")

pdf_file = generate_pdf(data, fig_heatmap, fig_candle)
with open(pdf_file, "rb") as f:
    st.download_button(label="Download PDF", data=f, file_name="gapup_report.pdf", mime="application/pdf")

def cleanup_temp_files(*files):
    for file in files:
        try:
            os.remove(file)
        except:
            pass

cleanup_temp_files(pdf_file)
