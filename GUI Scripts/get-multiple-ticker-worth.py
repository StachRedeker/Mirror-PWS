import sys
import yfinance as yf

input_tickers = sys.argv
input_tickers.pop(0)

for elem in input_tickers:
    ticker = yf.Ticker(elem)
    history = ticker.history(period="1d", interval="1m")

    i = -1
    while i < 1000:
        if history.get("Close")[i]:
            print("{0}|{1}".format(elem, history.get("Close")[i]))
            break
        else:
            i += 1

sys.stdout.flush()
