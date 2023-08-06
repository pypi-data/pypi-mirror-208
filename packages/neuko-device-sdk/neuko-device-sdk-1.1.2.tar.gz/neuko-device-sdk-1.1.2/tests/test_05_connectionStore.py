import unittest
import asyncio
from unittest.mock import patch
from src.neuko.connection.connectionStore import ConnectionStore

class ConnectionStoreTest(unittest.TestCase):

    def setUp(self):
        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

    @patch("src.neuko.connection.connectionStore.ConnectionStore.__abstractmethods__", set())
    def test_01_internet_connection(self):
        '''
        This function tests if the user has an internet connection
        '''
        store = ConnectionStore()
        res = self.my_loop.run_until_complete(store.isConnectedToInternet())
        self.assertTrue(res)


if __name__ == '__main__':
    unittest.main()