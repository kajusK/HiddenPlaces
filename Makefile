.PHONY: build run lint tests coverage

app_name = hidden_places

build:
	@docker build -t $(app_name) .

run:
	python run.py

lint:
	@echo "linting packages and modules ..."
	@pylint app
	@pylint tests

tests:
	@echo "running tests ..."
	@python -m pytest -v

coverage:
	@echo "Checking code coverage"
	@python -m pytest --cov=project