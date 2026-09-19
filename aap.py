import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# 1. ऐप की सेटिंग और डिज़ाइन
st.set_page_config(page_title="AI Stock Analyst Pro", layout="wide", page_icon="📈")
st.title("📈 AI Stock & Options Analyst Pro")
st.markdown("फंडामेंटल एनालिसिस, लाइव चार्ट्स और स्मार्ट ट्रेड सेटअप (SL & Targets) के साथ।")

# 2. साइडबार में API Key 
API_KEY = st.sidebar.text_input("🔑 अपनी Gemini API Key डालें:", type="password")

st.write("---")
col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.text_input("कंपनी का नाम या Ticker लिखें (उदा. RELIANCE, CRUDEOIL, NIFTY):", "RELIANCE")
with col2:
    exchange = st.selectbox("एक्सचेंज चुनें:", ["NSE", "BSE", "MCX"])

if st.button("📊 स्मार्ट एनालिसिस और ट्रेड सेटअप दिखाएं"):
    
    if not API_KEY:
        st.error("कृपया साइडबार में अपनी API Key डालें!")
    else:
        # स्क्रीन को दो हिस्सों में बांटना (बाएं चार्ट, दाएं टेक्निकल मीटर)
        chart_col, meter_col = st.columns([2, 1])
        
        with chart_col:
            st.subheader(f"🔴 {company_name} - एडवांस्ड लाइव चार्ट")
            # TradingView का लाइव चार्ट (RSI, MACD और Bollinger Bands के साथ प्री-लोडेड)
            tv_chart = f"""
            <div class="tradingview-widget-container">
              <div id="tv_chart_1"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
              "width": "100%",
              "height": 450,
              "symbol": "{exchange}:{company_name}",
              "interval": "D",
              "timezone": "Asia/Kolkata",
              "theme": "dark",
              "style": "1",
              "locale": "in",
              "enable_publishing": false,
              "allow_symbol_change": true,
              "studies": [
                "RSI@tv-basicstudies",
                "MACD@tv-basicstudies",
                "BB@tv-basicstudies"
              ],
              "container_id": "tv_chart_1"
            }}
              );
              </script>
            </div>
            """
            components.html(tv_chart, height=470)

        with meter_col:
            st.subheader("⚡ लाइव बाय/सेल सिग्नल")
            # TradingView Technical Analysis Meter (20+ इंडिकेटर्स का निचोड़)
            tv_meter = f"""
            <div class="tradingview-widget-container">
              <div class="tradingview-widget-container__widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
              {{
              "interval": "1D",
              "width": "100%",
              "isTransparent": true,
              "height": 450,
              "symbol": "{exchange}:{company_name}",
              "showIntervalTabs": true,
              "displayMode": "single",
              "locale": "in",
              "colorTheme": "dark"
            }}
              </script>
            </div>
            """
            components.html(tv_meter, height=470)

        # ---- भाग 2: GEMINI AI स्मार्ट ट्रेड सेटअप ----
        st.write("---")
        st.subheader("🤖 AI स्मार्ट ट्रेड सेटअप (SL & Targets)")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # AI प्रॉम्प्ट को पूरी तरह से एक प्रो-ट्रेडर की तरह सेट किया गया है
        prompt_text = f"""
        आप एक टॉप-लेवल स्टॉक मार्केट और कमोडिटी ट्रेडर हैं।
        एसेट का नाम: {company_name} (Exchange: {exchange})
        
        कृपया अपनी रिपोर्ट को 2 स्पष्ट भागों में दें:
        
        भाग 1: टेक्निकल ट्रेड सेटअप (Swing / Positional)
        - VWAP, SuperTrend, RSI, MACD और Bollinger Bands जैसे इंडिकेटर्स के आधार पर वर्तमान टेक्निकल ट्रेंड क्या है?
        - स्पष्ट राय दें: [STRONG BUY / BUY / HOLD / SELL]
        - Entry Price (किस भाव के आसपास एंट्री लें?)
        - Stop Loss (सटीक स्टॉप लॉस लेवल क्या होना चाहिए?)
        - Target 1 और Target 2 (मुनाफा कहाँ बुक करें?)
        - रिस्क-रिवॉर्ड रेश्यो क्या बन रहा है?
        
        भाग 2: फंडामेंटल चेक (लॉन्ग टर्म ट्रेंड)
        - सेक्टर एडवांटेज या हालिया खबरें।
        - प्रमोटर प्लेज, ऑडिटर या कोई रेड फ्लैग?
        """
        
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}
        
        with st.spinner("AI इंडिकेटर्स और सेटअप कैलकुलेट कर रहा है..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    st.success("ट्रेड सेटअप तैयार है!")
                    st.write(ai_response)
                else:
                    st.error("API ओवरलोड! कृपया कुछ सेकंड बाद दोबारा कोशिश करें।")
            except Exception as e:
                st.error(f"एरर: {e}")
            
