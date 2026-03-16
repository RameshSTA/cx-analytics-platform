# ============================================================
# Customer Experience Analytics Platform — Makefile
# ============================================================
# Usage:
#   make install        Install all dependencies into a virtual environment
#   make pipeline       Run all 5 notebooks end-to-end (requires datasets)
#   make eda            Run only the EDA notebook
#   make segmentation   Run Module 1 — Segmentation + CLV
#   make forecasting    Run Module 2 — Forecasting
#   make nlp            Run Module 3 — NLP Sentiment Pipeline
#   make abtesting      Run Module 4 — A/B Testing + Causal Inference
#   make test           Run the unit test suite (pytest)
#   make lint           Lint source code with ruff
#   make format         Auto-format source code with ruff
#   make clean          Remove generated outputs (keeps raw data)
#   make help           Show this help message
# ============================================================

PYTHON      := python3
VENV        := .venv
VENV_BIN    := $(VENV)/bin
PIP         := $(VENV_BIN)/pip
PYTEST      := $(VENV_BIN)/pytest
JUPYTER     := $(VENV_BIN)/jupyter
RUFF        := $(VENV_BIN)/ruff
NOTEBOOKS   := notebooks
OUTPUTS     := outputs

.DEFAULT_GOAL := help

.PHONY: help install pipeline eda segmentation forecasting nlp abtesting test lint format clean

help:
	@echo ""
	@echo "  Customer Experience Analytics Platform"
	@echo "  ===================================="
	@echo ""
	@echo "  make install        Create .venv and install all dependencies"
	@echo "  make pipeline       Run all 5 notebooks end-to-end"
	@echo "  make eda            Run 00_EDA.ipynb only"
	@echo "  make segmentation   Run 01_segmentation.ipynb (Module 1)"
	@echo "  make forecasting    Run 02_forecasting.ipynb (Module 2)"
	@echo "  make nlp            Run 03_nlp_pipeline.ipynb (Module 3)"
	@echo "  make abtesting      Run 04_ab_testing.ipynb (Module 4)"
	@echo "  make test           Run pytest unit tests"
	@echo "  make lint           Lint src/ with ruff"
	@echo "  make format         Auto-format src/ with ruff"
	@echo "  make clean          Remove generated outputs (charts, reports)"
	@echo ""

# ── Install ──────────────────────────────────────────────────────────────────
install:
	@echo "→ Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "→ Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Installation complete. Activate with: source $(VENV)/bin/activate"

# ── Notebooks ─────────────────────────────────────────────────────────────────
eda:
	@echo "→ Running 00_EDA.ipynb..."
	$(JUPYTER) nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=600 \
		--output $(NOTEBOOKS)/00_EDA_executed.ipynb \
		$(NOTEBOOKS)/00_EDA.ipynb
	@echo "✓ EDA complete"

segmentation:
	@echo "→ Running 01_segmentation.ipynb (Module 1)..."
	$(JUPYTER) nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=600 \
		--output $(NOTEBOOKS)/01_segmentation_executed.ipynb \
		$(NOTEBOOKS)/01_segmentation.ipynb
	@echo "✓ Module 1 (Segmentation + CLV) complete"

forecasting:
	@echo "→ Running 02_forecasting.ipynb (Module 2)..."
	$(JUPYTER) nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=1200 \
		--output $(NOTEBOOKS)/02_forecasting_executed.ipynb \
		$(NOTEBOOKS)/02_forecasting.ipynb
	@echo "✓ Module 2 (Forecasting) complete"

nlp:
	@echo "→ Running 03_nlp_pipeline.ipynb (Module 3)..."
	$(JUPYTER) nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=1800 \
		--output $(NOTEBOOKS)/03_nlp_pipeline_executed.ipynb \
		$(NOTEBOOKS)/03_nlp_pipeline.ipynb
	@echo "✓ Module 3 (NLP Pipeline) complete"

abtesting:
	@echo "→ Running 04_ab_testing.ipynb (Module 4)..."
	$(JUPYTER) nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=600 \
		--output $(NOTEBOOKS)/04_ab_testing_executed.ipynb \
		$(NOTEBOOKS)/04_ab_testing.ipynb
	@echo "✓ Module 4 (A/B Testing + Causal Inference) complete"

pipeline: eda segmentation forecasting nlp abtesting
	@echo ""
	@echo "✓ Full pipeline complete. Outputs in $(OUTPUTS)/"

# ── Testing ───────────────────────────────────────────────────────────────────
test:
	@echo "→ Running unit tests..."
	$(PYTEST) tests/ -v --tb=short
	@echo "✓ Tests complete"

test-coverage:
	@echo "→ Running tests with coverage report..."
	$(PYTEST) tests/ -v --tb=short --cov=src --cov-report=term-missing
	@echo "✓ Coverage report complete"

# ── Code Quality ─────────────────────────────────────────────────────────────
lint:
	@echo "→ Running ruff linter on src/..."
	$(RUFF) check src/
	@echo "✓ Lint complete"

format:
	@echo "→ Auto-formatting src/ with ruff..."
	$(RUFF) format src/
	@echo "✓ Format complete"

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean:
	@echo "→ Removing generated outputs..."
	rm -f $(OUTPUTS)/charts/*.png
	rm -f $(OUTPUTS)/reports/*.md
	rm -f $(NOTEBOOKS)/*_executed.ipynb
	@echo "✓ Clean complete (raw data preserved)"

clean-all: clean
	@echo "→ Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✓ Full clean complete"
