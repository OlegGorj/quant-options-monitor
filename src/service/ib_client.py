import os
from ib_insync import IB

class IBClient:
    """
    IB_HOST=127.0.0.1
    IB_PORT=7497
    IB_CLIENT_ID=123
    """
    def __init__(self):
        self.host = os.getenv("IB_HOST", "127.0.0.1")
        self.port = int(os.getenv("IB_PORT", 7497))
        self.client_id = int(os.getenv("IB_CLIENT_ID", 123))
        self.ib = IB()

    def connect(self):
        self.ib.connect(self.host, self.port, clientId=self.client_id)
        return self.ib

