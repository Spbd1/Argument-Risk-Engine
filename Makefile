.PHONY: install test run-backend run-frontend dev evaluate import-taxonomy export-taxonomy

install:
	python -m pip install -e .[dev]
	cd frontend && npm install

test:
	python -m compileall backend engine tests
	pytest
	ruff check backend engine tests scripts

run-backend:
	python scripts/run_backend.py

run-frontend:
	python scripts/run_frontend.py

dev:
	python scripts/dev.py --install --run --open

evaluate:
	python scripts/run_evaluation.py

import-taxonomy:
	python scripts/import_taxonomy_excel.py

export-taxonomy:
	python scripts/export_taxonomy_excel.py
