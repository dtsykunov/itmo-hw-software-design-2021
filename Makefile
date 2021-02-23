SRCDIRS=./cli ./tests

.PHONY: test lint check ci install run

test:
	python -m unittest discover ./tests

lint:
	isort $(SRCDIRS) --profile black
	autoflake -r --in-place $(SRCDIRS)
	black $(SRCDIRS)
	flake8 $(SRCDIRS) --max-line-length=88 --ignore=E203
	mypy $(SRCDIRS)

check:
	isort $(SRCDIRS) --profile black --check
	autoflake -r --in-place $(SRCDIRS) --check
	black $(SRCDIRS) --check
	flake8 $(SRCDIRS) --max-line-length=88 --ignore=E203
	mypy $(SRCDIRS)

ci: lint test

install:
	python -m pip install .

run:
	python -m cli
