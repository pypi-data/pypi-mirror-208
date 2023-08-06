from InquirerPy import prompt

from procurement_bytetheory import DatabaseHandler, FloatValidator


class Simulator():

    def simulate(self, game):
        actions_prompt = {
            'type': 'list',
            'name': 'action',
            'message': 'What would you like to do next?',
            'choices': ['Buy inventory', 'Sell inventory', 'Check net worth', 'Quit']
        }
        answer = prompt(actions_prompt)
        if(answer['action'] == 'Buy inventory'):
            self.buyInventory(game.business)
        elif(answer['action'] == 'Sell inventory'):
            self.sellInventory(game.business)
        elif(answer['action'] == 'Check net worth'):
            self.checkNetWorth(game.business)
        elif(answer['action'] == 'Quit'):
            game.stop()
        else:
            raise Exception('Something went wrong')

    def stopGame(self, game):
        game.stop()

    def buyInventory(self, business):
        inventoryItems = business.getAllInventoryItems()
                
        whichItemsPrompt = [
            {
                'type': 'list',
                'name': 'which_item(s)',
                'message': 'Which item(s) do you want to buy?',
                'choices': inventoryItems + ['One of whatever\'s cheapest', 'As many units of the cheapest item as possible', 'Quit']
            }
        ]
        answer = prompt(whichItemsPrompt)
        itemName = answer['which_item(s)']

        if(itemName == "One of whatever\'s cheapest"):
            self.owners[owner_name].buy_cheapest()
            return True
        elif(itemName == "As many units of the cheapest item as possible"):
            self.owners[owner_name].buy_all()
            return True
        elif(itemName == "Quit"):
            return False
        else:
            self.owners[owner_name].buy_cheapest(itemName)
            return True

    def sellInventory(self, business):
        owner_name = self.which_owner() 
        if(not owner_name): return False

        items = list(set([i[0] for i in self.owners[owner_name].inventory_dict]))
        which_items_prompt = [
            {
                'type': 'list',
                'name': 'which_item(s)',
                'message': 'Which item(s) do you want to sell?',
                'choices': items + ['One of whatever has the highest price', 'All of it', 'Quit']
            }
        ]
        answer = prompt(which_items_prompt)
        itemName = answer['which_item(s)']

        if(itemName == "One of whatever has the highest price"):
            self.owners[owner_name].sell_item()
            return True
        elif(itemName == "All of it"):
            self.owners[owner_name].fire_sale()
            return True
        elif(itemName == "Quit"):
            return False
        else:
            self.owners[owner_name].sell_item(itemName)
            return True

    def checkNetWorth(self, business):
        owner_name = self.which_owner() 
        if(not owner_name): return False
        self.owners[owner_name].net_worth()
        return True
