from procurement_bytetheory.db_connectors.DatabaseHandler import DatabaseHandler
from procurement_bytetheory.db_connectors.ItemDbHandler import ItemDbHandler


class InventoryDbHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()
        self.itemDbHandler = ItemDbHandler()

    def saveInventory(self, inventory):
        self.populateInventoryTempTable(inventory)
        self.populateItemTempTable(inventory.items)

        self.upsertInventoryRecord(inventory)
        self.updateInventoriesThatNoLongerExist()

        self.upsertCurrentInventoryItems(inventory.items)
        self.updateItemsNoLongerInInventory()

    def populateInventoryTempTable(self, inventory):
        # don't need this right now
        pass

    def populateItemTempTable(self, items):
        self.itemDbHandler.populateItemTempTable(items)

    def upsertInventoryRecord(self, inventory):
        curs = self.db.cursor()
        try:
            print("Attempting to insert a new Inventory...")
            curs.execute(
                """
                INSERT INTO Inventory
                VALUES ({id}, '{name}')
                """.format(
                    id=inventory.id, name=inventory.name
                )
            )
            print("New inventory inserted.")
        except Exception as e:
            print(e)
            print("Record already exists.  Updating a Inventory...")
            curs.execute(
                """
                UPDATE Inventory
                SET id={id}, name='{name}'
                WHERE id={id};
                """.format(
                    id=inventory.id, name=inventory.name
                )
            )
            print("Inventory updated")
        self.db.commit()
        curs.close()

    def updateInventoriesThatNoLongerExist(self):
        # don't need this right now
        pass

    def upsertCurrentInventoryItems(self, items):
        self.itemDbHandler.upsertItems(items)

    def updateItemsNoLongerInInventory(self):
        curs = self.db.cursor()
        print("Updating items no long in Inventory...")
        curs.execute(
            """
            UPDATE Item
            SET inventory_id = -1
            WHERE id IN (
                SELECT i.id 
                FROM 
                    Item as i LEFT JOIN Temp_Item as ti
                        ON i.id = ti.id
                    WHERE ti.id is NULL
            )
            """
        )
        print("Items updated")
        self.db.commit()
        curs.close()
