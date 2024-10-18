# backend/services/calendar_service.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
import sys
import os
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

    def format_date(self, date_string):
        # Convert the ISO format date string to a timezone-aware datetime object
        date_obj = datetime.fromisoformat(date_string.rstrip("Z")).replace(
            tzinfo=ZoneInfo("UTC")
        )
        return date_obj.strftime("%B %d, %Y at %I:%M %p %Z")

    def fetch_events(self, calendar_id="primary", max_results=100):
        # Get the current date and time in UTC
        now = datetime.now(ZoneInfo("UTC"))

        # Set time range: 7 days before and 30 days after current date
        time_min = (now - timedelta(days=7)).isoformat()
        time_max = (now + timedelta(days=30)).isoformat()

        events = []
        page_token = None
        retry_count = 0

        while True:
            try:
                events_result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
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
                    # Format the start and end times
                    if "dateTime" in event["start"]:
                        event["start"]["formatted"] = self.format_date(
                            event["start"]["dateTime"]
                        )
                        event["end"]["formatted"] = self.format_date(
                            event["end"]["dateTime"]
                        )
                    else:
                        event["start"]["formatted"] = self.format_date(
                            event["start"]["date"] + "T00:00:00Z"
                        )
                        event["end"]["formatted"] = self.format_date(
                            event["end"]["date"] + "T00:00:00Z"
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
        current_date_context = f"Today is {now.strftime('%B %d, %Y')}. "
        return current_date_context, EventList(events=validated_events)

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
            print(f"An error occurred while searching events: {error}")
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
            print(f"An error occurred while getting event details: {error}")
            return None
