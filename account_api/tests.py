import unittest
from django.test import Client


class AccountTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.unique_id = 'e93e2a61-42b9-4017-a5ab-ce5b4cb8a2f2'

    def test_ping(self):
        response = self.client.get('/api/ping/')
        self.assertEqual(response.status_code, 200)