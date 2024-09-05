# backend/services/calendar_service.py

import datetime
import time
import sys
import os

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.models.user_model import Event, EventList
from dotenv import load_dotenv

load_dotenv()

class CalendarService:
    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build("calendar", "v3", credentials=self.credentials)

    def fetch_events(
        self, calendar_id="primary", min_time=None, max_time=None, max_results=100
    ):
        if min_time is None:
            min_time = datetime.datetime.utcnow().isoformat() + "Z"
        if max_time is None:
            max_time = (
                datetime.datetime.utcnow() + datetime.timedelta(days=30)
            ).isoformat() + "Z"

        events = []
        page_token = None
        retry_count = 0

        while True:
            try:
                events_result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=min_time,
                        timeMax=max_time,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                        pageToken=page_token,
                        fields="items(id,summary,description,location,start,end,attendees,organizer,recurrence,reminders),nextPageToken",
                    )
                    .execute()
                )

                items = events_result.get("items", [])
                for event in items:
                    event["type"] = (
                        "Scheduled Event"
                        if "dateTime" in event["start"]
                        else "All Day Event"
                    )
                    events.append(event)

                page_token = events_result.get("nextPageToken")
                if not page_token:
                    break

            except HttpError as error:
                if error.resp.status in [403, 500, 503] and retry_count < 5:
                    retry_count += 1
                    time.sleep(2**retry_count)  # Exponential backoff
                    continue
                else:
                    print(f"An error occurred: {error}")
                    break

        validated_events = [Event(**event) for event in events]
        return EventList(events=validated_events)

    def search_events(self, query, max_results=10):
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    q=query,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            items = events_result.get("items", [])
            validated_events = [Event(**event) for event in items]
            return EventList(events=validated_events)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return EventList(events=[])

    def get_event_details(self, event_id):
        try:
            event = (
                self.service.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )
            return Event(**event)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None