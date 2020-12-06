import sys
from forex_python.converter import CurrencyRates
from gui_utils import GUIUtils as Utils
import yfinance as yf

input_ticker = sys.argv[1]

ticker = yf.Ticker(input_ticker)
history = ticker.history(period="1d", interval="1m")

rates = CurrencyRates()

i = -1
while i < 1000:
    if history.get("Close")[i]:
        worth = history.get("Close")[i]
        print(worth)

        print(Utils.format_money(rates.convert(ticker.info["currency"], "EUR", worth)))
        break
    else:
        i += 1

sys.stdout.flush()
