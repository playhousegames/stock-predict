from flask import Flask, render_template, request, jsonify
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from datetime import datetime
import requests
import os

app = Flask(__name__)

# Function to fetch and preprocess the stock data
def fetch_and_preprocess_stock_data(symbol):
    stock_data = yf.download(symbol, start='2010-01-01', end=datetime.today().strftime('%Y-%m-%d'))
    stock_data_cleaned = stock_data.dropna()
    return stock_data_cleaned

# Function to fetch the current stock price
def fetch_current_price(symbol):
    stock = yf.Ticker(symbol)
    todays_data = stock.history(period='1d')
    current_price = todays_data['Close'].iloc[0]
    return current_price

# Function to fetch yesterday's stock price
def fetch_yesterday_price(symbol):
    stock = yf.Ticker(symbol)
    stock_data = stock.history(period="5d")  # Fetch last 5 days of data
    yesterday_data = stock_data.iloc[-2]  # The second-to-last row corresponds to yesterday's price
    return yesterday_data['Close']

# Directly set your API key (not recommended for production)
API_KEY = "3JtDYjDf9Jvx0fscGz4a0IL7HKevl9Ha"

@app.route('/ticker-data', methods=['GET'])
def get_ticker_data():
    url = f"https://financialmodelingprep.com/api/v3/quote/AAPL,GOOGL,MSFT,AMZN,TSLA?apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for errors
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Define a route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Define a route for receiving stock symbol and returning predicted price
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    symbol = data['symbol']  # Extract stock symbol from request data
    stock_data_cleaned = fetch_and_preprocess_stock_data(symbol)

    # Use features directly from the stock data
    X = stock_data_cleaned[['Open', 'High', 'Low', 'Volume']]
    y = stock_data_cleaned['Close']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the model and train it
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict the stock price for today (most recent day in the dataset)
    predicted_price_today = model.predict([X.iloc[-1]])[0]

    # Prepare tomorrow's feature set by extrapolating from today's data
    tomorrow_features = X.iloc[-1].values.reshape(1, -1)  # Use the same features as today
    predicted_price_tomorrow = model.predict(tomorrow_features)[0]

    # Fetch the current stock price and yesterday's price
    current_price = fetch_current_price(symbol)
    yesterday_price = fetch_yesterday_price(symbol)

    # Return the predicted and actual prices as a response
    response = {
        'predicted_price_today': float(predicted_price_today),  # Today's predicted price
        'predicted_price_tomorrow': float(predicted_price_tomorrow),  # Tomorrow's predicted price
        'current_price': current_price,  # Today's actual price
        'yesterday_price': yesterday_price  # Yesterday's price
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
