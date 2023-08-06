from importlib.resources import files
import sqlite3
class DatabaseHandler:
    dbFile = files("procurement_bytetheory.data").joinpath("ProcurementGame.db")

    def __init__(self):
        dbFile = files("procurement_bytetheory.data").joinpath("ProcurementGame.db")
        self.db = sqlite3.connect(dbFile)

    @classmethod
    def truncateTables(cls):
        db = sqlite3.connect(cls.dbFile)
        curs = db.cursor()
        curs.execute("""DELETE FROM Business""")
        curs.execute("""DELETE FROM Temp_Business""")
        curs.execute("""DELETE FROM Market""")
        curs.execute("""DELETE FROM Temp_Market""")
        curs.execute("""DELETE FROM Inventory""")
        curs.execute("""DELETE FROM Temp_Inventory""")
        curs.execute("""DELETE FROM Item""")
        curs.execute("""DELETE FROM Temp_Item""")
        db.commit()
        curs.close()
        db.close()

    @classmethod
    def get_all_items(cls, item_name=None):
        db = sqlite3.connect("../data/ProcurementGame.db")
        curs = db.cursor()

        items = []
        if item_name:
            pass
        else:
            curs.execute("""select * from Inventory""")
            items = curs.fetchall()
            db.commit()
            curs.close()
            db.close()

        return list(set([i[0] for i in items]))

    def get_cheapest_item(self, item_name=None):
        """If item_name is given then find cheapest of the given item.
        Otherwise, find the cheapest item across all items
        """
        curs = self.db.cursor()
        if item_name:
            curs.execute(
                """select "Item Name", Value, Quantity from Inventory where "Item Name"
            == ?""",
                (item_name,),
            )
            candidates = curs.fetchall()
            self.db.commit()
            curs.close()

            try:
                return sorted(candidates, key=lambda x: x[1])[0]
            except:
                return []
        else:
            curs.execute(""" select "Item Name", MIN(Value), Quantity from Inventory""")
            item = curs.fetchone()
            self.db.commit()
            curs.close()
            return item

    def execute_buy(self, item):
        curs = self.db.cursor()
        item_name, value, db_quantity = self.item_in_db(item)
        if db_quantity > 1:
            curs.execute(
                """update Inventory set Quantity = Quantity - 1 where "Item Name" = ?
                and Value = ?""",
                (item_name, value),
            )
            self.db.commit()
            curs.close()
        else:
            curs.execute(
                """delete from Inventory where "Item Name" = ?
                and Value = ?""",
                (item_name, value),
            )
            self.db.commit()
            curs.close()

    def execute_sell(self, item):
        curs = self.db.cursor()
        if self.item_in_db(item):
            curs.execute(
                """update Inventory set Quantity = Quantity + 1 where
                "Item Name" = ? and Value = ?""",
                [item[0], item[1]],
            )
        else:
            curs.execute(
                """insert into Inventory ("Item Name",Value,Quantity)
                values (?,?,?)""",
                [item[0], item[1], 1],
            )

        self.db.commit()
        curs.close()

    def item_in_db(self, item):
        curs = self.db.cursor()

        curs.execute(
            """select "Item Name", Value, Quantity from Inventory where
            "Item Name" = ? and Value = ?""",
            [item[0], item[1]],
        )
        item = curs.fetchone()

        self.db.commit()
        curs.close()

        return item
