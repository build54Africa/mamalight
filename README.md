# Mamalight

Mamalight is a Python application that uses Flask, Twilio, Cohere, APScheduler, and python-dotenv to provide SMS-based services. It integrates with Twilio for sending/receiving SMS, Cohere for AI-powered text processing, and APScheduler for scheduled tasks. Environment variables are managed using python-dotenv.

## Features
- Flask web server for handling HTTP requests
- Twilio integration for SMS messaging
- Cohere API for AI text generation or analysis
- APScheduler for scheduling background jobs
- Environment variable management with .env file

## Prerequisites
- Python 3.12+
- The following Python packages (see `requirements.txt`):
  - Flask
  - twilio
  - apscheduler
  - cohere
  - python-dotenv

## Setup
1. **Clone the repository**
	```bash
	git clone <repo-url>
	cd mamalight
	```

2. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```

3. **Configure environment variables**
	- Create a `.env` file in the project root (see example below):
	  ```env
	  TWILIO_ACCOUNT_SID='your_twilio_account_sid'
	  TWILIO_AUTH_TOKEN='your_twilio_auth_token'
	  COHERE_API_KEY='your_cohere_api_key'
	  TWILIO_PHONE_NUMBER='+1234567890'
	  ```
	- Replace the values with your actual credentials.

4. **Run the application**
	```bash
	python mamalight.py
	```

## Usage
- The Flask server will start and listen for incoming requests.
- Twilio will handle SMS sending/receiving using the credentials provided.
- Cohere API will be used for AI text processing.
- Scheduled tasks will run in the background using APScheduler.

## File Structure
- `mamalight.py`: Main application code
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (not committed to version control)
- `db.sqlite3`: SQLite database file

## Notes
- Make sure your Twilio and Cohere accounts are active and have valid API keys.
- For production, secure your `.env` file and never share your credentials.

## License
MIT (or specify your license)
