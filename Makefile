.PHONY: install clean lint lint-fix test run makemigrations migrate db-update db-reset setup hash docker-start docker-stop docker-reset docker-clean

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
	@echo "Resetting databases..."
	rm -f db.sqlite3
	python3 manage.py flush --no-input
	python3 manage.py migrate
	python3 manage.py seed
	@echo "Database reset complete!"

setup: install migrate

hash:
ifndef TARGET
	@echo "Usage: make hash TARGET=your_password"
	@echo "Example: make hash TARGET=password123"
else
	@python3 manage.py shell -c "from django.contrib.auth.hashers import make_password; print(make_password('$(TARGET)'))"
endif

docker-start:
	@docker volume create postgres_data 2>/dev/null || true
	@if [ -z "$$(docker ps -q -f name=c3-app-postgres)" ]; then \
		if [ -n "$$(docker ps -aq -f name=c3-app-postgres)" ]; then \
			docker start c3-app-postgres; \
		else \
			docker run -d \
				--name c3-app-postgres \
				-e POSTGRES_DB=c3_app_dev \
				-e POSTGRES_USER=c3 \
				-e POSTGRES_PASSWORD=password \
				-p 5433:5432 \
				-v postgres_data:/var/lib/postgresql/data \
				--restart unless-stopped \
				postgres:17-alpine; \
		fi \
	else \
		echo "PostgreSQL container is already running"; \
	fi

docker-stop:
	@docker stop c3-app-postgres 2>/dev/null || true

docker-reset:
	@docker stop c3-app-postgres 2>/dev/null || true
	@docker rm c3-app-postgres 2>/dev/null || true
	@docker volume rm postgres_data 2>/dev/null || true
	@docker volume create postgres_data
	@docker run -d \
		--name c3-app-postgres \
		-e POSTGRES_DB=c3_app_dev \
		-e POSTGRES_USER=c3 \
		-e POSTGRES_PASSWORD=password \
		-p 5433:5432 \
		-v postgres_data:/var/lib/postgresql/data \
		--restart unless-stopped \
		postgres:17-alpine
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	python3 manage.py migrate
	python3 manage.py seed

docker-clean:
	@docker stop c3-app-postgres 2>/dev/null || true
	@docker rm c3-app-postgres 2>/dev/null || true
	@docker volume rm postgres_data 2>/dev/null || true
	@echo "PostgreSQL container and volume removed"
