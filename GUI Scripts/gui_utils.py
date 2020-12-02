class GUIUtils:
    @staticmethod
    def format_money(value):
        return '{:,.2f}'.format(value)

    @staticmethod
    def format_money_decimal(value):
        return '{:.2f}'.format(value)