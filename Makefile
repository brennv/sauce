install:
	python3 -m venv .env; \
	source .env/bin/activate; \
	pip install --upgrade pip
	pip install -r requirements.txt; \

run:
	source .env/bin/activate; \
	python sauce/cli.py; \

test:
	source .env/bin/activate; \
	py.test -q tests; \

freeze:
	source .env/bin/activate; \
	pip freeze > requirements.txt; \
