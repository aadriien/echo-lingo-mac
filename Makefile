# Echo Lingo Mac

POETRY = poetry
PYTHON = python3

VENV_DIR = .venv

.PHONY: all setup run clean

all: setup run


# Install Poetry dependencies & set up venv
setup:
	@which poetry > /dev/null || (echo "Poetry not found. Installing..."; curl -sSL https://install.python-poetry.org | python3 -)
	@$(POETRY) config virtualenvs.in-project true
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating..."; \
		$(POETRY) env use python3.11; \
		$(POETRY) install --no-root --quiet; \
	fi


# Run the main pipeline (PYTHONPATH=src so imports resolve from src/)
run:
	@PYTHONPATH=src $(POETRY) run $(PYTHON) main.py


# Clear away venv
clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV_DIR)
