SRCDIRS=./cli ./tests

.PHONY: test lint ci install run

test:
	python -m unittest discover ./tests

lint:
	isort $(SRCDIRS)
	autoflake -r --in-place $(SRCDIRS)
	black $(SRCDIRS)
	flake8 $(SRCDIRS) --max-line-length=88
	mypy $(SRCDIRS)

ci: lint test

install:
	python -m pip install .

run:
	python -m cli
