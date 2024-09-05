import yfinance as yf
import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)



def netProfitMarginCalculator(average):
    conditions_scores = [
        (average > 50, 25),
        (average > 40, 20),
        (average > 30, 15),
        (average > 20, 10),
        (average > 10, 5),
        (average > 0, 2),
        (average <= 0, -10)
    ]

    for condition, score in conditions_scores:
        if condition:
            return score

    return 0  # Default case if no conditions match
def priceToBookCalculator(ratio):
    conditions_scores = [

        (ratio > 40, -10),
        (ratio > 10, 0),
        (ratio > 5, 1),
        (ratio > 2, 5),
        (ratio > 1, 10),
        (ratio < 1, 20)
    ]

    for condition, score in conditions_scores:
        if condition:
            return score

    return 0  # Default case if no conditions match

def average_growthCalculetor(average):
    conditions_scores = [

        (average > 11, 15),
        (average > 10, 10),
        (average > 9, 9),

        (average > 8, 8),
        (average > 7, 7),
        (average > 6, 6),
        (average > 5, 5),
        (average > 4, 4),
        (average > 3, 3),
        (average > 2, 2),
        (average > 1, 1),
        (average < 0, -5)
    ]

    for condition, score in conditions_scores:
        if condition:
            return score

    return 0  # Default case if no conditions match


def check_financial_criteria(financials):
    score = 0
    required_keys = ['Total Revenue', 'Net Income']

    # Check if all required keys are present
    if not all(key in financials.columns for key in required_keys):
        return score

    income = financials['Total Revenue']
    net_profit = financials['Net Income']

    if len(income) < 4 or len(net_profit) < 4:
        return score

    # Check if the revenue has consistently increased
    if (income[0] > income[1] and income[1] > income[2] and income[2] > income[3]):
        score += 10

    # Check if the net profit is positive for the last three quarters
    if (net_profit[0] > 0 and net_profit[1] > 0 and net_profit[2] > 0):
        score += 20

    # Check if the net profit is consistently increased
    if (net_profit[0] > net_profit[1] and net_profit[1] > net_profit[2] and net_profit[2] > net_profit[3]):
        score += 5

    # Check if the revenue increasing in a high percent
    growth_percentages = []
    for i in range(0, 2):
        prev_month = income.iloc[i+1]
        current_month = income.iloc[i]
        if prev_month > 0:  # Avoid division by zero
            growth_percentage = ((current_month - prev_month) / prev_month) * 100
            growth_percentages.append(growth_percentage)
        else:
            growth_percentages.append(0)

    # Calculate the average growth percentage over the last 3 months
    average_growth = sum(growth_percentages) / len(growth_percentages)
    score+=average_growthCalculetor(average_growth)
    # Net Profit Margin
    sum_percentage = 0
    for i in range(3):
        if income[i] != 0:  # Avoid division by zero
            percentage = (net_profit[i] / income[i]) * 100
            sum_percentage += percentage

    average = sum_percentage / 3
    score += netProfitMarginCalculator(average)

    return score

def priceToBookRatio(ticker):
    pb_ratio = ticker.info.get('priceToBook')
    score=priceToBookCalculator(pb_ratio)
    return score


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form['ticker']
    stock = yf.Ticker(ticker)
    score = 0
    try:
        financials = stock.quarterly_financials.T
        score = check_financial_criteria(financials)
        score += priceToBookRatio(stock)
        result_message = f"Score for {ticker}: {score}"
        result_class = "success"
    except Exception as e:
        result_message = f"Error fetching data for {ticker}: {e}"
        result_class = "error"

    return render_template('result.html', result_message=result_message, result_class=result_class)



if __name__ == "__main__":
    app.run(debug=True)