# tests/test_calendar_service.py
import unittest
import os
import sys
from unittest.mock import Mock, patch

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from backend.services.calendar_service import CalendarService
from dotenv import load_dotenv


load_dotenv()


class TestCalendarService(unittest.TestCase):
    def setUp(self):
        self.mock_credentials = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        }
        self.calendar_service = CalendarService(self.mock_credentials)

    @patch("googleapiclient.discovery.build")
    def test_fetch_events(self, mock_build):
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_service.events().list().execute.return_value = {
            "items": [
                {
                    "id": "1",
                    "summary": "Test Event",
                    "start": {"dateTime": "2023-08-30T10:00:00Z"},
                }
            ]
        }

        events = self.calendar_service.fetch_events()
        self.assertEqual(len(events.events), 1)
        self.assertEqual(events.events[0].summary, "Test Event")

    # Add more tests for search_events, get_event_details, etc.
