import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import google.generativeai as genai


st.set_page_config(page_title="DAT.co Robo-Advisor", layout="wide")
st.title("📈 Robo-Advisor: MicroStrategy (MSTR) Premium to NAV")


@st.cache_data
def load_data():

    mstr_data = yf.download('MSTR', period='1y')
    btc_data = yf.download('BTC-USD', period='1y')
    

    df = pd.DataFrame(index=mstr_data.index)
    df['MSTR_Close'] = mstr_data['Close']
    df['BTC_Close'] = btc_data['Close']
    df.dropna(inplace=True)
    

    CURRENT_BTC_HOLDINGS = 762099 
    

    ticker = yf.Ticker("MSTR")
    shares_out = ticker.info.get('sharesOutstanding', 35000000) 
    

    df['MSTR_Market_Cap'] = df['MSTR_Close'] * shares_out
    df['BTC_Treasury_Value'] = df['BTC_Close'] * CURRENT_BTC_HOLDINGS
    

    df['Premium_to_NAV'] = (df['MSTR_Market_Cap'] / df['BTC_Treasury_Value']) - 1
    
    return df

df = load_data()


st.subheader("Time-Series: MSTR Premium to NAV")
st.markdown("This chart visualizes how much of a premium investors are paying for MSTR stock relative to its actual Bitcoin holdings over the last year.")


fig = px.line(
    df, 
    x=df.index, 
    y='Premium_to_NAV', 
    title="Daily Premium/Discount to Net Asset Value",
    labels={'Premium_to_NAV': 'Premium to NAV', 'index': 'Date'}
)
fig.update_layout(yaxis_tickformat='.2%') 
st.plotly_chart(fig, use_container_width=True)


if st.checkbox("Show Raw Data"):
    st.dataframe(df.tail(10))


st.subheader("🤖 AI-Assisted Insights")
api_key = st.text_input("Enter your Gemini API Key to generate insights:", type="password")

if st.button("Generate Trend Analysis"):
    if api_key:
        try:

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            

            latest_premium = df['Premium_to_NAV'].iloc[-1]
            avg_premium = df['Premium_to_NAV'].mean()
            
            prompt = f"""
            You are an expert crypto financial analyst. 
            The current MicroStrategy (MSTR) Premium to NAV is {latest_premium:.2%}. 
            The 1-year average premium is {avg_premium:.2%}.
            Based on these numbers, provide a short, 3-sentence investment insight on what this means for Bitcoin (BTC) market sentiment.
            """
            
            response = model.generate_content(prompt)
            st.success("Analysis Generated!")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating insights: {e}")
    else:
        st.warning("Please enter an API key first.")