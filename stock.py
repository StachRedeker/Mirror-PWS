import yfinance as stocks
import time


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


class Programma:
    # Waardes initialiseren
    def __init__(self):
        self.run = True

        # Voor de volg-functie
        self.follow = None
        self.followName = None
        self.followInfo = None
        self.lastFollowUpdate = time.time()
        self.lastFollowPrice = "0.00"

    # Het programma wordt geactiveerd als dit runt.
    def start(self):
        while self.run:
            if self.follow is not None:
                if time.time() - self.lastFollowUpdate >= 5.0:
                    self.lastFollowUpdate = self.lastFollowUpdate + 100
                    self.getFollowed()
            else:
                self.vraagCommando()

    def getFollowed(self):
        # De geschiedenis van de prijs van de afgelopen 2 dagen.
        history = self.follow.history(period="2d")

        lastCloseFormatted = Utils.formatValue(history.get("Close")[0])
        priceNowFormatted = Utils.formatValue(history.get("Close")[1])

        lastCloseFloat = float(lastCloseFormatted)
        newPriceFloat = float(priceNowFormatted)
        oldPriceFloat = float(self.lastFollowPrice)

        diffPrev = "~"
        if newPriceFloat > oldPriceFloat:
            diffPrev = "+" + Utils.formatValue(newPriceFloat - oldPriceFloat)
        elif oldPriceFloat > newPriceFloat:
            diffPrev = "-" + Utils.formatValue(oldPriceFloat - newPriceFloat)

        diffLastClose = "~"
        if lastCloseFloat > newPriceFloat:
            diffLastClose = "-" + Utils.formatValue(lastCloseFloat - newPriceFloat)
        elif newPriceFloat > lastCloseFloat:
            diffLastClose = "+" + Utils.formatValue(newPriceFloat - lastCloseFloat)

        print("Huidige waarde " + self.followName + ": " + priceNowFormatted + " (" + diffPrev + " | " + diffLastClose + ")")
        self.lastFollowUpdate = time.time()
        self.lastFollowPrice = priceNowFormatted

    def infoCommand(self, naam):
        marktInfo = Utils.getMarketInformation(naam)

        if marktInfo is not None:
            # De markt bestaat
            titel = "================= Informatie " + naam + " ================="
            print("\n" + titel + "\n")
            print(" " + marktInfo["longName"] + " is een bedrijf uit de '" + marktInfo["sector"] + "' sector.")
            print(" Het heeft ongeveer " + str(marktInfo["fullTimeEmployees"]) + " werknemers.")
            print(" Op dit moment is is één aandeel " + Utils.formatValue(
                stocks.Ticker(naam).history(period="1d").get("Close")[0]) + " " + marktInfo["currency"] + " waard.")
            print("\n" + ("=" * len(titel)) + "\n")
        else:
            # De markt bestaat niet.
            print("Die ticker komt me niet bekend voor. Is het goed gespeld?")

    def vraagCommando(self):
        commandRaw = input("Voer je commando in.\n» ")
        commandSplit = commandRaw.split(" ")
        commandName = commandSplit[0].lower()

        arguments = commandSplit.copy()
        arguments.pop(0)

        if commandName == "info":
            if len(arguments) > 0:
                marktNaam = arguments[0].upper()

                print("Informatie over " + marktNaam + " verkrijgen...")
                self.infoCommand(marktNaam)
                return
            else:
                print("Gebruik: info <ticker>")
                return
        elif commandName == "volg":
            if len(arguments) > 0:
                marktNaam = arguments[0].upper()

                print("Informatie over " + marktNaam + " verkrijgen...")

                marktInfo = Utils.getMarketInformation(marktNaam)

                if marktInfo is not None:
                    print("Je volgt nu " + marktInfo["longName"] + ". (prijs in " + marktInfo["currency"] + ")")
                    self.follow = stocks.Ticker(marktNaam)
                    self.followName = marktNaam
                    self.followInfo = marktInfo
                    self.lastFollowPrice = "0.00"
                else:
                    print("Die ticker komt me niet bekend voor. Is het goed gespeld?")
                return
            else:
                print("Gebruik: volg <ticker>")
                return
        elif commandName == "quit" or commandName == "stop":
            self.run = False
            print("Tot ziens!")
            return
        elif commandName == "help":
            print("\nBeschikbare commando's:")
            print("- info <ticker> | Verkrijgt informatie over een markt.")
            print("- volg <ticker> | Volg de prijs van een markt. Update elke 5 seconden.")
            print("- stop | Verlaat het programma.")
            print("- quit | Verlaat het programma.")
            print("<...>: vereist, [...]: optioneel\n")
            return
        else:
            print("Sorry, ik ken het commando \"" + commandName + "\" niet. Typ \"help\" voor een lijst met "
                                                                  "commando's.\n")


Programma().start()