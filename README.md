# Flask Quiz Platform

A complete Flask quiz application with user authentication, timer-based quizzes, admin question management, and SQLite storage.

## Project structure

- `app.py` — main Flask application and route handlers
- `config.py` — application configuration
- `quiz.db` — SQLite database created automatically on first run
- `requirements.txt` — Python dependencies
- `templates/` — HTML templates for pages
- `static/css/styles.css` — responsive UI styles
- `static/js/quiz.js` — quiz timer logic

## Getting started

1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the app:
   ```powershell
   python app.py
   ```
4. Open the app in your browser at `http://127.0.0.1:5000`

## Admin login

- Visit `http://127.0.0.1:5000/admin-login`
- Admin email: one of the allowed addresses
- Admin password: the password you were provided
- No OTP is required for admin login
http://127.0.0.1:5000
## Notes

- The database file is created automatically when the app starts.
- Use the Admin page to add new quiz questions.
- The quiz page selects 5 random questions each time.
