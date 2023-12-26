from screens.portfolio_optimization import portfolio_optimization
from screens.stock_analyzer import run_stock_analyzer
from screens.single_stock_analyse import main
from screens.stock_chatbot import main2
from utils.index import get_hash

def get_routes():
    screens = [
        
        {
            "component": portfolio_optimization,
            "name": "Portfolio Optimization",
            "icon": "currency-dollar"  
        },
        {
            "component": run_stock_analyzer,
            "name": "Multi Stock Analyzer",
            "icon": "coin"  
        },
        {
            "component": main,
            "name": "Single Stock Analyzer",
            "icon": "cash-coin"  
        },
        {
            "component": main2,
            "name": "Stock Chatbot",
            "icon": "piggy-bank"  
        },
    ]
    
    return get_hash(screens)
