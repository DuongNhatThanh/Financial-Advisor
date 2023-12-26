import streamlit as st
import requests
from datetime import date, timedelta, datetime
import pytz
from datetime import time

tz_NY = pytz.timezone('America/New_York')
datetime_NY = datetime.now(tz_NY).time()

today = date.today()
yesterday = today - timedelta(days=1)

stock_dictionary = {'Apple, INC.': 'AAPL', 'Google': 'GOOGL', 'Microsoft': 'MSFT', 'Facebook': 'META', 'Amazon': 'AMZN',
                    'Samsung Electronics': 'SSNLF', 'Synopsys, INC.': 'SNPS', 'IBM': 'IBM', 'Tesla': 'TSLA',
                    'Intel Corporation': 'INTC'}

def main():
    st.title("Currency, Stock, and News App")
    
    # Sidebar with user input
    option = st.sidebar.selectbox('Choose an option:', ['Currency Converter', 'Stock Information', 'News Fetcher'])
    
    if option == 'Currency Converter':
        st.header('Currency Converter')
        in_curr = st.text_input('Input Currency', 'USD')
        quant = st.number_input('Amount', value=1.0)
        out_curr = st.text_input('Output Currency', 'EUR')
    
        if st.button('Convert'):
            url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={in_curr}&to_currency={out_curr}&apikey=OSO8WN3NV4T5VRQP'
            response = requests.get(url).json()
            con_fact = float(response['Realtime Currency Exchange Rate']['5. Exchange Rate'])
            final_amt = round(quant * con_fact, 2)
            st.success(f'{quant:,} {in_curr} is {final_amt:,} {out_curr}, Exchange rate: {con_fact}')
    
    elif option == 'Stock Information':
        st.header('Stock Information')
        company = st.selectbox('Select a company', list(stock_dictionary.keys()))
    
        if (datetime_NY <= time(16, 0, 0)) and (datetime_NY >= time(9, 30, 0)):
            url = f'https://realstonks.p.rapidapi.com/{stock_dictionary[company]}'
            headers = {
                "X-RapidAPI-Key": "a416be2db6msh637b1741a1e961fp1eac42jsnc85269cffde2",
                "X-RapidAPI-Host": "realstonks.p.rapidapi.com"
            }
            stock_response = requests.get(url, headers=headers).json()
            price = stock_response['price']
            change_point = stock_response['change_point']
            change_percentage = stock_response['change_percentage']
            total_vol = stock_response['total_vol']
            st.success(f'**Current Stock Statistics for {company}**')
            st.markdown(f'- **Price:** {price}')
            st.markdown(f'- **Change Point:** {change_point}')
            st.markdown(f'- **Change Percentage:** {change_percentage}')
            st.markdown(f'- **Total Volume:** {total_vol}')
    
    
        else:
            date_time = st.date_input('Select a date', today)
            dt = str(date_time)
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_dictionary[company]}&apikey=OSO8WN3NV4T5VRQP'
            stock_response = requests.get(url).json()
            stock_data = stock_response['Time Series (Daily)'][dt]
            opening = stock_data['1. open']
            high = stock_data['2. high']
            low = stock_data['3. low']
            closing = stock_data['4. close']
            volume = stock_data['5. volume']
            st.success(f'''Today's Stock Statistics for {company} on {str(today)} (All prices in USD)
                Opening Price: {opening}
                High Price: {high}
                Low Price: {low}
                Closing Price: {closing}
                Volume: {int(volume):,}''')
    
    elif option == 'News Fetcher':
        st.header('News Fetcher')
        company = st.text_input('Enter a company name', 'Google')
    
        url = f'https://newsapi.org/v2/everything?q={company}&from={str(yesterday)}&to={str(today)}&sortBy=popularity&apiKey=8580d08ca6e14b3882e3f40c3bb75aea'
        article_response = requests.get(url).json()
        news_article = ''
        for i in range(min(10, len(article_response['articles']))):
            title = article_response['articles'][i]['title']
            url = article_response['articles'][i]['url']
            news_article = news_article + f'{title}\n{url}\n\n'
    
        st.success(news_article)
