import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

# 1. ऐप की सेटिंग
st.set_page_config(page_title="स्मार्ट AI स्टॉक एनालिस्ट", layout="wide", page_icon="📈")
st.title("📈 स्मार्ट AI स्टॉक एनालिस्ट")

# 2. साइडबार में API Key (इसे हर बार ऐप खोलने पर डालना होगा)
API_KEY = st.text_input("🔑 अपनी Gemini API Key डालें:", type="password")

st.write("---")
col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.text_input("कंपनी का नाम (उदा. RELIANCE, TCS):", "RELIANCE")
with col2:
    exchange = st.selectbox("एक्सचेंज:", ["NSE", "BSE"])

if st.button("📊 एनालिसिस और चार्ट दिखाएं"):
    
    if not API_KEY:
        st.error("कृपया मेनू (≡) से साइडबार खोलें और अपनी API Key डालें!")
    else:
        st.write("---")
        yfinance_ticker = company_name.upper()
        if exchange == "NSE":
            yfinance_ticker += ".NS"
        elif exchange == "BSE":
            yfinance_ticker += ".BO"

        st.subheader(f"🔴 {company_name.upper()} का चार्ट (पिछले 1 महीने का ट्रेंड)")

        # ---- भाग 1: चार्ट (वीकेंड प्रूफ) ----
        with st.spinner("डेटा लोड हो रहा है..."):
            ticker_data = yf.Ticker(yfinance_ticker)
            try:
                # 1 महीने का डेली डेटा ला रहे हैं ताकि वीकेंड पर भी चार्ट खाली न दिखे
                hist = ticker_data.history(period="1mo", interval="1d")
                
                if hist.empty:
                    st.error("डेटा नहीं मिला। कृपया कंपनी का सही नाम (Ticker) चेक करें।")
                else:
                    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                                        open=hist['Open'],
                                                        high=hist['High'],
                                                        low=hist['Low'],
                                                        close=hist['Close'])])
                    fig.update_layout(yaxis_title='मूल्य', xaxis_title='समय', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"चार्ट एरर: {e}")

        # ---- भाग 2: AI एनालिसिस ----
        st.write("---")
        st.subheader("🤖 AI फंडामेंटल एनालिसिस")
        
        # नया और फ़ास्ट Gemini 1.5 Flash मॉडल इस्तेमाल कर रहे हैं
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        prompt_text = f"""
        आप एक स्ट्रिक्ट फंडामेंटल स्टॉक एनालिस्ट हैं। 
        कंपनी: {company_name.upper()} ({exchange})
        1. सेक्टर एडवांटेज 2. वैल्यूएशन (PE vs Growth) 3. एग्जिट ट्रिगर्स (रिस्क) के आधार पर इसका विश्लेषण करें।
        अंत में स्पष्ट निष्कर्ष दें: BUY, WAIT, या AVOID.
        """
        
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}
        
        with st.spinner("AI एनालिसिस कर रहा है..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    st.success("एनालिसिस तैयार है!")
                    st.write(result['candidates'][0]['content']['parts'][0]['text'])
                else:
                    # यह लाइन आपको असली एरर बताएगी (अगर API key गलत है तो)
                    st.error(f"API Error: {response.text}") 
            except Exception as e:
                st.error(f"AI कॉल एरर: {e}")
