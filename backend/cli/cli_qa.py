# updated with Full OAuth2 flow
import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
from backend.services.calendar_service import CalendarService
from backend.services.nlp_service import NLPService
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None

        if not creds:
            print("No valid credentials found. Starting new OAuth2 flow...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "backend/cli/client_secret.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error in OAuth2 flow: {e}")
                return None

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def fetch_events(service, max_results=10):
    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


from datetime import datetime
from zoneinfo import ZoneInfo


def main():
    credentials = get_credentials()
    if not credentials:
        print("Failed to obtain valid credentials. Exiting.")
        return

    calendar_service = CalendarService(credentials)
    nlp_service = NLPService()

    print("Welcome to the Calendar Q&A CLI!")
    print("Type 'exit' to quit the application.")

    while True:
        query = input("\nEnter your question about your calendar: ")

        if query.lower() == "exit":
            print("Thank you for using Calendar Q&A CLI. Goodbye!")
            break

        try:
            # Fetch recent events
            current_date_context, events = calendar_service.fetch_events(max_results=10)

            # Prepare context from events
            events_context = " ".join(
                [
                    f"{event.summary} on {event.start.get('formatted', event.start.get('dateTime', event.start.get('date')))}"
                    for event in events.events
                ]
            )

            # Combine current date context and events context
            full_context = current_date_context + events_context

            # Handle "what day is it today" query specifically
            if "what day is it today" in query.lower():
                today = datetime.now(ZoneInfo("UTC"))
                response = f"Today is {today.strftime('%A, %B %d, %Y')}."
            else:
                # Generate response using NLP service
                response = nlp_service.generate_response(query, full_context)

            print(f"\nAnswer: {response}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again or type 'exit' to quit.")


if __name__ == "__main__":
    main()
