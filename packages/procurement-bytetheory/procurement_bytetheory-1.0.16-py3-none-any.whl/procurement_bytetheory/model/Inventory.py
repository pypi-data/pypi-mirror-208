from procurement_bytetheory.db_connectors.InventoryDbHandler import InventoryDbHandler
import json

class Inventory:
    numInventories = 0

    def __init__(self, name, id=None, items=None, dbHandler=None):
        self.name = name

        self.id = id if id else Inventory.numInventories + 1
        Inventory.numInventories += 1

        self.items = items if items else []  # [item1, item2, ...]
        self.dbHandler = dbHandler if dbHandler else InventoryDbHandler()

    def save(self):
        self.dbHandler.saveInventory(self)

    def getDictionaryRepresentation(self):
        return {
            "id": self.id,
            "name": self.name,
            "items": [item.getDictionaryRepresentation() for item in self.items]
        }

    def serializeToJson(self):
        return json.dumps(self.getDictionaryRepresentation())

    def addItem(self, item):
        self.items.append(item)
        item.setInventory(self.id)

    def removeItem(self, item):
        self.items.remove(item)
        item.setInventory(None)

    def clear(self):
        for item in self.items:
            item.setInventory(None)
        self.items = []

    def isEmpty(self):
        return not bool(len(self.items))

    def hasItem(self, itemName):
        return itemName in [item.name for item in self.items]

    def getHighestValueItem(self, itemName=None):
        if itemName:
            return max([item for item in self.items if item.name == itemName])
        else:
            return max(self.items)

    def getWorth(self):
        return sum([item.getSalesPrice() for item in self.items])
