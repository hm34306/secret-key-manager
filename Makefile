.PHONY: format pip-install pi 



fmt: 
	ruff format

test:
	pytest --junit-xml=pytest-results.xml tests -s

coverage:
	pytest --cov-report html --cov-report term --cov phab_commons tests -s

verify: fmt test

pip-install:
	uv pip install .

pi: pip-install
