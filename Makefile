install:
	poetry install

package-install:
	python3 -m pip install --user dist/hexlet_code-0.1.0-py3-none-any.whl

package-reinstall:
	python3 -m pip install . --force-reinstall

lint:
	poetry run flake8

build:
	./build.sh

publish:
	poetry publish --dry-run

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

start-debug:
	poetry run flask --app page_analyzer.app:app --debug run --port 8000
