.PHONY: install sync linearize extract compile consolidate all test clean discover-topics assign-topics topics all-with-topics all-15 topics-15 help

# Input file (can be overridden: make INPUT=myfile.json)
INPUT := chatgpt-export.json

# Output directories (can be overridden)
EVIDENCE_DIR := _evidence
ATOMS_DIR := _atoms
DOCS_DIR := docs
OUTPUT_DIR := output

# Topic modeling outputs
TOPIC_REGISTRY := $(OUTPUT_DIR)/topic_registry.json

# 15 conversations specific directories
EVIDENCE_DIR_15 := _evidence_15
ATOMS_DIR_15 := _atoms_15
DOCS_DIR_15 := docs_15
OUTPUT_DIR_15 := output_15
INPUT_15 := claude-conversations/15/all_conversations.json
TOPIC_REGISTRY_15 := $(OUTPUT_DIR_15)/topic_registry.json

install sync:
	uv sync --extra dev

linearize:
	uv run ckx linearize --input $(INPUT) --out $(EVIDENCE_DIR) $(if $(LIMIT),--limit $(LIMIT))

extract:
	uv run ckx extract --input $(INPUT) --evidence $(EVIDENCE_DIR) --out $(ATOMS_DIR) $(if $(LIMIT),--limit $(LIMIT))

compile:
	uv run ckx compile --atoms $(ATOMS_DIR) --out $(DOCS_DIR)

consolidate:
	uv run ckx consolidate --atoms $(ATOMS_DIR) --docs $(DOCS_DIR) --out $(OUTPUT_DIR)

discover-topics:
	uv run ckx discover-topics --input $(INPUT) --atoms $(OUTPUT_DIR)/project --out $(OUTPUT_DIR) $(if $(LIMIT),--limit $(LIMIT))

assign-topics:
	uv run ckx assign-topics --input $(INPUT) --atoms $(OUTPUT_DIR)/project --registry $(TOPIC_REGISTRY) --out $(OUTPUT_DIR) $(if $(LIMIT),--limit $(LIMIT))

topics: discover-topics assign-topics

all: linearize extract compile consolidate

all-with-topics: all topics

# 15 conversations targets
linearize-15:
	uv run ckx linearize --input $(INPUT_15) --out $(EVIDENCE_DIR_15)

extract-15:
	uv run ckx extract --input $(INPUT_15) --evidence $(EVIDENCE_DIR_15) --out $(ATOMS_DIR_15)

compile-15:
	uv run ckx compile --atoms $(ATOMS_DIR_15) --out $(DOCS_DIR_15)

consolidate-15:
	uv run ckx consolidate --atoms $(ATOMS_DIR_15) --docs $(DOCS_DIR_15) --out $(OUTPUT_DIR_15)

discover-topics-15:
	uv run ckx discover-topics --input $(INPUT_15) --atoms $(OUTPUT_DIR_15)/project --out $(OUTPUT_DIR_15)

assign-topics-15:
	uv run ckx assign-topics --input $(INPUT_15) --atoms $(OUTPUT_DIR_15)/project --registry $(TOPIC_REGISTRY_15) --out $(OUTPUT_DIR_15)

topics-15: discover-topics-15 assign-topics-15

all-15: linearize-15 extract-15 compile-15 consolidate-15

all-with-topics-15: all-15 topics-15

help:
	@echo "Main pipeline targets:"
	@echo "  make all              - Run full pipeline: linearize → extract → compile → consolidate"
	@echo "  make all-with-topics  - Run full pipeline + topic modeling"
	@echo "  make topics           - Run topic discovery + assignment (requires consolidate first)"
	@echo ""
	@echo "Individual step targets:"
	@echo "  make linearize        - Linearize conversations to markdown"
	@echo "  make extract          - Extract knowledge atoms"
	@echo "  make compile          - Compile documentation"
	@echo "  make consolidate      - Consolidate per-conversation outputs"
	@echo "  make discover-topics  - Discover topics using BERTopic"
	@echo "  make assign-topics    - Assign topics to conversations"
	@echo ""
	@echo "15 conversations targets:"
	@echo "  make all-15              - Run full pipeline on 15 conversations"
	@echo "  make all-with-topics-15  - Run full pipeline + topics on 15 conversations"
	@echo "  make topics-15           - Run topic modeling on 15 conversations"
	@echo ""
	@echo "Other targets:"
	@echo "  make test            - Run test suite"
	@echo "  make clean           - Clean build artifacts"
	@echo ""
	@echo "Override defaults:"
	@echo "  make INPUT=myfile.json EVIDENCE_DIR=_my_evidence linearize"
	@echo "  make INPUT=myfile.json LIMIT=50 all-with-topics"

test:
	uv run pytest tests/ -v

clean:
	rm -rf .venv
	rm -f uv.lock
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
