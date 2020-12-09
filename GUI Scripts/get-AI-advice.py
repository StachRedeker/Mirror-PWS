import sys
import yfinance
import pickle
import os

from datetime import datetime, timedelta
import neat

input_ticker = sys.argv[1]

date = datetime.now()

stock = yfinance.download(tickers=input_ticker, start=(date - timedelta(days=32)), end=date, interval="1d")

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, "config-feedforward.txt")

config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,neat.DefaultStagnation, config_path)

def get_stock_value(stock_closes, day):
    cur_day = day
    result = None

    while result is None:
        result = stock_closes.get(
            "{0}-{1}-{2}".format(cur_day.year, cur_day.month, cur_day.day))
        cur_day -= timedelta(days=1)

    return result

def advice(neat_config, stock_data, day):
    genome = None
    with open(os.path.join(local_dir, "winner.pkl"), "rb") as f:
        genome = pickle.load(f)

    network = neat.nn.FeedForwardNetwork.create(genome, neat_config)

    closes = stock_data.get("Close")
    today_value = get_stock_value(closes, day)

    delta_1d = today_value - get_stock_value(closes, day - timedelta(days=1))
    delta_2d = today_value - get_stock_value(closes, day - timedelta(days=2))
    delta_5d = today_value - get_stock_value(closes, day - timedelta(days=5))
    delta_14d = today_value - get_stock_value(closes, day - timedelta(days=14))
    delta_31d = today_value - get_stock_value(closes, day - timedelta(days=31))

    output = network.activate((delta_1d, delta_2d, delta_5d, delta_14d, delta_31d))
    return output


advice = advice(config, stock, date)
print("Buy? (>0.5=yes) - " + str(advice[0]))

sys.stdout.flush()