# Script to run the application
# run.py

import os
from dotenv import load_dotenv
from backend.app import app, db

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Ensure all tables are created
    with app.app_context():
        db.create_all()

    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))

    # Run the app
    app.run(host="0.0.0.0", port=port, debug=True)
