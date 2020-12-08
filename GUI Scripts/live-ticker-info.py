import sys
from forex_python.converter import CurrencyCodes, CurrencyRates
from datetime import datetime
from gui_utils import GUIUtils as Utils
import yfinance as yf

input_ticker = sys.argv[1]

ticker = yf.Ticker(input_ticker)
history = ticker.history(period="1d", interval="1m")

rates = CurrencyRates()
codes = CurrencyCodes()

i = -1
while i < 1000:
    if history.get("Close")[i]:
        worth = history.get("Close")[i]
        print(Utils.format_money(worth))

        # Symbol
        print("|".join([str(ord(char)) for char in codes.get_symbol(ticker.info["currency"])]))
        # Converted
        print(Utils.format_money(rates.convert(ticker.info["currency"], "EUR", worth)))
        break
    else:
        i += 1


# Graph
history = ticker.history(period="1d", interval="1m")
dateArrRaw = list(history.index.values)
closeArr = []
splitArr = []
dividendsArr = []
for i in history.index:
    closeArr.append(Utils.formatClose(history.get("Close")[i]))
    splitArr.append(Utils.formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(Utils.formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(Utils.formatDate(raw, "day"))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%H:%M"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))



sys.stdout.flush()