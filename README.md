# Sprint 3 - PROJECT WEEKS 9-11 DELIVERABLE

## Project Summary
EduMate is a web-based productivity app built using **Flask**. It allows users to:

- Create and manage reminders
- Track personal progress
- Access their profile and membership information
- Visualize productivity through a dashboard

This submission covers the complete project from Sprints 2 and 3, with fully functional features.

## Project Structure
- `app.py` – Main Flask application
- `templates/` – HTML templates
- `static/` – CSS, JS, images
- `database.db` – SQLite database (if included)
- `requirements.txt` – Python dependencies

## Setup Instructions
1. Clone or download the repository.
2. Open the project folder in VS Code.
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

To run the application, open the terminal in vscode. (Make sure you are in the right folder)
Type: python app.py

Open the browser at:
http://127.0.0.1:5000

Notes

Ensure Flask and other dependencies are installed in the virtual environment.

The database is automatically updated when reminders are added, edited, or deleted.
