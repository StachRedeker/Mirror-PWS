import yfinance as stocks


class Utils:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    @staticmethod
    def unknown_command(command_name):
        print("The command \"" + command_name + "\" could not be recognised. Type \"help\" for a list of "
                                                "commands.\n")

    @staticmethod
    def format_money(value):
        # formatted = str(round(value, 2))
        # if len(formatted.split(".")[1]) < 2:
        #     formatted = formatted + "0"
        return '{:,.2f}'.format(value)

    @staticmethod
    def get_market_info(name):
        try:
            return stocks.Ticker(name).info
        except:
            return None

    @staticmethod
    def format_time(time):
        time_str = str(time)
        if len(time_str) == 1:
            time_str = "0" + time_str
        return time_str

    @staticmethod
    def get_price_diff(now, old):
        now_f = float(now)
        old_f = float(old)

        if now_f > old_f:
            return "+" + Utils.format_money(now_f - old_f)
        elif old_f > now_f:
            return "-" + Utils.format_money(old_f - now_f)
        else:
            return "="

    @staticmethod
    def get_full_name(ticker_name, info):
        if "longName" in info:
            return info["longName"]
        else:
            return ticker_name
