setup:
	poetry install --with dev

activate:
	poetry shell

core:
	poetry run uvicorn core.main:app --reload --port 8000

hw_agent:
	poetry run uvicorn hw_agent.main:app --reload --host 0.0.0.0 --port 9000

cli:
	poetry run colorctl --help

test:
	poetry run pytest -q

