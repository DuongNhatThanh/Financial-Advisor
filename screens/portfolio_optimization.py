import streamlit as st
import pandas as pd
import os
from src.client import PyOpt


# set os environment for backwards compatibility

def portfolio_optimization():
    os.environ["IS_STREAMLIT"] = "true"
    opt = PyOpt()
    
    
    st.title("Portfolio Optimisation")
    
    
    st.write(
        """
    
    This app optimises a portfolio of stocks based on the Sharpe Ratio and Volatility.
    
    Input your stocks names and the app will return the optimal portfolio weights.
    
    """
    )
    
    opt.period = st.selectbox(
        label="Select the data to look back on",
        options=["6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        index=1,
        help="As the granularity is set to daily, the minimum period is 6 months."
        + "\nThis may be changed in the future.",
    )
    
    opt.RFR = st.number_input(
        label="Risk Free Rate", value=2.0, help="Risk Free Rate in percent", format="%f"
    )
    
    
    stocks = st.text_input(
        label="Enter your stock tickers separated by a comma (,)" " Non case sensitive.",
        placeholder="voo, vwra.l, qqq, gbug, spbo",
        help="You might need to google for the ticker name.",
    )
    stocks_split = [s.strip() for s in stocks.split(",") if s.strip()]
    
    opt.add_stocks(stocks_split)
    if len(stocks_split) > 1:
        opt.maxweights = st.slider(
            label="Max weightage of each asset",
            min_value=100 / len(stocks_split),
            max_value=100.0,
            value=100.0,
            step=1.0,
            help="Max allocation per asset in percent",
        )
        if st.button("Optimise"):
            col1, col2 = st.columns(2)
            with col1:
                outputs = opt.run(method="fmin", minimize="sharpe")
                st.write("## OPTIMIZED SHARPE RATIO")
                st.write(f"Returns:\t {outputs['metrics'][0] * 100:.3f}%")
                st.write(f"Volatility:\t {outputs['metrics'][1]:.3f}")
                st.write(f"Sharpe Ratio:\t {outputs['metrics'][2]:.3f}")
                st.subheader("Weights:")
                st.dataframe(outputs["result"])
            with col2:
                outputs = opt.run(method="fmin", minimize="vol")
                st.write("## OPTIMIZED VOLATILITY")
                st.write(f"Returns:\t {outputs['metrics'][0] * 100:.3f}%")
                st.write(f"Volatility:\t {outputs['metrics'][1]:.3f}")
                st.write(f"Sharpe Ratio:\t {outputs['metrics'][2]:.3f}")
                st.subheader("Weights:")
                st.dataframe(outputs["result"])
    
    else:
        st.write("Add some stocks! 👆 You need more than one to optimise!")
    
    with st.expander("Issues"):
        st.write(
            """
        It doesn't seem to handle negative sharpe ratios well yet.
        """
        )