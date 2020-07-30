default: all


all: 
	LOGLEVEL='INFO' \
	python -m unittest discover tests test_*.py

clean: 
	LOGLEVEL='INFO' \
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
