.PHONY: test run check

SRCDIRS=./cli ./tests
test:
	python -m unittest discover ./tests

lint:
	isort $(SRCDIRS)
	black $(SRCDIRS)
	# flake8 $(SRCDIRS)
	# mypy $(SRCDIRS)

check: lint test

run:
	python -m cli
