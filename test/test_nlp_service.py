# tests/test_nlp_service.py
import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
import unittest
from backend.services.nlp_service import NLPService
from dotenv import load_dotenv


load_dotenv()


class TestNLPService(unittest.TestCase):
    def setUp(self):
        self.nlp_service = NLPService()

    def test_generate_response(self):
        query = "When is my next meeting?"
        context = "You have a meeting on August 30th at 2 PM."
        response = self.nlp_service.generate_response(query, context)
        self.assertIn("August 30th", response)
        self.assertIn("2 PM", response)

    # Add more tests for other NLP functionalities
