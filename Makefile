.PHONY: install run test lint clean

install:
	pip install -r requirements.txt

run:
	FLASK_APP=run.py FLASK_ENV=development flask run

test:
	pytest tests/ -v

test-fast:
	pytest tests/ -x -q

lint:
	flake8 app/ tests/ --max-line-length=120

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f instance/tasks.db
