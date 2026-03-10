import streamlit as st
import pandas as pd
from google import genai
import plotly.express as px
import json

# 1. PAGE CONFIGURATION & THEME
st.set_page_config(page_title="AI BI Dashboard Pro", layout="wide", page_icon="📊")

# Custom CSS for "Impressive & Stylish" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input {
        background-color: #161b22;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INITIALIZE AI CLIENT (2026 SDK)
# Replace with your actual key
client = genai.Client(api_key="Enter_your_key") 

# 3. SYSTEM PROMPT (Accuracy & Hallucination Handling)
SYSTEM_PROMPT = """
You are a Senior BI Analyst. Use the provided dataset columns to answer the user.
RULES:
1. ALWAYS return a valid JSON object.
2. If the data is missing for a request, return {"error": "Description of why data is missing"}.
3. Choose chart_type from: 'line' (trends), 'bar' (comparison), 'pie' (proportions).
4. Identify the correct 'x' and 'y' columns from the user's data.

JSON FORMAT:
{
  "chart_type": "bar",
  "x": "column_name",
  "y": "column_name",
  "title": "Professional Title",
  "insight": "One sentence business takeaway"
}
"""

# 4. SIDEBAR (User Flow & Data Stats)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Insight Engine")
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Upload Business Data", type="csv")
    st.info("Powered by Gemini 2.5 Flash")

# 5. MAIN DASHBOARD LOGIC
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    cols = list(df.columns)
    
    # Header Section
    st.title("🚀 Conversational BI Dashboard")
    
    # KPI Cards (Aesthetics & Innovation)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        if 'Sales' in df.columns:
            st.metric("Total Sales", f"${df['Sales'].sum():,.0f}")
    with col3:
        st.metric("Total Categories", len(df.iloc[:, 1].unique())) # Dynamically looks at 2nd column

    st.divider()

    # Natural Language Input
    user_query = st.text_input("💬 What business insight are you looking for today?", 
                               placeholder="e.g., 'Show me sales by region'")

    if user_query:
        with st.status("🧠 AI Analyst is thinking...", expanded=True) as status:
            # AI Call
            full_prompt = f"{SYSTEM_PROMPT}\nColumns in Dataset: {cols}\nUser Request: {user_query}"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            
            try:
                # Clean and Parse Response
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                res_json = json.loads(raw_text)
                
                if "error" in res_json:
                    st.warning(res_json["error"])
                else:
                    # Chart Generation
                    st.subheader(f"📊 {res_json['title']}")
                    
                    if res_json['chart_type'] == 'bar':
                        fig = px.bar(df, x=res_json['x'], y=res_json['y'], 
                                     color=res_json['x'], template="plotly_dark")
                    elif res_json['chart_type'] == 'line':
                        fig = px.line(df, x=res_json['x'], y=res_json['y'], 
                                      markers=True, template="plotly_dark")
                    else:
                        fig = px.pie(df, names=res_json['x'], values=res_json['y'], 
                                     template="plotly_dark")
                    
                    st.plotly_chart(fig, width="stretch")
                    
                    # Insight Section
                    with st.chat_message("assistant"):
                        st.write(f"**AI Insight:** {res_json['insight']}")
                
                status.update(label="Analysis Complete!", state="complete", expanded=False)

            except Exception as e:
                st.error("The AI had trouble formatting that data. Try a simpler question.")
                status.update(label="Error Found", state="error")
else:
    st.title("Welcome to your AI BI Suite")
    st.info("Please upload a CSV file in the sidebar to begin your analysis.")
    st.image("https://images.unsplash.com/photo-1551288049-bbbda546697a?q=80&w=2070&auto=format&fit=crop", width=700)
