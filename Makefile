.PHONY: install lint test security docker

install:
	python -m pip install -r requirements-dev.txt

lint:
	ruff check .

test:
	pytest --cov=app --cov-report=term-missing --cov-fail-under=85

security:
	bandit -c pyproject.toml -r app -ll
	pip-audit -r requirements.txt

docker:
	docker build -t devsecops-secure-pipeline:local .
