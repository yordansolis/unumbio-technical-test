.PHONY: install run test lint format

install:
	uv sync && uv run playwright install chromium

run:
	uv run python main.py

test:
	uv run pytest tests/

lint:
	uv run ruff check .

format:
	uv run ruff format .
