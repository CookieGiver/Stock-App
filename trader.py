import json
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from bokeh.embed import components
from bokeh.plotting import figure
import random
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
from pytz import timezone


def fetch_stock_data(ticker, time_frame):
    '''
    *Fetches Stock data using the yfinance python package and 
    returns information regarding historical stock data and 
    metadata about the company
    
    Parameters:
    - ticker: stock ticker name (str)
    - time_frame: the length of time to fetch the data (str)
    
    Output:
    - stock_data: a pandas dataframe with historical stock data
        with date as the index. Includes EPS
    - info: info about the company (dict), E.g. revenue, price, name, etc.
    '''
    
    stock = yf.Ticker(ticker)
    
    hist = stock.history(period=time_frame)
    info = stock.info
    hist['Change'] = hist['Close'] - hist['Open']
    quarterly_financials = stock.quarterly_financials

    stock_data = hist[['Open', 'High', 'Low', 'Close', 'Change', 'Volume']].copy()
    stock_data['EPS'] = 0


    for i in range(len(stock_data)):
        cols = quarterly_financials.columns
        tz_aware_cols = cols.tz_localize('America/New_York')

        for j, col in enumerate(cols):
            if j == 0:
                if stock_data.index[i] > tz_aware_cols[j]:
                    stock_data.iloc[i, 6] = quarterly_financials.loc['Diluted EPS', col]
                    break
            elif j == len(cols) - 1:
                if stock_data.index[i] < tz_aware_cols[j]:
                    stock_data.iloc[i, 6] = quarterly_financials.loc['Diluted EPS', col]
                    break
            else:
                if stock_data.index[i] < tz_aware_cols[j] and stock_data.index[i] > tz_aware_cols[j+1]:
                    stock_data.iloc[i, 6] = quarterly_financials.loc['Diluted EPS', col]
                    break
    
    stock_data['Date'] = hist.index.to_series().dt.strftime('%Y-%m-%d')
    return stock_data, info


app = Flask(__name__)

@app.route('/')
def index():
    '''
    *flask function that routes the home/index url at "/"
    
    Output:
    - renders the index.html file with jinja2 templating
    '''
    return render_template('index.html')

@app.route('/stock-tracker/', methods = ['GET'])
def stock_tracker():
    '''
    *flask function that routes the url at "/stock-tracker/"
    only permits GET requests. Obtains information on a specific
    ticker, the default is Microsoft (MSFT) over a 2y period
    and sends the data to the jinja2 templating engine to be
    rendered in javascript on the webpage
    
    Output:
    - renders the stock_tracker.html file with jinja2 templating
    '''
    ticker = "MSFT"
    info = yf.Ticker(ticker).info
    data = fetch_stock_data(ticker, '2y')
    labels = list(data['Date'])
    values = list(data['Open'])
    
    return render_template('stock_tracker.html', labels=labels, data=values, ticker=ticker, info=info)

@app.route('/stock-tracker/', methods = ['POST'])
def stockSearch():
    '''
    *flask function that routes the url at "/stock-tracker/"
    only permits POST requests. Obtains information on the
    requeseted ticker over a 2y period and sends the data 
    to the jinja2 templating engine to be rendered in 
    javascript on the webpage
    
    Input:
    - requests form containing information regarding the desired 
        ticker
    
    Output:
    - renders the stock_tracker.html file with jinja2 templating
    '''
    data = request.form
    ticker = data['ticker']
    info = yf.Ticker(ticker).info
    data = fetch_stock_data(ticker, "2y")
    labels = list(data['Date'])
    values = list(data['Open'])
    
    return render_template('stock_tracker.html', labels=labels, data=values, ticker=ticker, info=info)

@app.route('/about/')
def about():
    '''
    *flask function that routes the about page url at "/about/"
    
    Output:
    - renders the about.html file with jinja2 templating
    '''
    return render_template('about.html')

@app.route('/portfolio/', methods = ['GET'])
def porfolio():
    '''
    *flask function that routes the portfolio page url at "/portfolio/"
    
    Output:
    - renders the portfolio.html file with jinja2 templating with
        blank data
    '''
    return render_template('portfolio.html', labels=[], data=[], tickers=[])

@app.route('/portfolio/', methods = ['POST'])
def portfolioSimulate():
    '''
    *flask function that routes the portfolio page url at "/portfolio/"
    obtains h istorical stock data for each of the tickers passed via
    the request form and the corresponding ammounts. It then creates
    a pandas df with historical data for each stock beginning at the
    desired date specified in the form. Also passes information on 
    each company.
    
    Output:
    - renders the portfolio.html file with jinja2 templating with
        labels, data, the tickers, the start date, and current date
    '''
    data = request.form
    hist_data = []
    tickers = []
    positions = []
    information = []
    date = datetime.strptime(data['startDateInput'], "%Y-%m-%d")
    date = date.astimezone(timezone('UTC'))
    for key, value in data.items():
        if 'ticker' in key:
            num = key.split('r')[1]
            tickers.append(value)
            hist, info = fetch_stock_data(value, '5y')
            labels = list(hist['Date'][hist.index > date])
            hist = hist['Open'][hist.index > date]
            for key, value in data.items():
                if key == 'ammount' + num:
                    position = float(value) / hist[0]
                    positions.append(position)
            info['position'] = position
            information.append(info)
            hist_data.append(list(hist*position))
    positions.append(sum(positions))
    tickers.append("Total")
    hist_data.append([sum([table[i] for table in hist_data]) for i in range(len(hist_data[0]))])
    
    return render_template('portfolio.html', labels=labels, data=hist_data, tickers=tickers, positions=positions, start_date=data['startDateInput'], today=datetime.strftime(datetime.today(), "%Y-%m-%d"), information=information)
