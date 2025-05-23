setup:
	poetry install --with dev

activate:
	eval "$(poetry env activate)"

core:
	poetry run uvicorn core.main:app --reload --port 8000

hw_agent:
	poetry run uvicorn hw_agent.main:app --reload --host 0.0.0.0 --port 9000

test:
	poetry run pytest -q

.PHONY: setup activate core hw_agent cli test
