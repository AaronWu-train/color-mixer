setup:
	poetry install --with dev

run-core:
	poetry run uvicorn core.main:app --reload --port 8000

run-hw:
	poetry run uvicorn hw_agent.main:app --reload --host 0.0.0.0 --port 9000

run-cli:
	poetry run colorctl --help

test:
	poetry run pytest -q

