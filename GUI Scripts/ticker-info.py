import sys
import yfinance as yf
from gui_utils import GUIUtils as Utils

input_ticker = Utils.decrypt(sys.argv[1])

ticker = yf.Ticker(input_ticker)

company_name = input_ticker.replace("^", "") + "-INDEX"
if "longName" in ticker.info:
    company_name = ticker.info['longName']

print(company_name)

history = ticker.history(period="2d")

price_last_close = history.get("Close")[0]
price_now = history.get("Close")[1]

print(Utils.format_money(price_now - price_last_close))

sys.stdout.flush()
