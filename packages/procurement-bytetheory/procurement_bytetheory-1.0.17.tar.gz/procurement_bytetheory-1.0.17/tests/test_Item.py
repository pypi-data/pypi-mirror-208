from procurement_bytetheory.model.Item import Item

class TestItem:
    def test_getItemById_success(self, baseEnvironment):
        newItem = Item("test item", 49, id=1, marketId=2, inventoryId=3)
        newItem.save()
        fetchedItem = Item.getItemById(1)
        assert fetchedItem == newItem

    
