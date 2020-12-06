import sys
import yfinance as yf
import numpy
from datetime import datetime
from forex_python.converter import CurrencyRates, CurrencyCodes
from gui_utils import GUIUtils as Utils

input_ticker = Utils.decrypt(sys.argv[1])

ticker = yf.Ticker(input_ticker)

def formatClose(raw):
    if str(type(raw)) == "<class 'numpy.float64'>":
        return Utils.format_money_decimal(raw)
    else:
        return " "

def formatSplit(raw):
    try:
        return str(raw)
    except Exception:
        return "0.0"

def formatDividend(raw):
    try:
        return str(raw)
    except Exception:
        return "0.0"

def formatDate(raw, period):
    makeup = ["%b", "%d"]
    if period == "week":
        makeup = ["%a", "%h"]
    elif period == "max":
        makeup = ["%Y", "%b"]

    try:
        return datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("{0}-{1}".format(makeup[0], makeup[1]))
    except OSError:
        return "??-??"



# Week
history = ticker.history(period="5d", interval="30m")
dateArrRaw = list(history.index.values)
closeArr = []
splitArr = []
dividendsArr = []
for i in history.index:
    closeArr.append(formatClose(history.get("Close")[i]))
    splitArr.append(formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(formatDate(raw, "week"))

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
    closeArr.append(formatClose(history.get("Close")[i]))
    splitArr.append(formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(formatDate(raw, "month"))

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
    closeArr.append(formatClose(history.get("Close")[i]))
    splitArr.append(formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(formatDate(raw, "6months"))

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
    closeArr.append(formatClose(history.get("Close")[i]))
    splitArr.append(formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(formatDate(raw, "year"))

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
    closeArr.append(formatClose(history.get("Close")[i]))
    splitArr.append(formatSplit(history.get("Stock Splits")[i]))
    dividendsArr.append(formatDividend(history.get("Dividends")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(formatDate(raw, "max"))

print("|".join(dateArr))
print("|".join(closeArr))
print("|".join(splitArr))
print("|".join(dividendsArr))

sys.stdout.flush()