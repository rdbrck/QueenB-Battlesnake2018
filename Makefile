.PHONY: clean lint test-static test bootstrap

bootstrap:
	pip install -r requirements.txt

lint:
	flake8 --config setup.cfg

clean:
	find . -type f -name "*.pyc" -delete

test-static:
	cd tests/static && python test.py

test: clean lint test-static

