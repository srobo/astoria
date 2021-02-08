.PHONY: all clean docs docs-serve lint type test test-cov debian

CMD:=poetry run
PYMODULE:=astoria
TESTS:=tests
EXTRACODE:=docs/_code
SPHINX_ARGS:=docs/ docs/_build -nWE
PYTEST_FLAGS:=-vv

all: type test lint

docs:
	$(CMD) sphinx-build $(SPHINX_ARGS)

docs-serve:
	$(CMD) sphinx-autobuild $(SPHINX_ARGS)

lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS) $(EXTRACODE)

type:
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE)

test:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS) --cov-report html

isort:
	$(CMD) isort $(PYMODULE) $(TESTS) $(EXTRACODE)

setup.py:
	$(CMD) dephell deps convert --from pyproject.toml --to setup.py

debian: setup.py
	sudo mk-build-deps -ir
	debuild -uc -us

clean:
	git clean -Xdf # Delete all files in .gitignore
