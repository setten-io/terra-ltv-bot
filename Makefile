all: fmt flake8 mypy coverage

fmt:
	poetry run isort terra_ltv_bot
	poetry run black terra_ltv_bot

flake8:
	poetry run flake8 terra_ltv_bot

mypy:
	poetry run mypy --ignore-missing-imports --follow-imports=silent --show-column-numbers terra_ltv_bot

test:
	poetry run coverage run --source terra_ltv_bot -m pytest

coverage: test
	poetry run coverage report

htmlcov: test
	poetry run coverage html
	open htmlcov/index.html

.PHONY: fmt flake8 mypy test coverage htmlcov all 
