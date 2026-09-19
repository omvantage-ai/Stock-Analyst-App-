import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

# 1. ऐप की सेटिंग और डिज़ाइन (प्रोफेशनल लुक के लिए)
st.set_page_config(page_title="स्मार्ट AI स्टॉक एनालिस्ट", layout="wide", page_icon="📈")
st.title("📈 स्मार्ट AI स्टॉक एनालिस्ट")
st.markdown("भारतीय शेयर बाजार का विश्लेषण करने के लिए आपका अपना स्मार्ट टर्मिनल।")

# 2. साइडबार में API Key डालने की जगह
API_KEY = st.text_input("🔑 अपनी Gemini API Key डालें:", type="password", help="यहाँ अपनी Google Gemini Pro API Key डालें।")

st.write("---")

# 3. यूज़र इनपुट फ़ील्ड्स
col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.text_input("कंपनी का नाम या Ticker लिखें (उदा. RELIANCE, INFOSYS):", "RELIANCE")
with col2:
    exchange = st.selectbox("एक्सचेंज चुनें:", ["NSE", "BSE"], help="याहू फाइनेंस भारतीय कंपनियों के लिए सही सिंबल खोजने के लिए एक्सचेंज का उपयोग करता है।")

# जब बटन दबाया जाए
if st.button("📊 स्मार्ट एनालिसिस दिखाएं"):
    
    if not API_KEY:
        st.error("कृपया साइडबार में अपनी API Key डालें!")
    else:
        st.write("---")
        
        # 4. याहू फाइनेंस के लिए टिकर तैयार करना
        # याहू फाइनेंस को 'NSE' या 'BSE' टिकर की आवश्यकता होती है।
        yfinance_ticker = company_name.upper()
        
        if exchange == "NSE":
            yfinance_ticker += ".NS"
        elif exchange == "BSE":
            yfinance_ticker += ".BO"

        st.subheader(f"🔴 {company_name.upper()} ({exchange}) का डेटा लोड हो रहा है...")

        # ---- भाग 1: याहू फाइनेंस से लाइव डेटा प्राप्त करना ----
        with st.spinner("लाइव डेटा प्राप्त किया जा रहा है..."):
            ticker_data = yf.Ticker(yfinance_ticker)
            try:
                # 1-मिनट अंतराल के साथ 1-दिन का डेटा प्राप्त करने का प्रयास करें (लाइव डेटा के लिए)
                hist = ticker_data.history(period="1d", interval="1m")
                
                if hist.empty:
                    # यदि 1-मिनट का डेटा नहीं है, तो व्यापक डेटा का प्रयास करें (जैसे कि 5-दिन 1-घंटे अंतराल के साथ)
                    hist = ticker_data.history(period="5d", interval="1h")

                if hist.empty:
                    st.error(f"{company_name.upper()} के लिए डेटा नहीं मिला। कृपया टिकर की जाँच करें या फिर प्रयास करें।")
                else:
                    st.write(f"अंतिम डेटा अपडेट: {hist.index[-1].strftime('%d %b %Y, %H:%M:%S')}")

                    # 5. प्लॉटली कैंडलस्टिक चार्ट बनाना
                    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                                        open=hist['Open'],
                                                        high=hist['High'],
                                                        low=hist['Low'],
                                                        close=hist['Close'])])
                    fig.update_layout(title=f"{company_name.upper()} - लाइव कैंडलस्टिक चार्ट (yfinance डेटा)",
                                    yaxis_title='मूल्य',
                                    xaxis_title='समय',
                                    xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"याहू फाइनेंस डेटा प्राप्त करने में एरर: {e}")

        # ---- भाग 2: GEMINI AI एनालिसिस ----
        st.write("---")
        st.subheader("🤖 AI फंडामेंटल एनालिसिस")
        
        # Google Gemini Pro API URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # AI प्रॉम्प्ट को एक वित्तीय विशेषज्ञ की तरह सेट किया गया है
        prompt_text = f"""
        आप एक स्ट्रिक्ट फंडामेंटल स्टॉक एनालिस्ट एजेंट हैं। 
        कंपनी का नाम: {company_name.upper()} (Exchange: {exchange})
        कृपया हालिया वित्तीय डेटा और खबरों के आधार पर इसका पूरा विश्लेषण तैयार करें। 
        इन 3 नियमों पर फोकस करें:
        1. सेक्टर एडवांटेज (PLI, China+1, High Growth सेक्टर).
        2. Low PE vs High Growth (वैल्यूएशन और 15%+ ग्रोथ).
        3. एग्जिट ट्रिगर्स (प्रमोटर प्लेज, ऑडिटर इस्तीफा, अचानक प्रॉफिट गिरना, फ्रॉड केस).
        अंत में [BUY / WAIT / STRICT AVOID] का स्पष्ट निष्कर्ष दें।
        
        प्रतिक्रिया वित्तीय डेटा और विश्वसनीय समाचारों पर आधारित होनी चाहिए।
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }
        
        with st.spinner("AI डेटा और खबरें पढ़ रहा है..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    st.success("एनालिसिस पूरा हुआ!")
                    st.write(ai_response)
                else:
                    st.error("AI सर्वर पर लोड ज्यादा है। कृपया कुछ सेकंड बाद दोबारा कोशिश करें।")
            except Exception as e:
                st.error(f"AI कॉल में दिक्कत: {e}")

# 6. ऐप के बारे में जानकारी
st.sidebar.write("---")
st.sidebar.subheader("ऐप के बारे में")
st.sidebar.write("यह ऐप याहू फाइनेंस से लाइव मार्केट डेटा और Google Gemini Pro AI से वित्तीय विश्लेषण प्रदान करता है।")
st.sidebar.write("डिज़ाइन किया गया है: [आपका नाम या आपकी टीम का नाम]")
