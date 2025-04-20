PY_FILES := $(shell git ls-files --format='%(path)' *.py)

.SILENT:
.PHONY: fix 
fix:
	ruff check $(PY_FILES) --fix

.PHONY: lint
lint:
	ruff check $(PY_FILES)

.PHONY: lint
fmt: 
	ruff format $(PY_FILES)

.PHONY: test
test:
	pytest --junit-xml=pytest-results.xml tests -s

.PHONY: coverage 
coverage:
	pytest --cov-report html --cov-report term --cov phab_commons tests -s

.PHONY: verify 
verify: lint fmt test

.PHONY: pip-install
pip-install:
	uv pip install -e ".[all]"

.PHONY: pi
pi: pip-install
