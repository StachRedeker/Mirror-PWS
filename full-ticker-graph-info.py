import sys
import yfinance as yf
import numpy
from datetime import datetime
from forex_python.converter import CurrencyRates, CurrencyCodes
from utils import Utils

input_ticker = sys.argv[1]

ticker = yf.Ticker(input_ticker)

# Week
history = ticker.history(period="5d", interval="30m")
dateArrRaw = list(history.index.values)
closeArr = []
for i in history.index:
    closeArr.append(Utils.format_money(history.get("Close")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%H:%M"))

print("|".join(dateArr))
print("|".join(closeArr))

# Month
history = ticker.history(period="1mo", interval="1d")
dateArrRaw = list(history.index.values)
closeArr = []
for i in history.index:
    closeArr.append(Utils.format_money(history.get("Close")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%m:%d"))

print("|".join(dateArr))
print("|".join(closeArr))

# 6 Months
history = ticker.history(period="6mo", interval="1d")
dateArrRaw = list(history.index.values)
closeArr = []
for i in history.index:
    closeArr.append(Utils.format_money(history.get("Close")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%b-%d"))

print("|".join(dateArr))
print("|".join(closeArr))

# Year
history = ticker.history(period="1y", interval="5d")
dateArrRaw = list(history.index.values)
closeArr = []
for i in history.index:
    closeArr.append(Utils.format_money(history.get("Close")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%b-%d"))

print("|".join(dateArr))
print("|".join(closeArr))

# Max
history = ticker.history(period="max", interval="1mo")
dateArrRaw = list(history.index.values)
closeArr = []
for i in history.index:
    closeArr.append(Utils.format_money(history.get("Close")[i]))

dateArr = []
for raw in dateArrRaw:
    dateArr.append(datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("%Y-%b"))

print("|".join(dateArr))
print("|".join(closeArr))

sys.stdout.flush()