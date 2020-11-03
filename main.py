import stock
import invest

inp = None
while inp not in ["informeren", "investeren"]:
    inp = input("Investeren of informeren?\n» ").lower()

if inp == "informeren":
    print("Starten...\n")
    stock.StockProgram().start()
else:
    print("Starten...\n")
    invest.InvestProgram().start()
