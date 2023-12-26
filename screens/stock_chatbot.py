import plotly.graph_objs as go
import streamlit as st
import google.generativeai as genai
import os 
from src.financial_data import get_financial_data
from src.tickers import is_valid_ticker
import yfinance as yf
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI


# CSS styling
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

# Define user and bot templates
user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://resizing.flixster.com/ocuc8yjm8Fu5UK5Ze8lbdp58m9Y=/300x300/v2/https://flxt.tmsimg.com/assets/p11759522_i_h9_aa.jpg">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://www.sideshow.com/storage/product-images/2171/c-3po_star-wars_square.jpg">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''


os.environ["GOOGLE_API_KEY"] = 'AIzaSyCNIINGRv_N8mxjU6kmzuYh20ySYeTFZ-4'
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def plot_stock_data(ticker, data):
    trace = go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name=ticker,
    )

    layout = go.Layout(title=f"{ticker} Stock Data (3 Months)")
    fig = go.Figure(data=[trace], layout=layout)
    return fig

def get_financial_statements(ticker):
    # time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker = ticker.split(".")[0]
    else:
        ticker = ticker   
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1] >= 3:
        balance_sheet = balance_sheet.iloc[:, :3]  # Remove 4th years data
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    
    # cash_flow = company.cash_flow.to_string()
    # print(balance_sheet)
    # print(cash_flow)
    return balance_sheet

def get_company_name(ticker):
    stock_info = yf.Ticker(ticker)
    company_name = stock_info.info['longName']
    return company_name

    
def main2():
    # Add a title and description
    st.title("StockAI💸")
    st.markdown("Enter a stock ticker 📈 and chat with its financial data using Gemini Language Model 🧠.")
    
    
    # Get user input for the stock ticker
    ticker = st.text_input("Enter the stock ticker:")
    
    if ticker and is_valid_ticker(ticker):
        # Fetch and display financial data when the user clicks the button
        stock_financials = get_financial_statements(ticker)
        data, news, stock_data = get_financial_data(ticker)
        Company_name = get_company_name(ticker)
        available_information=f"Stock Financials: {stock_financials}\n\nStock News: {news}\n\nStock data: {data}"
    
        # Plot stock data
        stock_chart = plot_stock_data(ticker, stock_data)
        stock_chart.update_layout(width=1000, height=600)
        st.plotly_chart(stock_chart)
    
        # Define Satirical Template 
        sat_template = PromptTemplate(
            input_variables=['query', 'Company_name', 'available_information'],
            template="""
                Provide a detailed stock analysis for {Company_name} based on the available data. Assume the user is well-informed about investment risks. Avoid generic disclaimers. Imagine you are a professional financial advisor.
        
                Analyze the current financial status:
                {available_information}
        
                User Query: {query}
        
                Investment Analysis:
                1. **Financial Health:** Assess the company's financial statements for stability and growth.
                2. **News Impact:** Evaluate recent news and its potential impact on stock performance.
                3. **Technical Analysis:** Interpret the three-month stock chart for trends and patterns.
                4. **Risk Factors:** Identify potential risks affecting the stock.
                5. **Investment Recommendation:** Provide a balanced recommendation based on the analysis.
        
                Remember to consider both positive and negative aspects. Conclude with a clear and concise summary. Avoid boilerplate responses and ensure the analysis is tailored to the specific stock.
            """
        )

    
        # Memory
        sat_memory = ConversationBufferMemory(input_key='query', memory_key="chat_history")
    
        # Language Model
        llm = ChatGoogleGenerativeAI(model="gemini-pro",
                                 temperature=0.7)
    
        # Satirical Response Generation Chain
        gem_chain = LLMChain(llm=llm, prompt=sat_template, memory=sat_memory)

        # Define Generated and Past Chat Arrays
        if 'generated' not in st.session_state: 
            st.session_state['generated'] = []
    
        if 'past' not in st.session_state: 
            st.session_state['past'] = []

        # Clear history
        with st.sidebar:
            if st.button("Clear history"):
                st.session_state['generated'] = []
                st.session_state['past'] = []
            
        # Title and Description
        st.title("StockGemini")
        st.write("A Stock Advisor Chatbot using Gemini")
        st.write(css, unsafe_allow_html=True)
    
        # User input
        input_text = st.text_input('Enter message for StockGemini')
        if st.button('Send Message') and input_text:
            with st.spinner('Generating response...'):
                try:
                    # Generate satirical response
                    response = gem_chain.predict(query=input_text, Company_name=Company_name, available_information = available_information)
    
                    # Store conversation
                    st.session_state.past.append(input_text)
                    st.session_state.generated.append(response)
    
                    # Display conversation in reverse order
                    for i in range(len(st.session_state.past)):
                        st.write(user_template.replace("{{MSG}}",st.session_state.past[i] ), unsafe_allow_html=True)
                        st.write(bot_template.replace("{{MSG}}",st.session_state.generated[i] ), unsafe_allow_html=True)
                        st.write("")
    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")