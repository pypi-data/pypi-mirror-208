from InquirerPy import prompt
from procurement_bytetheory import FloatValidator
from procurement_bytetheory.controllers import CLIController
from procurement_bytetheory.views import CLIProcurementSimulator


class CLIProcurementGame():
    def __init__(self):
        self.viewController = CLIController()
        self.business = self.promptUserToCreateBusiness()
        self.gameInProgress = False

    def start(self):
        simulator = CLIProcurementSimulator()
        self.gameInProgress = True
        while self.gameInProgress:
            simulator.simulate(self)

    def promptUserToCreateBusiness(self):
        promptToCreateBusiness = [
            {
                'type': 'input',
                'name': 'business_name',
                'message': 'What\'s the name of your business?',
            },
            {
                'type': 'input',
                'name': 'money_amount',
                'message': 'How much money does your business have?',
                'validate': FloatValidator
            }
        ]
        businessName, moneyAmount = self.getResponseToPrompt(promptToCreateBusiness)        
        self.viewController.createBusiness(businessName, moneyAmount)

    def getResponseToPrompt(self, promptToCreateBusiness):
        response = prompt(promptToCreateBusiness)
        return [response['business_name'], int(response['money_amount'])]

    def stop(self):
        self.gameInProgress = False