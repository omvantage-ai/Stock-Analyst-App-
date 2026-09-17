import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# 1. ऐप की सेटिंग और डिज़ाइन
st.set_page_config(page_title="AI Stock Analyst Pro", layout="wide", page_icon="📈")
st.title("📈 AI Stock Analyst & Live Chart")
st.markdown("TradingView चार्ट्स और Gemini AI के साथ अपना खुद का स्मार्ट टर्मिनल।")

# 2. साइडबार में API Key डालने की जगह (ताकि कोड में न दिखे)
API_KEY = st.sidebar.text_input("अपनी Gemini API Key डालें:", type="password")

# 3. यूज़र से कंपनी का नाम लेना (NSE/BSE सिंबल के साथ)
st.write("---")
col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.text_input("कंपनी का नाम या NSE/BSE Ticker लिखें (उदा. HSCL, RELIANCE):", "HSCL")
with col2:
    exchange = st.selectbox("एक्सचेंज चुनें:", ["NSE", "BSE"])

# जब बटन दबाया जाए
if st.button("📊 चार्ट और AI एनालिसिस दिखाएं"):
    
    if not API_KEY:
        st.error("कृपया साइडबार में अपनी API Key डालें!")
    else:
        # ---- भाग 1: TRADINGVIEW लाइव चार्ट (HTML Widget) ----
        st.subheader(f"🔴 {company_name} का लाइव चार्ट")
        
        # TradingView का फ्री विजेट कोड
        tv_widget = f"""
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div id="tradingview_12345"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
          "width": "100%",
          "height": 400,
          "symbol": "{exchange}:{company_name}",
          "interval": "D",
          "timezone": "Asia/Kolkata",
          "theme": "dark",
          "style": "1",
          "locale": "in",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_12345"
        }}
          );
          </script>
        </div>
        <!-- TradingView Widget END -->
        """
        # स्ट्रीमलिट में चार्ट दिखाना
        components.html(tv_widget, height=420)

        # ---- भाग 2: GEMINI AI एनालिसिस ----
        st.subheader("🤖 AI फंडामेंटल एनालिसिस")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        prompt_text = f"""
        आप एक स्ट्रिक्ट फंडामेंटल स्टॉक एनालिस्ट एजेंट हैं। 
        कंपनी का नाम: {company_name} (Exchange: {exchange})
        कृपया हालिया वित्तीय डेटा और खबरों के आधार पर इसका पूरा विश्लेषण तैयार करें। 
        इन 3 नियमों पर फोकस करें:
        1. सेक्टर एडवांटेज (PLI, China+1, High Growth सेक्टर).
        2. Low PE vs High Growth (वैल्यूएशन और 15%+ ग्रोथ).
        3. एग्जिट ट्रिगर्स (प्रमोटर प्लेज, ऑडिटर इस्तीफा, अचानक प्रॉफिट गिरना, फ्रॉड केस).
        अंत में [BUY / WAIT / STRICT AVOID] का स्पष्ट निष्कर्ष दें।
        """
        
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}
        
        with st.spinner("AI डेटा और खबरें पढ़ रहा है..."):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    st.success("एनालिसिस पूरा हुआ!")
                    st.write(ai_response)
                else:
                    st.error("API ओवरलोड या एरर! 1 मिनट बाद कोशिश करें।")
            except Exception as e:
                st.error(f"कुछ गड़बड़ हो गई: {e}")
