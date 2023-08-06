class Subject:
    def __init__(self):
        self.observers = []

    def attachObserver(self, observer):
        self.observers.append(observer)

    def detachObserver(self, observer):
        self.observers.remove(observer)

    def notifyObservers(self, message="", payload={}):
        for observer in self.observers:
            observer.update(message, payload)
