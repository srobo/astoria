.PHONY: all clean lint type test test-cov isort

CMD:=poetry run
PYMODULE:=astoria
TESTS:=tests
PYTEST_FLAGS:=-vv

all: type test lint
	make -C libastoria

lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS)

type:
	$(CMD) mypy $(PYMODULE) $(TESTS)

test:
	$(CMD) pytest $(PYTEST_FLAGS) $(TESTS)

test-cov:
	$(CMD) pytest $(PYTEST_FLAGS) $(TESTS) --cov-report html

isort:
	$(CMD) isort $(PYMODULE) $(TESTS) $(EXTRACODE)

clean:
	git clean -Xdf # Delete all files in .gitignore
