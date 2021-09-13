.PHONY: build run lint tests coverage run_docker

app_name = hidden_places

build:
	@docker build -t $(app_name) .

run_docker:
	@docker run -d -p 8080:80 --name $(app_name) $(app_name)

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
