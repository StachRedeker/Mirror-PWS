import sys
import yfinance as yf
from utils import Utils

input_ticker = sys.argv[1]

ticker = yf.Ticker(input_ticker)

company_name = ticker.info['longName']
print(company_name)

history = ticker.history(period="2d")

price_last_close = history.get("Close")[0]
price_now = history.get("Close")[1]

print(Utils.format_money(price_now - price_last_close))

sys.stdout.flush()
