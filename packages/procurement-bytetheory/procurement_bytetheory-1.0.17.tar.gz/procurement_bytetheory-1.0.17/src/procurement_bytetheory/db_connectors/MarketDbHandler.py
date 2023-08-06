from procurement_bytetheory.db_connectors.DatabaseHandler import DatabaseHandler
from procurement_bytetheory.db_connectors.ItemDbHandler import ItemDbHandler


class MarketDbHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()
        self.itemDbHandler = ItemDbHandler()

    def saveMarket(self, market):
        self.populateMarketTempTable(market)
        self.populateItemTempTable(market.items)

        self.upsertMarketRecord(market)
        self.updateMarketsThatNoLongerExist()

        self.upsertCurrentMarketItems(market.items)
        self.updateItemsNoLongerInMarket()

    def populateItemTempTable(self, items):
        self.itemDbHandler.populateItemTempTable(items)

    def populateMarketTempTable(self, market):
        # don't need this right now
        pass

    def upsertMarketRecord(self, market):
        curs = self.db.cursor()
        try:
            print("Attempting to insert a new Market...")
            curs.execute(
                """
                INSERT INTO Market
                VALUES ({id}, '{name}')
                """.format(
                    id=market.id, name=market.name
                )
            )
            print("New market inserted.")
        except Exception as e:
            print(e)
            print("Record already exists.  Updating a Market...")
            curs.execute(
                """
                UPDATE Market
                SET id={id}, name='{name}'
                WHERE id={id};
                """.format(
                    id=market.id, name=market.name
                )
            )
            print("Market updated")
        self.db.commit()
        curs.close()

    def updateMarketsThatNoLongerExist(self):
        # don't need this right now
        pass

    def upsertCurrentMarketItems(self, items):
        self.itemDbHandler.upsertItems(items)

    def updateItemsNoLongerInMarket(self):
        curs = self.db.cursor()
        print("Updating items no long in market...")
        curs.execute(
            """
            UPDATE Item
            SET market_id = -1
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
