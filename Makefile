.PHONY: help install migrate createsuperuser seed test run lint clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make migrate        - Run database migrations"
	@echo "  make createsuperuser - Create admin user"
	@echo "  make seed          - Seed test data"
	@echo "  make test          - Run tests"
	@echo "  make run           - Run development server"
	@echo "  make lint          - Run linters"
	@echo "  make clean         - Clean temporary files"

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

createsuperuser:
	python manage.py createsuperuser

seed:
	python manage.py seed_data

test:
	python manage.py test

run:
	python manage.py runserver

lint:
	pylint dashboard/
	black dashboard/ --check
	isort dashboard/ --check-only

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
