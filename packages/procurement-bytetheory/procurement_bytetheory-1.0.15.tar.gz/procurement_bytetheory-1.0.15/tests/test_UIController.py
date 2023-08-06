from procurement_bytetheory.model.Item import Item

class TestUIController:
    def test_buyItemById_itemRemovedFromMarket(self, seededController):
        newItem = Item("test_item", 100, id=100)
        seededController.business.market.addItemToMarket(newItem)
        seededController.business.market.save()

        seededController.buyItemById(100)
        assert newItem not in seededController.business.market.items

    def test_buyItemById_itemAddedToInventory(self, seededController):
        newItem = Item("test_item", 100, id=100)
        seededController.business.market.addItemToMarket(newItem)
        seededController.business.market.save()
        seededController.business.inventory.save()

        seededController.buyItemById(100)
        assert newItem in seededController.business.inventory.items

    def test_buyItemById_businessMoneyAmountDecreases(self, seededController):
        newItem = Item("test_item", 100, id=100)
        seededController.business.market.addItemToMarket(newItem)
        seededController.business.market.save()
        seededController.business.save()

        initialMoneyAmount = seededController.business.moneyAmount
        seededController.buyItemById(100)
        assert seededController.business.moneyAmount == initialMoneyAmount - newItem.getPurchasePrice()

    def test_sellItemById_itemRemovedFromInventory(self, seededController):
        newItem = Item("test_item", 100, id=100)
        seededController.business.inventory.addItem(newItem)
        seededController.business.inventory.save()

        seededController.sellItemById(100)
        assert newItem not in seededController.business.inventory.items

    def test_sellItemById_businessMoneyAmountDecreases(self, seededController):
        newItem = Item("test_item", 100, id=100)
        seededController.business.inventory.addItem(newItem)
        seededController.business.inventory.save()
        seededController.business.save()

        initialMoneyAmount = seededController.business.moneyAmount
        seededController.sellItemById(100)
        assert seededController.business.moneyAmount == initialMoneyAmount + newItem.getSalesPrice() 

    def test_getNetWorth(self, seededController):
        newItem = Item("test_item", 100, id=100)
        seededController.business.market.addItemToMarket(newItem)
        seededController.business.market.save()
        seededController.business.save()

        initialNetWorth = seededController.business.moneyAmount
        seededController.buyItemById(100)
        assert seededController.business.getNetWorth() == initialNetWorth - newItem.getPurchasePrice() + newItem.getSalesPrice()
        