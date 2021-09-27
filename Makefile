.PHONY: build run lint unittests tests coverage run_docker ci all

app_name = hidden_places

build:
	@docker build -t $(app_name) .

run_docker:
	@docker run -d -p 8080:80 --name $(app_name) $(app_name)

run:
	python run.py

lint:
	@echo "Linting packages and modules ..."
	@mypy app
	@pylint app
	@pylint tests
	@jinjalint app/templates

unittests:
	@echo "Running unit tests ..."
	@pytest tests/unit

tests:
	@echo "Running all tests ..."
	@pytest tests

coverage:
	@echo "Checking code coverage"
	@python -m pytest --cov=project

ci:
	@drone exec --pipeline=test

all: tests coverage lint
