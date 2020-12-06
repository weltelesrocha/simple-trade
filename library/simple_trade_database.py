class SimpleTradeDatabase:
    def __init__(self, host: str = None):
        self.connection = None
        pass

    def connect(self):
        if self.connection is None:
            pass
        return self.connection

    def create(self, collection: str = None, data: object = None):
        connection = self.connect()
        pass
