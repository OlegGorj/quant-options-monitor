import os
import logging
from ib_insync import IB
import time


class IBClient:
    """Client wrapper for IB connection with retry, logging, and health check."""
    def __init__(self):
        self.host = os.getenv("IB_HOST", "127.0.0.1")
        self.port = int(os.getenv("IB_PORT", 4001)) # 7497 for TWS, 4002 for IB Gateway 
        self.client_id = int(os.getenv("IB_CLIENT_ID", 12345678))
        self.timeout = int(os.getenv("IB_TIMEOUT", 10))  # seconds
        self.max_retries = int(os.getenv("IB_RETRIES", 3))
        self.retry_delay = int(os.getenv("IB_RETRY_DELAY", 3))  # seconds
        self.ib = IB()

    def connect(self):
        attempt = 0
        while attempt < self.max_retries:
            try:
                logging.info(f"Connecting to IB at {self.host}:{self.port} with client ID {self.client_id}...")
                self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=self.timeout)
                if self.ib.isConnected():
                    logging.info("Successfully connected to Interactive Brokers API.")
                    return self.ib
                else:
                    raise ConnectionError("Connection established but isConnected() returned False")
            except Exception as e:
                logging.warning(f"Connection attempt {attempt + 1} failed: {e}")
                attempt += 1
                time.sleep(self.retry_delay)

            raise ConnectionError("Unable to connect to IB after multiple attempts.")

    def is_connected(self):
        """Returns True if the IB client is currently connected."""
        return self.ib.isConnected()

    def ensure_connected(self):
        """Reconnect if the connection is lost."""
        if not self.is_connected():
            logging.info("IB connection lost. Reconnecting...")
            self.connect()
        self.ib.connect(self.host, self.port, clientId=self.client_id)
        return self.ib
