css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 12%;
}
.chat-message .avatar img {
  max-width: 60px;
  max-height: 60px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 90%;
  padding: 0 .35rem;
  color: #fff;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://www.sideshow.com/storage/product-images/2171/c-3po_star-wars_square.jpg">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://resizing.flixster.com/ocuc8yjm8Fu5UK5Ze8lbdp58m9Y=/300x300/v2/https://flxt.tmsimg.com/assets/p11759522_i_h9_aa.jpg">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

import streamlit as st
import yfinance as yf
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_types import AgentType
import os
from dotenv import load_dotenv

os.environ['GOOGLE_API_KEY'] = 'AIzaSyDu9N0IvDky3_uZQeusrwPQ-LM2lvO4YMk'

def init_ses_states():
    st.session_state.setdefault('chat_history', [])


def relret(df):
    rel = df.pct_change()
    cumret = (1+rel).cumprod()-1
    cumret = cumret.fillna(0)
    return cumret


def display_convo():
    with st.container():
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            if i % 2 == 0:
                 st.markdown(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)
            else:
                st.markdown(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)


def main():
    st.title("Stock Price AI Bot :chart:")
    st.write(css, unsafe_allow_html=True)
    init_ses_states()
    st.caption("Visualizations and Gemini Chatbot for Multiple Stocks Over A Specified Period")


    with st.sidebar:
        asset_tickers = sorted(['DOW','NVDA','TSL','GOOGL','AMZN','AI','NIO','LCID','F','LYFY','AAPL', 'MSFT', 'BTC-USD', 'ETH-USD'])
        asset_dropdown = st.multiselect('Pick Assets:', asset_tickers)

        metric_tickers = ['Adj. Close', 'Relative Returns']
        metric_dropdown = st.selectbox("Metric", metric_tickers)

        viz_tickers = ['Line Chart', 'Area Chart']
        viz_dropdown = st.multiselect("Pick Charts:", viz_tickers)

        start = st.date_input('Start', value=pd.to_datetime('2023-01-01'))
        end = st.date_input('End', value=pd.to_datetime('today'))

        chatbot_temp = st.slider("Chat Bot Temperature",0.0,1.0,0.5)

        clear_button = st.button("Clear chat history")


    # Only when a stock is selected
    if clear_button:
        st.session_state.chat_history = []

    if len(asset_dropdown) > 0:
        df = yf.download(asset_dropdown,start,end)['Adj Close']
        if metric_dropdown == 'Relative Returns':
            df = relret(df)
        if len(viz_dropdown) > 0:
            with st.expander("Data Visualizations for {} of {}".format(metric_dropdown,asset_dropdown), expanded=True):
                if "Line Chart" in viz_dropdown:
                    st.subheader("Line Chart")
                    st.line_chart(df)
                if "Area Chart" in viz_dropdown:
                    st.subheader("Area Chart")
                    st.area_chart(df)
        st.header("Chat with your Data") 

        query = st.text_input("Enter a query:")

        chat_prompt = f'''
            You are an AI ChatBot intended to help with user stock data.
            \nYou have access to a pandas dataframe with the following specifications 
            \nDATA MODE: {metric_dropdown}
            \nSTOCKS: {asset_dropdown} 
            \nTIME PERIOD: {start} to {end}
            \nCHAT HISTORY: {st.session_state.chat_history}
            \nUSER MESSAGE: {query}
            \nAI RESPONSE HERE:
        '''

        if st.button("Execute") and query:
            with st.spinner('Generating response...'):
                try:
                    agent = create_pandas_dataframe_agent(
                        ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=chatbot_temp),
                        pd.DataFrame(df),
                        verbose=True
                    )

                    answer = agent.run(chat_prompt)
                    st.session_state.chat_history.append(f"USER: {query}\n")
                    st.session_state.chat_history.append(f"AI: {answer}\n")
                    display_convo()

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


def run_stock_analyzer():
    load_dotenv()
    main()

    