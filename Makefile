.PHONY: all clean docs docs-serve lint type test test-cov

CMD:=poetry run
PYMODULE:=astoria
TESTS:=tests
EXTRACODE:=docs/_code

all: type test lint

docs:
	$(CMD) sphinx-build docs/ docs/_build -nWE

docs-serve: docs
	$(CMD) python3 -m http.server --directory docs/_build

lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS) $(EXTRACODE)

type:
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE)

test:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report html

isort:
	$(CMD) isort $(PYMODULE) $(TESTS) $(EXTRACODE)

clean:
	git clean -Xdf # Delete all files in .gitignore
