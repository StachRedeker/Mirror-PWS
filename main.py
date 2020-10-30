import stock

while not input("Investeren of informeren?\n» ").lower() == "informeren":
    pass

print("Running stock.py - StockProgram...")
stock.StockProgram().start()