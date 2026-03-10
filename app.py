import streamlit as st
import pandas as pd
from google import genai  # NEW: Notice the import change
from google.genai import types # NEW: Useful for strict JSON configs
import plotly.express as px
import json

# 1. SETUP & CONFIGURATION
st.set_page_config(page_title="Instant BI Dashboard", layout="wide")

# NEW: The SDK now uses a Client object
client = genai.Client(api_key="enter_your_key") 

# 2. SYSTEM PROMPT (The "Brain" Instructions)
SYSTEM_PROMPT = """
You are a Senior BI Analyst. Use the provided dataset columns to answer the user.
ALWAYS return a valid JSON object with these keys:
"chart_type": (choose 'line', 'bar', or 'pie')
"x": (the column name for X axis)
"y": (the column name for Y axis)
"title": (a professional title)
"insight": (a 1-sentence summary)
"""

# 3. USER INTERFACE (UX & Aesthetics)
st.title("🚀 Conversational BI Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    cols = ", ".join(df.columns)
    
    user_query = st.text_input("Example: 'Show me sales by region'")

    if user_query:
        with st.spinner("AI is generating your dashboard..."):
            # NEW: Call the API using client.models.generate_content
            full_prompt = f"{SYSTEM_PROMPT}\nColumns: {cols}\nUser Request: {user_query}"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash", # Use the latest supported model
                contents=full_prompt
            )
            
            try:
                # Clean the response to ensure it's just raw JSON
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                res_json = json.loads(raw_text)
                
                st.subheader(res_json['title'])
                
                # Render the Chart
                if res_json['chart_type'] == 'bar':
                    fig = px.bar(df, x=res_json['x'], y=res_json['y'], color=res_json['x'])
                elif res_json['chart_type'] == 'line':
                    fig = px.line(df, x=res_json['x'], y=res_json['y'])
                else:
                    fig = px.pie(df, names=res_json['x'], values=res_json['y'])
                
                # NEW: use_container_width is now width='stretch'
                st.plotly_chart(fig, width="stretch") 
                st.info(f"💡 **Insight:** {res_json['insight']}")

            except Exception as e:

                st.error("Error processing AI response. Try rephrasing your question.")
