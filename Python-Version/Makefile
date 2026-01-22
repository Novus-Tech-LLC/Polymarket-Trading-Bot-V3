.PHONY: install build test clean run

install:
	pip install -r requirements.txt

build:
	python build.py

test:
	python -m pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf build/ dist/ .eggs/

run:
	python -m src.main
