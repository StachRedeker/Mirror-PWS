import sys
import yfinance as yf
import numpy
from datetime import datetime
from forex_python.converter import CurrencyRates, CurrencyCodes
from gui_utils import GUIUtils as Utils

input_ticker = Utils.decrypt(sys.argv[1])

ticker = yf.Ticker(input_ticker)

# Week
history = ticker.history(period="5d", interval="30m")
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
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%a-%H"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

# Month
history = ticker.history(period="1mo", interval="1d")
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
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%m/%d"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

# 6 Months
history = ticker.history(period="6mo", interval="1d")
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
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%b-%d"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

# Year
history = ticker.history(period="1y", interval="5d")
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
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%b-%d"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

# Max
history = ticker.history(period="max", interval="1mo")
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
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%Y-%b"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

sys.stdout.flush()