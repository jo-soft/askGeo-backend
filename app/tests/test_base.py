import unittest.mock as mock
import unittest
from app import App


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.init_db_patcher = mock.patch('app.db._init_db_')
        self.db_mock = self.init_db_patcher.start()
        self.get_db_patcher = mock.patch('database.manager.get_db')
        self.get_db_mock = self.get_db_patcher.start()
        self.app = App.test_client()

    def tearDown(self):
        self.init_db_patcher.stop()
        self.get_db_patcher.stop()
