import os
import pickle
from datetime import datetime, timedelta

import xlsxwriter

import random
import yfinance as stocks
import math
import time
import signal
import sys

from matplotlib import pyplot as plt
from matplotlib import ticker as pltticker

import neat

from utils import Utils

from enum import Enum


class Trader:
    def __init__(self, balance):
        self.balance = balance
        self.equities = dict()

    def get_total_balance(self):
        return self.balance


class VirtualMarket:
    def __init__(self, startdate, enddate, ticker="MSFT"):
        self.market_info = stocks.download(tickers=ticker, group_by='ticker', progress=True,
                                           start=(startdate - timedelta(days=32)), end=(enddate + timedelta(days=2)),
                                           interval="1d")
        self.today = startdate
        self.startdate = startdate
        self.enddate = enddate
        self.ticker = ticker

        last_valid = 0
        for i, price in enumerate(self.market_info.get("Close")):
            if price == math.nan or price is None:
                self.market_info.get("Close")[i] = last_valid
                continue
            last_valid = price

        print(self.market_info)

    def tick_day(self):
        # print(self.market_info.get("BTC-EUR").get("Close").get(
        #     "{0}-{1}-{2}".format(self.get_today().year, self.get_today().month, self.get_today().day)))
        pass

    def get_day_value(self, d):
        current = None
        current_date = d
        while current is None or current == math.nan:
            current = self.market_info.get("Close").get(
                "{0}-{1}-{2}".format(current_date.year, current_date.month, current_date.day))
            current_date -= timedelta(days=1)

        return current

    def get_today(self):
        return self.today

    def get_yesterday(self):
        return self.today - timedelta(days=1)

    def get_tomorrow(self):
        return self.today + timedelta(days=1)

    def get_value(self, day, stock):
        return self.market_info

    def increment_day(self):
        self.today += timedelta(days=1)

    def decrease_day(self):
        self.today -= timedelta(days=1)

    def get_ticker(self):
        return self.ticker

    def reset(self):
        self.today = self.startdate


START_BALANCE = 5000

date = datetime.now()
market = VirtualMarket(date - timedelta(days=366), date, "RYDAF")

markets = []

GENERATION = 0


def main(genomes, config):
    global GENERATION
    global market

    solo = len(genomes) == 1
    actions = []
    money = []
    values = []

    if not solo:
        if GENERATION > 0 and GENERATION % 100 == 0:
            index = int(GENERATION / 100)
            market = markets[index]
            print("Updated market.")

    GENERATION += 1

    market.reset()

    networks = []
    ge = []
    traders = []

    for _, genome in genomes:
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(network)

        traders.append(Trader(START_BALANCE))

        genome.fitness = 0
        ge.append(genome)

    run = True

    while run:
        # Stuur een signaal dat het een nieuwe dag is, voer de code uit...
        market.tick_day()
        # ...en dan naar de volgende dag.
        market.increment_day()

        today = market.get_today()
        today_value = market.get_day_value(today)
        tomorrow_value = market.get_day_value(market.get_tomorrow())

        delta_1d = today_value - market.get_day_value(market.get_yesterday())
        delta_2d = today_value - market.get_day_value(today - timedelta(days=2))
        delta_5d = today_value - market.get_day_value(today - timedelta(days=5))
        delta_14d = today_value - market.get_day_value(today - timedelta(days=14))
        delta_31d = today_value - market.get_day_value(today - timedelta(days=31))

        for i, trader in enumerate(traders):
            output = networks[i].activate((delta_1d, delta_2d, delta_5d, delta_14d, delta_31d))
            # traders[i].balance -= 2

            if solo:
                money.append([market.get_today(), traders[i].balance])
                values.append(today_value)

            amount500 = (500 / today_value)
            amount100 = (100 / today_value)

            if output[0] >= 0.5:
                # Hij kiest om 500$ te kopen voor 1 dag
                traders[i].balance += amount500 * (tomorrow_value - today_value)
                if solo:
                    actions.append("BUY500")
            elif output[1] >= 0.5:
                # Hij kiest om voor 100$ te kopen voor 1 dag
                traders[i].balance += amount100 * (tomorrow_value - today_value)
                if solo:
                    actions.append("BUY100")
            else:
                if solo:
                    actions.append("NOTHING")

            if trader.get_total_balance() <= 0:
                ge[i].fitness = -99999999
                ge.pop(i)
                traders.pop(i)
                networks.pop(i)
                continue

            # if trader.get_total_balance() > START_BALANCE:
            #     ge[i].fitness += (math.floor((0.1 * trader.get_total_balance()/START_BALANCE)*100)/100)
            # elif trader.get_total_balance() == START_BALANCE:
            #     pass
            # else:
            #    ge[i].fitness -= 5

            ge[i].fitness = (trader.get_total_balance() / 100) ** 3

        # Was dit de laatste dag? Dan is het nu tijd om te stoppen.
        if market.today >= market.enddate:
            run = False
            break

    best = -1
    best_bal = -1
    worst = 99999999999999999999999
    worst_bal = 99999999999999999999999
    for i, trader in enumerate(traders):
        if trader.get_total_balance() == START_BALANCE:
            ge[i].fitness = -1
            traders.pop(i)
            ge.pop(i)
            networks.pop(i)
            continue
        if trader.get_total_balance() > best_bal:
            best = i
            best_bal = trader.get_total_balance()
        if trader.get_total_balance() < worst_bal:
            worst = i
            worst_bal = trader.get_total_balance()

    # ge[best].fitness += 1000
    # ge[worst].fitness -= 1000
    print("Best: {0} with ${1}".format(best, Utils.format_money(best_bal)))
    print("Worst: {0} with ${1}".format(worst, Utils.format_money(worst_bal)))

    if solo:
        print(money)
        print(actions)

        dates = []
        moneyz = []
        percentages = []
        percentages_stock = []

        for pair in money:
            dates.append(pair[0])
            moneyz.append(pair[1])
            percentages.append((math.floor((pair[1] / START_BALANCE * 100) * 100) / 100 - 100))

        stock_start = market.get_day_value(market.startdate)

        for date in dates:
            if date < market.startdate:
                continue

            percentages_stock.append((math.floor((market.get_day_value(date) / stock_start * 100) * 100) / 100 - 100))

        graph(dates, moneyz, "balance")
        graph(dates, percentages, "percentage", dates, percentages_stock)

        if not excel(dates, moneyz, "balance"):
            print("Error in generating xlsx file for balances.")
        if not excel(dates, percentages, "percentage"):
            print("Error in generating xlsx file for percentages.")


