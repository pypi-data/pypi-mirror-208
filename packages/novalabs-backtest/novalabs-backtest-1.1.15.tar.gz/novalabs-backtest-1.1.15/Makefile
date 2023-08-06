.PHONY: all clean format lint test test_watch docker_tests help
PYTHON_VERSIONS=3.8 3.9 3.10


all: help

coverage:
	poetry run pytest --cov \
		--cov-config=marketwatch \
		--cov-report xml \
		--cov-report html \
		--cov-report term-missing:skip-covered

clean: docs_clean

docs_build:
	cd docs && poetry run make html

docs_clean:
	cd docs && poetry run make clean

docs_linkcheck:
	poetry run linkchecker docs/_build/html/index.html

format:
	poetry run black .
	poetry run ruff --select I --fix .

PYTHON_FILES=.
lint: PYTHON_FILES=.
lint_diff: PYTHON_FILES=$(shell git diff --name-only --diff-filter=d master | grep -E '\.py$$')

lint lint_diff:
	poetry run mypy $(PYTHON_FILES)
	poetry run black $(PYTHON_FILES) --check
	poetry run ruff .

test:
	poetry run pytest tests

test_watch:
	poetry run ptw --now . -- tests/unit_tests

docker_tests:
	docker build -t nova-backtest-image:test .
	docker run --rm nova-backtest-image:test

help:
	@echo '----'
	@echo 'coverage            - run unit tests and generate coverage report'
	@echo 'docs_build          - build the documentation'
	@echo 'docs_clean          - clean the documentation build artifacts'
	@echo 'docs_linkcheck      - run linkchecker on the documentation'
	@echo 'format              - run code formatters'
	@echo 'lint                - run linters'
	@echo 'test                - run unit tests'
	@echo 'test_watch          - run unit tests in watch mode'
	@echo 'docker_tests        - run unit tests in docker'

# test_python_versions:
# 	for v in $(PYTHON_VERSIONS); do \
# 		python$$v -m venv venv$$v; \
# 		source venv$$v/bin/activate; \
# 		pip install poetry; \
# 		poetry install; \
# 		poetry run pytest tests; \
# 		deactivate; \
# 	done