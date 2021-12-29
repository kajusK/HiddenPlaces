.PHONY: run lint unit functional tests ci all

run_docker:
	@docker-compose up

run:
	flask run

lint:
	@echo "Linting packages and modules ..."
	@flake8 app
	@mypy app
	@pylint app
	@pylint tests

unit:
	@echo "Running unit tests ..."
	@pytest tests/unit

functional:
	@echo "Running functional tests ..."
	@pytest tests/functional
	@pytest tests/integration

tests:
	@echo "Running all tests ..."
	@pytest tests

ci:
	@drone exec

all: lint tests
