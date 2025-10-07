# Event Registration System

## Project Description

The Event Registration System is a web application built with Flask to facilitate the creation, management, and registration for events. Users can register, log in, browse available events, and enroll in them online. Admins can create events, view registrants, and manage event details through an intuitive dashboard. The application features secure user authentication, event registration tracking, and administrative oversight.

## Technologies Used

- Python 3.x
- Flask web framework
- SQLite database
- HTML, CSS, JavaScript (with Bootstrap 5 for UI)
- Werkzeug for password hashing
- python-dotenv for environment variable management

## Setup Instructions

### Prerequisites

- Python 3.7 or higher installed
- Git (optional for cloning the repo)
- SQLite (optional for managing the database file)

### Steps to Run

1. **Clone the repository (or download source code):**
```bash
git clone https://github.com/Sricharan-V/event_registration.git
cd event_registration
```


2. **Create and activate a virtual environment:**

For Windows (PowerShell):
```bash
python -m venv venv
venv\Scripts\activate
```


For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```


3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a `.env` file in project root and add:
```
SECRET_KEY=your_secret_key_here
ADMIN_PASSWORD=your_admin_password_here
```


5. **Initialize the database:**

Run the database initialization script(Only use it again if you want the complete database to be reset):
```bash
python init_db.py
```

6. **Run the Flask app:**
```bash
python app.py
```
or
```bash
flask run
```

7. **Access the application:**

Open [http://localhost:5000](http://localhost:5000) in your browser.
