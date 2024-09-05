# cli_qa.py

import os
from dotenv import load_dotenv
from backend.services.calendar_service import CalendarService
from backend.services.nlp_service import NLPService
from google.oauth2.credentials import Credentials
from backend.models.user_model import User
from backend import db

load_dotenv()

def get_credentials():
    token = os.getenv("GOOGLE_TOKEN")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    token_uri = os.getenv("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    # Check if all required fields are present
    if not all([token, refresh_token, token_uri, client_id, client_secret]):
        missing = [
            field
            for field, value in {
                "GOOGLE_TOKEN": token,
                "GOOGLE_REFRESH_TOKEN": refresh_token,
                "GOOGLE_TOKEN_URI": token_uri,
                "GOOGLE_CLIENT_ID": client_id,
                "GOOGLE_CLIENT_SECRET": client_secret,
            }.items()
            if not value
        ]

        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
    )


def main():
    credentials = get_credentials()
    calendar_service = CalendarService(credentials)
    nlp_service = NLPService()

    print("Welcome to the Calendar Q&A CLI!")
    print("Type 'exit' to quit the application.")

    while True:
        query = input("\nEnter your question about your calendar: ")

        if query.lower() == "exit":
            print("Thank you for using Calendar Q&A CLI. Goodbye!")
            break

        # Fetch recent events
        events = calendar_service.fetch_events(max_results=10)

        # Prepare context from events
        context = " ".join(
            [
                f"{event.summary} on {event.start.get('dateTime', event.start.get('date'))}"
                for event in events.events
            ]
        )

        # Generate response
        response = nlp_service.generate_response(query, context)

        print(f"\nAnswer: {response}")


if __name__ == "__main__":
    main()
