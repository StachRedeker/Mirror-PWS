import os
import yfinance as stocks
import math
import time
import signal
import sys

from utils import Utils

from enum import Enum


class InvestProgram:
    def __init__(self):
        self.run = True
        self.commands = Commands(self)

        self.raw_balance = float(0)
        #self.equities = {"MSFT": 1.0, "BTC-EUR": 0.005, "^AEX": 0.5, "TKWY.AS": 0.2, "GOLD": 0.01, "LTC-EUR": 2.152, "FSR": 5.0, "ETH-EUR": 0.1, "^DJI": 25.12}
        self.equities = dict()

    def start(self):
        while self.run:
            self.commandloop()

    def get_raw_balance(self):
        return self.raw_balance

    def get_balance(self, verbose=False):
        if verbose:
            print("Loading balance...")

        total_balance = self.get_raw_balance()

        if len(self.equities) >= 1:
            data = stocks.download(tickers=" ".join(self.equities.keys()),
                                   group_by='ticker', progress=verbose, period="1d", interval="1m")

            index = 0
            for ticker_name in self.equities.keys():
                if len(self.equities.keys()) > 1:
                    close = list(data.get(ticker_name).get("Close"))
                else:
                    close = list(data.get("Close"))

                lastcost = math.nan
                attempt = 0
                while math.isnan(lastcost):
                    attempt = attempt + 1
                    lastcost = close[len(close)-attempt]

                equity_value = float(lastcost) * float(self.equities.get(ticker_name))

                if verbose:
                    prefix = None
                    if index == 0:
                        prefix = "\u250F  "  # ┏
                    elif index == len(self.equities.keys())-1:
                        prefix = "\u2517  "  # ┗
                    else:
                        prefix = "\u2523  "  # ┣

                    left_side = prefix + "{0}: {1} x{2} ".format(ticker_name, Utils.format_money(lastcost), self.equities.get(ticker_name))
                    print((left_side + (" "*(35-len(left_side))) + "=   {0}").format(Utils.format_money(equity_value)))

                total_balance = total_balance + equity_value
                index = index + 1

        return total_balance

    def commandloop(self):
        command_raw = input("Enter a command. ('help' for a list of commands)\n» ")
        command_split = command_raw.split(" ")
        command_name = command_split[0].lower()

        arguments = command_split.copy()
        arguments.pop(0)

        if command_name in ["balance", "bal"]:
            self.commands.balance(arguments)
            return
        elif command_name in ["setbalance", "setbal"]:
            self.commands.setbalance(arguments)
            return
        elif command_name in ["modbalance", "modbal"]:
            self.commands.modbalance(arguments)
            return
        elif command_name in ["quit", "stop", "exit"]:
            self.commands.quit(arguments)
            return
        elif command_name in ["help"]:
            self.commands.help(arguments)
            return
        elif command_name in ["buy", "b"]:
            self.commands.buy(arguments)
            return
        else:
            Utils.unknown_command(command_name)
            return


class Commands:
    def __init__(self, program):
        self.program = program

    def quit(self, arguments):
        self.program.run = False
        print("Goodbye!")

    def help(self, arguments):
        print("\nAvailable commands:")
        print("- help | View this list of commands.")
        print("- balance | View your total balance.")
        print("- setbalance <amount> | Set your balance")
        print("- modbalance <amount> | Modify your balance (positive/negative)")
        print("- buy <stock> <amount> <\'money\'/\'count\'> | Buy a stock")
        print("<...>: required, [...]: optional\n")

    def balance(self, arguments):
        print("Balance: " + Utils.format_money(self.program.get_raw_balance()) + " (or " + Utils.format_money(
            self.program.get_balance(True)) + " with equities)")

    def setbalance(self, arguments):
        if len(arguments) >= 1:
            try:
                newbalance = int(arguments[0])
                self.program.raw_balance = newbalance
                print("Changed balance to " + Utils.format_money(self.program.raw_balance))
            except ValueError:
                print("Error: <amount> must be a number.")
        else:
            print("Usage: setbalance <amount>")

    def modbalance(self, arguments):
        if len(arguments) >= 1:
            try:
                balancediff = int(arguments[0])
                self.program.raw_balance = self.program.raw_balance + balancediff
                print("Modified balance by " + Utils.format_money(balancediff) + ".")
                print("New balance " + Utils.format_money(self.program.get_raw_balance()) + ".")
            except ValueError:
                print("Error: <amount> must be a number.")
        else:
            print("Usage: modbalance <amount>")

    def buy(self, arguments):
        # buy <stock> <amount> <\'money\'/\'count\'> | Buy a stock
        if len(arguments) >= 3:
            stock_name = arguments[0].upper()
            input_amt = arguments[1]
            option = arguments[2]

            if option in ["money", "count"]:
                try:
                    input_amt = float(int(input_amt))
                except ValueError:
                    print("Error: <amount> must be a number.")
                    return

                info = Utils.get_market_info(stock_name)

                if info is not None:
                    history = stocks.Ticker(stock_name).history("1d", "1m")
                    close = history.get("Close")
                    lastcost = math.nan
                    attempt = 0

                    while math.isnan(lastcost):
                        attempt = attempt + 1
                        lastcost = close[len(close) - attempt]

                    amount = 0.0

                    if option == "money":
                        amount = input_amt / float(lastcost)
                        pass
                    elif option == "count":
                        amount = input_amt
                        pass

                    amount = float('{:.4f}'.format(amount))

                    if amount < 0:
                        print("Error: amount must be at least 0.0001")
                        return

                    cost = float('{:.2f}'.format(amount * lastcost))

                    if cost <= self.program.raw_balance:
                        self.program.raw_balance = self.program.raw_balance - cost

                        if stock_name in self.program.equities:
                            self.program.equities[stock_name] = self.program.equities[stock_name] + amount
                        else:
                            self.program.equities[stock_name] = amount

                        print("Bought {0}x {1} for {2}".format(amount, stock_name, Utils.format_money(cost)))
                    else:
                        print("You can not afford this transaction. (cost = {0}, you have {1})".format(Utils.format_money(cost), Utils.format_money(self.program.get_raw_balance())))
                else:
                    print("That ticker could not be recognised. Is it spelt correctly?")
            else:
                print("Error: purchasing method must be 'money' or 'count'.")

            pass
        else:
            print("Usage: buy <stock> <amount> <\'money\'/\'count\'>")