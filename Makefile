.PHONY: install sync linearize extract compile all test clean

# Input file
INPUT := chatgpt-export.json

# Output directories
EVIDENCE_DIR := _evidence
ATOMS_DIR := _atoms
DOCS_DIR := docs

install sync:
	uv sync --extra dev

linearize:
	uv run ckx linearize --input $(INPUT) --out $(EVIDENCE_DIR)

extract:
	uv run ckx extract --input $(INPUT) --evidence $(EVIDENCE_DIR) --out $(ATOMS_DIR)

compile:
	uv run ckx compile --atoms $(ATOMS_DIR) --out $(DOCS_DIR)

all: linearize extract compile

test:
	uv run pytest tests/ -v

clean:
	rm -rf .venv
	rm -f uv.lock
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
