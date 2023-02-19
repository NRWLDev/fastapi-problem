install:
	poetry install --no-dev

install-dev:
	poetry install

release:
	changelog-gen

check-style:
	ruff .

tests-coverage:
	pytest --cov=web_error
