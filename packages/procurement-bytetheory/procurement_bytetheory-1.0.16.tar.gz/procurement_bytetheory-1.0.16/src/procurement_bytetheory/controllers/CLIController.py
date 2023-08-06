from procurement_bytetheory.controllers import Observer
from procurement_bytetheory.model import Business

class CLIController(Observer):

    def __init__(self):
        super().__init__()
        self.view = None

    def setView(self, view):
        self.view = view

    def update(self):
        self.view.update()

    def createBusiness(self, name, moneyAmount):
        newBusiness = Business(name, moneyAmount)
        newBusiness.save()

    def buyCheapest(self):
        pass

    def buyAll(self):
        pass

    def sellItem(self):
        pass

    def liquidateInventory(self):
        pass

