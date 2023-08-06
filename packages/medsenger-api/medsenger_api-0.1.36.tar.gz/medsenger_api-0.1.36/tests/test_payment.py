from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from config import *

class TestPayment(TestCase):

    def create_client(self):
        return AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True)

    def test_request_payment(self):
        print(self.create_client().request_payment("test_1", 100, "Test payment"))


