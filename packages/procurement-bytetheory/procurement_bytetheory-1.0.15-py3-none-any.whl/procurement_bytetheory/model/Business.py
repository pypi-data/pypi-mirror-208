from procurement_bytetheory.model.Market import Market
from procurement_bytetheory.db_connectors.BusinessDbHandler import BusinessDbHandler
from procurement_bytetheory.model.Subject import Subject
from procurement_bytetheory.model.Inventory import Inventory
import json
from procurement_bytetheory.errors.InsufficientFundsError import InsufficientFundsError


class Business(Subject):
    numBusinesses = 0

    def __init__(
        self,
        name,
        moneyAmount=400,
        id=None,
        inventory=None,
        market=None,
        dbHandler=None,
    ):
        super().__init__()

        self.name = name
        self.moneyAmount = moneyAmount

        self.id = id if id else Business.numBusinesses + 1
        Business.numBusinesses += 1

        self.inventory = (
            inventory if inventory else Inventory("ACME Innovations Inventory")
        )
        self.market = market if market else Market("USA")
        self.dbHandler = dbHandler if dbHandler else BusinessDbHandler()

        self.volumeSold = 0
        self.volumePurchased = 0
        self.numberSold = 0
        self.numberPurchased = 0
        self.salesBasis = 0

    def save(self):
        self.dbHandler.saveBusiness(self)

    def getDictionaryRepresentation(self):
        return {
            "id": self.id,
            "name": self.name,
            "moneyAmount": self.moneyAmount,
            "inventory": self.inventory.getDictionaryRepresentation(),
            "market": self.market.getDictionaryRepresentation(),
            "metrics": {
                "netWorth": self.getNetWorth(),
                "margin": self.getMargin(),
                "volumeSold": self.getVolumeSold(),
                "volumePurchased": self.getVolumePurchased(),
                "numberSold": self.getNumberSold(),
                "numberPurchased": self.getNumberPurchased(),
                "avgSalePrice": self.getAverageSalePrice(),
                "avgPurchasePrice": self.getAveragePurchasePrice(),
            },
        }

    def serializeToJson(self):
        return json.dumps(self.getDictionaryRepresentation())

    def buyCheapest(self, itemName=None):
        """Buys the cheapest item with the specified itemName, and if no itemName is specified,
        buys one of the cheapest items in the market.
        """
        buyingCheapestOfSpecificItem = bool(itemName)
        if buyingCheapestOfSpecificItem:
            cheapestOfGivenItem = self.market.getCheapestItemByName(itemName)
            self.buy(cheapestOfGivenItem)
        else:
            cheapestItemInMarket = self.market.getCheapestItemInMarket()
            self.buy(cheapestItemInMarket)

    def buyAsManyAsPossible(self, itemName, numBought=0):
        """Buys as many of the specified item as possible."""
        if not bool(itemName) or not self.market.hasItem(itemName):
            return

        cheapestOfGivenItem = self.market.getCheapestItemByName(itemName)
        if self.canAfford(cheapestOfGivenItem):
            self.buy(cheapestOfGivenItem)
            self.buyAsManyAsPossible(cheapestOfGivenItem.name, numBought=numBought + 1)
        else:
            if numBought == 0:
                raise InsufficientFundsError(
                    self.moneyAmount,
                    cheapestOfGivenItem.getPurchasePrice(),
                    "You don't have enough money to buy anything!",
                )

    def buyAsManyAsPossible(self, numBought=0):
        itemToBuy = self.market.getCheapestItemInMarket()
        if self.canAfford(itemToBuy):
            self.buy(itemToBuy)
            self.buyAsManyAsPossible()
        else:
            if numBought == 0:
                raise InsufficientFundsError(
                    self.moneyAmount,
                    itemToBuy.getPurchasePrice(),
                    "You don't have enough money to buy anything!",
                )

    def payPriceOfItem(self, price):
        self.moneyAmount = self.moneyAmount - price

    def addItemToInventory(self, item):
        self.inventory.addItem(item)

    def canAfford(self, item):
        if self.moneyAmount > item.getPurchasePrice():
            return True
        return False

    def buy(self, item):
        if self.canAfford(item):
            self.market.removeItemFromMarket(item)
            self.payPriceOfItem(item.getPurchasePrice())
            self.addItemToInventory(item)

            self.volumePurchased += item.getPurchasePrice()
            self.numberPurchased += 1
        else:
            raise InsufficientFundsError(
                self.moneyAmount,
                item.getPurchasePrice(),
                "You don't have enough money to buy this!",
            )

    def sellItem(self, itemName=None):
        """Sells the most expensive of the specified itemName.
        If no itemName is specified, sells the most expensive item.
        """
        sellingSpecificItem = bool(itemName)
        if sellingSpecificItem:
            if self.inventory.hasItem(itemName):
                highestValueItem = self.inventory.getHighestValueItem(itemName)
                self.executeSale(highestValueItem)
        else:
            if not self.inventory.isEmpty():
                highestValueItem = self.inventory.getHighestValueItem()
                self.executeSale(highestValueItem)

    def liquidateInventory(self):
        for item in self.inventory.items:
            self.collectPaymentFromMarketCustomer(item.getFireSalePrice())
            self.volumeSold += item.getFireSalePrice()
            self.salesBasis += item.getPurchasePrice()
            self.numberSold += 1
        self.clearInventory()

    def collectPaymentFromMarketCustomer(self, salesPrice):
        self.moneyAmount += salesPrice

    def removeItemFromInventory(self, item):
        self.inventory.removeItem(item)

    def clearInventory(self):
        self.inventory.clear()

    def executeSale(self, item):
        self.collectPaymentFromMarketCustomer(item.getSalesPrice())
        self.removeItemFromInventory(item)
        self.volumeSold += item.getSalesPrice()
        self.salesBasis += item.getPurchasePrice()
        self.numberSold += 1

    def getNetWorth(self):
        return round(self.moneyAmount + self.inventory.getWorth(), 2)

    def getMargin(self):
        if self.volumePurchased == 0 or self.volumeSold == 0:
            return None
        return round(((self.volumeSold / self.salesBasis) - 1) * 100, 2)

    def getVolumeSold(self):
        return round(self.volumeSold, 2)

    def getVolumePurchased(self):
        return round(self.volumePurchased, 2)

    def getNumberSold(self):
        return self.numberSold

    def getNumberPurchased(self):
        return self.numberPurchased

    def getAverageSalePrice(self):
        if self.numberSold == 0:
            return None
        return round(self.volumeSold / self.numberSold, 2)

    def getAveragePurchasePrice(self):
        if self.numberPurchased == 0:
            return None
        return round(self.volumePurchased / self.numberPurchased, 2)
