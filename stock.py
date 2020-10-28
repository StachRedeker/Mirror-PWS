import yfinance as stocks
import time
import signal
import sys

class Utils:
    @staticmethod
    def formatValue(value):
        formatted = str(round(value, 2))
        if len(formatted.split(".")[1]) < 2:
            formatted = formatted + "0"
        return formatted

    @staticmethod
    def getMarketInformation(naam):
        try:
            return stocks.Ticker(naam).info
        except:
            return None


class StockProgram:
    # Waardes initialiseren
    def __init__(self):
        self.run = True

        # Voor de 'watch'-functie
        self.watching_tick = None
        self.watching_name = None
        self.watching_info = None
        self.watching_last_update = time.time()
        self.watching_last_price = "0.00"

        # Instellingen
        self.watching_log = False

        signal.signal(signal.SIGINT, self.signal_handler)

    def reset_watching(self):
        self.watching_tick = None
        self.watching_name = None
        self.watching_info = None
        self.watching_last_update = time.time()
        self.watching_last_price = "0.00"

    # Het programma wordt geactiveerd als dit runt.
    def start(self):
        while self.run:
            if self.watching_tick is not None:
                if time.time() - self.watching_last_update >= 5.0:
                    self.watching_last_update = self.watching_last_update + 100
                    self.watchedloop()
            else:
                self.commandloop()

    def watchedloop(self):
        # De geschiedenis van de prijs van de afgelopen 2 dagen.
        history = self.watching_tick.history(period="2d")

        price_last_close = Utils.formatValue(history.get("Close")[0])
        price_now = Utils.formatValue(history.get("Close")[1])

        price_last_close_f = float(price_last_close)
        price_now_f = float(price_now)
        price_old_f = float(self.watching_last_price)

        diff_prev = "~"
        if price_now_f > price_old_f:
            diff_prev = "+" + Utils.formatValue(price_now_f - price_old_f)
        elif price_old_f > price_now_f:
            diff_prev = "-" + Utils.formatValue(price_old_f - price_now_f)

        diff_close = "~"
        if price_last_close_f > price_now_f:
            diff_close = "-" + Utils.formatValue(price_last_close_f - price_now_f)
        elif price_now_f > price_last_close_f:
            diff_close = "+" + Utils.formatValue(price_now_f - price_last_close_f)

        if not self.watching_log:
            print(
                "Current value " + self.watching_name + ": " + price_now + " (" + diff_prev + " | " + diff_close + ")" +
                (" "*8), end="\r", flush=True)
        else:
            print(
                "Current value " + self.watching_name + ": " + price_now + " (" + diff_prev + " | " + diff_close + ")")

        self.watching_last_update = time.time()
        self.watching_last_price = price_now

    def command_info(self, name):
        stock_info = Utils.getMarketInformation(name)

        if stock_info is not None:
            # De markt bestaat
            titel = "================= Information " + name + " ================="
            print("\n" + titel + "\n")
            if "longName" in stock_info:
                print(" " + stock_info["longName"] + " is a company in the " + stock_info["sector"] + " sector.")
                print(" It has an estimated amount of " + str(stock_info["fullTimeEmployees"]) + " full-time employees.")
            print(" At this time, one share is worth " + Utils.formatValue(
                stocks.Ticker(name).history(period="1d").get("Close")[0]) + " " + stock_info["currency"] + ".")
            print("\n" + ("=" * len(titel)) + "\n")
        else:
            # De markt bestaat niet.
            print("That ticker could not be recognised. Is it spelt correctly?")

    def commandloop(self):
        command_raw = input("Enter a command. ('help' for a list of commands)\n» ")
        command_split = command_raw.split(" ")
        command_name = command_split[0].lower()

        arguments = command_split.copy()
        arguments.pop(0)

        if command_name == "info":
            if len(arguments) > 0:
                stock_name = arguments[0].upper()

                print("Fetching information about " + stock_name + "...")
                self.command_info(stock_name)
                return
            else:
                print("Usage: info <ticker>")
                return
        elif command_name == "watch":
            if len(arguments) > 0:
                stock_name = arguments[0].upper()

                print("Fetching information about " + stock_name + "...")

                stock_info = Utils.getMarketInformation(stock_name)

                if stock_info is not None:
                    name = stock_name
                    if "longName" in stock_info:
                        name = stock_info["longName"]

                    print("You are now watching " + name + ". (price in " + stock_info["currency"] + ")")
                    self.watching_tick = stocks.Ticker(stock_name)
                    self.watching_name = stock_name
                    self.watching_info = stock_info
                    self.watching_last_price = "0.00"
                else:
                    print("That ticker could not be recognised. Is it spelt correctly?")
                return
            else:
                print("Usage: watch <ticker>")
                return
        elif command_name == "watchlog":
            if self.watching_log:
                self.watching_log = False
                print("Toggled logging style to a single line.")
            else:
                self.watching_log = True
                print("Toggled logging style to multiple lines.")
        elif command_name == "quit" or command_name == "stop" or command_name == "exit":
            self.run = False
            print("Goodbye!")
            return
        elif command_name == "help":
            print("\nAvailable commands:")
            print("- help | View this list of commands.")
            print("- info <ticker> | View the information about a certain stock.")
            print("- watch <ticker> | Watch a stock's price. Updates every 5 seconds.")
            print("- watchlog | Toggles the logging style of the watch feature.")
            print("- stop,quit,exit | Stop the program.")
            print("<...>: required, [...]: optional\n")
            return
        else:
            print("The command \"" + command_name + "\" could not be recognised. Type \"help\" for a list of "
                                                                  "commands.\n")

    def signal_handler(self, sig, frame):
        if self.watching_tick is not None:
            self.reset_watching()
            print("\nCancelled watching.\n")
        else:
            print("Goodbye!")
            sys.exit(0)

StockProgram().start()