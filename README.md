# PSSF Pension Administration System

Enhanced Django pension administration platform.

Modules:
- Member administration
- Contributions
- Interest processing
- Claims
- Withdrawals
- Trust fund accounting
- Income drawdown
- Pension payroll
- CRM tickets

## Run locally

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## Production

Uses Gunicorn + WhiteNoise and is ready for Render/PythonAnywhere configuration.
