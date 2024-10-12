#This code defines an API route. handles authentication and calendar interactions, and NLP  routes.
#Keeping all API routes in one file (routes.py) makes it easier to manage and understand the API structure at a glance.


from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.services.nlp_service import NLPService

app = Flask(__name__)

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    token = data.get('token')
    query = data.get('query')

    if not token or not query:
        return jsonify({'error': 'Missing token or query'}), 400

    try:
        # Create credentials using the token
        creds = Credentials(token)
        
        # Build the Calendar service
        service = build('calendar', 'v3', credentials=creds)

        # Fetch recent events
        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        # Process the query using NLP
        nlp_service = NLPService()
        response = nlp_service.process_query(query, events)

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Use HTTPS in production