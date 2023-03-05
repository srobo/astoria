.PHONY: all clean docs docs-serve lint lint-fix type test test-cov

CMD:=poetry run
PYMODULE:=astoria
TESTS:=tests
EXTRACODE:=docs/_code
SPHINX_ARGS:=docs/ docs/_build -nWE
PYTEST_FLAGS:=-vv
EXCLUDED_PATHS:=tests/data/execute_code

all: type test lint

docs:
	$(CMD) sphinx-build $(SPHINX_ARGS)

docs-serve:
	$(CMD) sphinx-autobuild $(SPHINX_ARGS)

lint:
	$(CMD) ruff $(PYMODULE) $(TESTS) $(EXTRACODE) --exclude $(EXCLUDED_PATHS)
	$(CMD) black --check $(PYMODULE) $(TESTS) $(EXTRACODE) --exclude $(EXCLUDED_PATHS)

lint-fix:
	$(CMD) ruff --fix $(PYMODULE) $(TESTS) $(EXTRACODE) --exclude $(EXCLUDED_PATHS)
	$(CMD) black $(PYMODULE) $(TESTS) $(EXTRACODE) --exclude $(EXCLUDED_PATHS)

type:
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE) --exclude $(EXCLUDED_PATHS)

test:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS) --cov-report html

clean:
	git clean -Xdf # Delete all files in .gitignore
