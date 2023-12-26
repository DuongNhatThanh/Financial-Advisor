import os
import google.generativeai as genai
from IPython.display import Markdown
# Gemini API key
os.environ["GOOGLE_API_KEY"] = 'AIzaSyAdsfh9ZSfbNmRt6vRlkALLpqax4UxRcwk'
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def summarize_financial_data(news, ticker):
    prompt = f'News of {ticker}: "{news}"\nIs {ticker} a buy at the moment? Here\'s the summary:\n'
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return Markdown(response.text)