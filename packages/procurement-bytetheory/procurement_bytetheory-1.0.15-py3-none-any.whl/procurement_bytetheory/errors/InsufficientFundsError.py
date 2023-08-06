class InsufficientFundsError(Exception):
    def __init__(self, fundsAvailable, fundsNeeded, message="Insufficient funds"):
        self.fundsAvailable = fundsAvailable
        self.fundsNeeded = fundsNeeded
        self.message = message
        super().__init__(self.message)
