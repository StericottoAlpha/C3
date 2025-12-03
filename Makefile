.PHONY: install clean lint lint-fix test run makemigrations migrate db-update db-reset setup hash docker-up docker-down docker-reset

install:
	pip3 install -r requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

lint:
	ruff check .

lint-fix:
	ruff check . --fix

test:
	python3 manage.py test

run:
	python3 manage.py runserver

makemigrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

db-update: makemigrations migrate

db-reset:
	rm -f db.sqlite3
	python3 manage.py migrate
	python3 manage.py seed

setup: install migrate

hash:
ifndef TARGET
	@echo "Usage: make hash TARGET=your_password"
	@echo "Example: make hash TARGET=password123"
else
	@python3 manage.py shell -c "from django.contrib.auth.hashers import make_password; print(make_password('$(TARGET)'))"
endif

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-reset:
	docker-compose down -v
	docker-compose up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	python3 manage.py migrate
	python3 manage.py seed
