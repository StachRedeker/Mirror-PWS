import sys
import json
import yfinance as yf
import numpy
from datetime import datetime
import pytz
from forex_python.converter import CurrencyRates, CurrencyCodes
from gui_utils import GUIUtils as Utils

input_ticker = sys.argv[1]

ticker = yf.Ticker(input_ticker)

company_name = ticker.info["longName"]
print(company_name)

# Value
history = ticker.history(period="1d")
value = history.get("Close")[0]
print(Utils.format_money(value))

# Value Symbol & Converted
rates = CurrencyRates()
codes = CurrencyCodes()
print(codes.get_symbol(ticker.info["currency"]))
print(Utils.format_money(rates.convert(ticker.info["currency"], "EUR", value)))

# Local Time
timezone = pytz.timezone(ticker.info["exchangeTimezoneName"])
print(datetime.now(timezone).strftime("%d %B %Y"))
print(datetime.now(timezone).strftime("%z").replace("0", ""))

# Graph
history = ticker.history(period="1d", interval="1m")
dateArrRaw = list(history.index.values)
closeArr = []
splitArr = []
dividendsArr = []
for i in history.index:
    closeArr.append(Utils.format_money_decimal(history.get("Close")[i]))
    splitArr.append(str(history.get("Stock Splits")[i]))
    dividendsArr.append(str(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%H:%M"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

sys.stdout.flush()
