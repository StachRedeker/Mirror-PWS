from datetime import datetime

class GUIUtils:
    @staticmethod
    def format_money(value):
        return '{:,.2f}'.format(value)

    @staticmethod
    def format_money_decimal(value):
        return '{:.2f}'.format(value)
    
    @staticmethod
    def decrypt(raw):
        return raw.replace("U2038", "^").replace("U002E", ".")

    @staticmethod
    def formatClose(raw):
        if str(type(raw)) == "<class 'numpy.float64'>":
            return GUIUtils.format_money_decimal(raw)
        else:
            return " "

    @staticmethod
    def formatSplit(raw):
        try:
            return str(raw)
        except Exception:
            return "0.0"

    @staticmethod
    def formatDividend(raw):
        try:
            return str(raw)
        except Exception:
            return "0.0"

    @staticmethod
    def formatDate(raw, period):
        makeup = ["%b", "-", "%d"]
        if period == "day":
            makeup = ["%H", ":", "%M"]
        elif period == "week":
            makeup = ["%a", "-", "%h"]
        elif period == "max":
            makeup = ["%Y", "-", "%b"]

        try:
            return datetime.utcfromtimestamp(raw.tolist()/1e9).strftime("{0}{1}{2}".format(makeup[0], makeup[1], makeup[2]))
        except OSError:
            return "??-??"