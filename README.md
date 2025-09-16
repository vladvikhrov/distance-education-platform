# distance Education Platform

## Installation Instructions

1. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Apply migrations and create superuser**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

Access the app at `http://127.0.0.1:8000`.

4. Meke .env file.
   Make your SECRET_KEY for django