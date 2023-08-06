import logging
import os
from dotenv import load_dotenv

class Logger():
    def __init__(self, name: str):
        self._logging = logging.getLogger(name)

    def set(self):
        self._logging.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        ch = logging.StreamHandler()
        ch.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        formatter = logging.Formatter('%(asctime)s : %(levelname)7s - %(name)25s # %(message)s')
        ch.setFormatter(formatter)
        self._logging.addHandler(ch)
        return self._logging
    
