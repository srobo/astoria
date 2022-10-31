.PHONY: all lint type isort

CMD:=poetry run
PYMODULE:=libastoria
PYTEST_FLAGS:=-vv

all: type lint

lint:
	$(CMD) flake8 $(PYMODULE)

type:
	$(CMD) mypy $(PYMODULE)

isort:
	$(CMD) isort $(PYMODULE)

