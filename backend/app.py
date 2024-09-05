# # backend/app.py, main Flask application

# from flask import Flask, request, jsonify
# from services.calendar_service import CalendarService
# from services.nlp_service import NLPService
# from dotenv import load_dotenv
# import os
# import sys

# # Add the project root directory to Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.insert(0, project_root)


# load_dotenv()

# app = Flask(__name__)
# app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# nlp_service = NLPService(app.config["OPENAI_API_KEY"])


# @app.route("/api/search", methods=["POST"])
# def search():
#     data = request.json
#     query = data["query"]
#     token = data["token"]

#     calendar_service = CalendarService(token)

#     events = calendar_service.search_events(query)
#     context = " ".join([event.summary for event in events.events])

#     response = nlp_service.generate_response(query, context)
#     return jsonify(
#         {"response": response, "events": [event.dict() for event in events.events]}
#     )


# @app.route("/api/events", methods=["GET"])
# def get_events():
#     token = request.headers.get("Authorization").split("Bearer ")[1]
#     token_info = token
#     calendar_service = CalendarService(token_info)

#     events = calendar_service.fetch_events()
#     return jsonify({"events": [event.dict() for event in events.events]})


# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.auth.oauth_server import oauth_bp
from backend.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Register the OAuth blueprint
app.register_blueprint(oauth_bp)

@app.route('/')
def index():
    return 'Welcome to the ORII Calendar Integration'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)