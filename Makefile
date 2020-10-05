install:
	poetry install --no-dev

install-dev:
	poetry install

clean:
	isort -y
	flake8

release:
	changelog-gen

check-style:
	flake8

tests-coverage:
	pytest --cov=web_error
