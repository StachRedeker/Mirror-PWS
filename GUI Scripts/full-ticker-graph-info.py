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
    closeArr.append(Utils.formatClose(history.get("Close")[i]))
    splitArr.append(Utils.formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(Utils.formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(Utils.formatDate(raw, "week"))

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
    closeArr.append(Utils.formatClose(history.get("Close")[i]))
    splitArr.append(Utils.formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(Utils.formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(Utils.formatDate(raw, "month"))

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
    closeArr.append(Utils.formatClose(history.get("Close")[i]))
    splitArr.append(Utils.formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(Utils.formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(Utils.formatDate(raw, "6months"))

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
    closeArr.append(Utils.formatClose(history.get("Close")[i]))
    splitArr.append(Utils.formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(Utils.formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(Utils.formatDate(raw, "year"))

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
    closeArr.append(Utils.formatClose(history.get("Close")[i]))
    splitArr.append(Utils.formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(Utils.formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(Utils.formatDate(raw, "max"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

sys.stdout.flush()