def excel(dates, values, tag):
    if not len(dates) == len(values):
        return False

    workbook = xlsxwriter.Workbook("graphs/winner_" + tag + "_" + market.get_ticker() + ".xlsx")
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    worksheet.write("A1", "Dates", bold)
    worksheet.write("B1", tag, bold)

    for i, date in enumerate(dates):
        worksheet.write("A" + str(i + 2), str(date.day) + "/" + str(date.month) + "/" + str(date.year))
        worksheet.write_number("B" + str(i + 2), values[i])

    workbook.close()
    return True


def advice(winner_genome, neat_config, stock_data, day):
    network = neat.nn.FeedForwardNetwork.create(winner_genome, neat_config)

    closes = stock_data.get("Close")
    today_value = get_stock_value(closes, day)

    delta_1d = today_value - get_stock_value(closes, day - timedelta(days=1))
    delta_2d = today_value - get_stock_value(closes, day - timedelta(days=2))
    delta_5d = today_value - get_stock_value(closes, day - timedelta(days=5))
    delta_14d = today_value - get_stock_value(closes, day - timedelta(days=14))
    delta_31d = today_value - get_stock_value(closes, day - timedelta(days=31))

    output = network.activate((delta_1d, delta_2d, delta_5d, delta_14d, delta_31d))
    return output


def get_stock_value(stock_closes, day):
    cur_day = day
    result = None

    while result is None:
        result = stock_closes.get(
            "{0}-{1}-{2}".format(cur_day.year, cur_day.month, cur_day.day))
        cur_day -= timedelta(days=1)

    return result


def graph(x, y, tag, x2=None, y2=None):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    plt.subplots_adjust(bottom=0.15)

    ax.set_title("Trader's balance over time (" + tag + ")")

    fig.set_size_inches(18.5, 10.5)
    ax.plot_date(x, y, marker='', linestyle='-')

    if x2 is not None and y2 is not None:
        ax.plot_date(x2, y2, marker='', linestyle='-')

    ax.xaxis.set_major_locator(pltticker.MultipleLocator(5))

    save_dir = "graphs/winner_" + tag + "_" + market.get_ticker() + ".png"

    if not os.path.isdir("graphs"):
        os.makedirs("graphs")

    fig.autofmt_xdate()

    plt.show()

    res = fig.savefig(save_dir)

    if res is None:
        file_path = os.path.realpath(__file__).split("\\")
        file_path.pop()
        print("\nGraph generated at \"{0}\"".format("/".join(file_path) + "/" + save_dir))
    else:
        print("An error occurred while generating the graph. Please try again. (" + str(
            res) + ")")

    plt.close(fig)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(main, 1500)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()


def replay_genome(config_path, tck, genome_path="winner.pkl"):
    global market

    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    market = VirtualMarket(date - timedelta(days=366), date, tck)
    main(genomes, config)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    inp = input("Command (rerun or advice, leave empty to train)» \n")
    if inp.split(" ")[0] == "rerun":
        print("Rerun of winner for {0}:".format(inp.split(" ")[1]))
        replay_genome(config_path, inp.split(" ")[1])
    elif inp.split(" ")[0] == "advice":
        stock_name = inp.split(" ")[1]
        print("Getting advice from winner.pkl for " + stock_name + "...")

        with open("winner.pkl", "rb") as f:
            genome = pickle.load(f)

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                    neat.DefaultStagnation, config_path)

        stock = stocks.download(tickers=stock_name, start=(date - timedelta(days=32)), end=date, interval="1d", progress=True)

        advice = advice(genome, config, stock, date)
        print("Buy? (>0.5=yes) - " + str(advice[0]))
    else:
        markets = [
            VirtualMarket(date - timedelta(days=366), date, "KLMR"),
            VirtualMarket(date - timedelta(days=366), date, "RYDAF"),
            VirtualMarket(date - timedelta(days=366), date, "BP"),
            VirtualMarket(date - timedelta(days=731), date - timedelta(days=366), "GOOG"),
            VirtualMarket(date - timedelta(days=366), date, "FSR"),
            VirtualMarket(date - timedelta(days=366), date, "GOLD"),
            VirtualMarket(date - timedelta(days=731), date, "TSLA"),
            VirtualMarket(date - timedelta(days=366), date, "AMZN"),
            VirtualMarket(date - timedelta(days=366), date, "SI=F"),
            VirtualMarket(date - timedelta(days=366), date, "CL=F"),
            VirtualMarket(date - timedelta(days=366), date, "XRP-USD"),
            VirtualMarket(date - timedelta(days=366), date, "KLMR"),
            VirtualMarket(date - timedelta(days=366), date, "BCH-USD"),
            VirtualMarket(date - timedelta(days=366), date, "LTC-USD"),
            VirtualMarket(date - timedelta(days=366), date, "RYDAF"),
        ]
        run(config_path)
