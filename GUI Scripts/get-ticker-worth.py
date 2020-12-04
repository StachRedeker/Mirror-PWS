import sys
import yfinance as yf

input_ticker = sys.argv[1]

ticker = yf.Ticker(input_ticker)
history = ticker.history(period="1d", interval="1m")

i = -1
while True:
    if history.get("Close")[i]:
        print(history.get("Close")[i])
        break
    else:
        i += 1

sys.stdout.flush()
