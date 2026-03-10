import streamlit as st
import pandas as pd
from google import genai
import plotly.express as px
import json
import re
from io import StringIO

# 1. SETTINGS & THEME
st.set_page_config(page_title="Amazon AI Analyst", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #161b22; color: #58a6ff; border: 1px solid #30363d; border-radius: 10px; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. SMART DATA LOADER
def load_data(file):
    try:
        content = file.read().decode('utf-8', errors='ignore')
        match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
        csv_text = match.group(1).strip() if match else content.strip()
        return pd.read_csv(StringIO(csv_text))
    except Exception as e:
        st.error(f"Upload Error: {e}")
        return None

# 3. INITIALIZE AI
client = genai.Client(api_key="YOUR_API_KEY")

# 4. ENHANCED SYSTEM PROMPT
# This prompt tells the AI it can either return a CHART (JSON) or a CONVERSATION (Text)
SYSTEM_PROMPT = """
You are a Senior Amazon Data Analyst. You have a dataset with these columns:
[order_id, order_date, product_id, product_category, price, discount_percent, 
quantity_sold, customer_region, payment_method, rating, review_count, 
discounted_price, total_revenue]

TASK:
- If the user asks for a chart or a visual, return a JSON object with keys: 
  "type": "chart", "chart_type": "bar/line/pie", "x": "col", "y": "col", "title": "...", "insight": "..."
- If the user asks a general question (e.g. 'What is the best category?'), return a JSON object with:
  "type": "text", "body": "Your detailed answer here based on the data."
- ALWAYS return valid JSON. Do not include markdown blocks.
"""

# 5. SIDEBAR & FILE UPLOAD
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=70)
    st.title("Amazon AI Suite")
    uploaded_file = st.file_uploader("Upload 'Amazon Sales (1).csv'", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        # Dashboard Header
        st.title("🚀 Amazon Conversational BI")
        
        # KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", f"${df['total_revenue'].sum():,.0f}")
        c2.metric("Orders", len(df))
        c3.metric("Avg Rating", f"{df['rating'].mean():.1f} ⭐")
        c4.metric("Top Region", df['customer_region'].mode()[0])

        st.divider()

        # Chat Interface
        user_query = st.text_input("💬 Ask the AI Analyst about your Amazon data...", 
                                   placeholder="e.g., 'What is our trend?' or 'Compare regions'")

        if user_query:
            with st.status("🧠 Gemini is analyzing...") as status:
                full_prompt = f"{SYSTEM_PROMPT}\nData Context: {df.head(5).to_string()}\nUser: {user_query}"
                response = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)
                
                try:
                    # Parse the AI response
                    raw_text = response.text.replace("```json", "").replace("```", "").strip()
                    res = json.loads(raw_text)

                    # Handle Text Answers
                    if res.get("type") == "text":
                        with st.chat_message("assistant"):
                            st.write(res["body"])
                    
                    # Handle Chart Answers
                    elif res.get("type") == "chart":
                        st.subheader(res['title'])
                        if res['chart_type'] == 'bar':
                            fig = px.bar(df, x=res['x'], y=res['y'], color=res['x'], template="plotly_dark")
                        elif res['chart_type'] == 'line':
                            fig = px.line(df, x=res['x'], y=res['y'], markers=True, template="plotly_dark")
                        else:
                            fig = px.pie(df, names=res['x'], values=res['y'], template="plotly_dark")
                        
                        st.plotly_chart(fig, width="stretch")
                        st.info(f"💡 **Insight:** {res['insight']}")

                    status.update(label="Analysis Complete", state="complete")
                except Exception as e:
                    st.error("I understood your question but had trouble formatting the answer. Try asking for a 'chart' specifically.")
                    status.update(label="Formatting Error", state="error")
