from procurement_bytetheory.controllers.Observer import Observer
from procurement_bytetheory.model.Business import Business
from procurement_bytetheory.model.Item import Item


class UIController(Observer):
    def __init__(self):
        super().__init__()
        self.view = None
        self.business = None

    def setView(self, view):
        self.view = view

    def setBusiness(self, business):
        self.business = business

    def update(self, message="", payload={}):
        self.view.update(message, payload)

    def createBusiness(self, name, moneyAmount):
        newBusiness = Business(name, moneyAmount)
        newBusiness.attachObserver(self)
        newBusiness.save()
        newBusiness.notifyObservers("Business created", newBusiness.serializeToJson())
        self.setBusiness(newBusiness)

    def seedMarket(self):
        self.business.market.seedMarket()
        self.business.market.save()
        self.business.notifyObservers("Market seeded", self.business.serializeToJson())

    def buyItemById(self, id):
        item = Item.getItemById(id)
        self.business.buy(item)
        self.business.save()
        self.business.notifyObservers("Item bought", self.business.serializeToJson())

    def buyCheapest(self, itemName=None):
        self.business.buyCheapest(itemName)
        self.business.save()
        self.business.notifyObservers(
            "Cheapest item bought", self.business.serializeToJson()
        )

    def buyAsManyAsPossible(self, itemName=None):
        if itemName:
            self.business.buyAsManyAsPossible(itemName)
        else:
            self.business.buyAsManyAsPossible()
        self.business.save()
        self.business.notifyObservers(
            "Bought as many as possible", self.business.serializeToJson()
        )

    def sellItemById(self, id):
        item = Item.getItemById(id)
        self.business.executeSale(item)
        self.business.save()
        self.business.notifyObservers("Item sold", self.business.serializeToJson())

    def sellItem(self, itemName=None):
        self.business.sellItem(itemName)
        self.business.save()
        self.business.notifyObservers("Sold item", self.business.serializeToJson())

    def liquidateInventory(self):
        self.business.liquidateInventory()
        self.business.save()
        self.business.notifyObservers(
            "Liquidated inventory", self.business.serializeToJson()
        )

    def getNetWorth(self):
        return self.business.getNetWorth()
