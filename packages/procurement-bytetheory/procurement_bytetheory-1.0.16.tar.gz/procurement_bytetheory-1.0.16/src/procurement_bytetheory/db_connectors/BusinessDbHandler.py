from procurement_bytetheory.db_connectors.DatabaseHandler import DatabaseHandler
from procurement_bytetheory.db_connectors.MarketDbHandler import MarketDbHandler
from procurement_bytetheory.db_connectors.InventoryDbHandler import InventoryDbHandler
class BusinessDbHandler(DatabaseHandler):

    def __init__(self):
        super().__init__()
        self.marketDbHandler = MarketDbHandler()
        self.inventoryDbHandler = InventoryDbHandler()

    def saveBusiness(self, business):
        self.saveBusinessRecord(business)
        self.marketDbHandler.saveMarket(business.market)
        self.inventoryDbHandler.saveInventory(business.inventory)

    def saveBusinessRecord(self, business):
        curs = self.db.cursor()
        try:
            print('Attempting to insert a new Business...')
            curs.execute(
                """
                INSERT INTO Business
                VALUES ({id}, '{name}', {money_amount}, {marketId}, {inventoryId});
                """.format(id=business.id, name=business.name, money_amount=business.moneyAmount, marketId=business.market.id if business.market else -1, inventoryId=business.inventory.id if business.inventory else -1)
            )
            print('New business inserted.')
        except Exception as e:
            print(e)
            print('Record already exists.  Updating a Business...')
            curs.execute(
                """
                UPDATE Business
                SET id={id}, name='{name}', money_amount={money_amount}, market_id={marketId}, inventory_id={inventoryId}
                WHERE id={id};
                """.format(id=business.id, name=business.name, money_amount=business.moneyAmount, marketId=business.market.id, inventoryId=business.inventory.id)
            )
            print('Business updated')
        self.db.commit()
        curs.close()

    def getBusinessById(self, id):
        curs = self.db.cursor()
        try:
            curs.execute(
                """
                SELECT id, name, money_amount, market_id
                FROM Business
                WHERE id = {}
                """.format(
                    id
                )
            )
            dbResponse = curs.fetchall()
            curs.close()
            return self.deserializer.deserializeBusiness(dbResponse[0])
        except Exception as e:
            print(e)
            raise Exception("No business with id {} exists", id)
