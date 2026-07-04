VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ARGS ?=

run: $(VENV)
	$(PYTHON) main.py $(ARGS)

$(VENV): requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	touch $(VENV)

clean:
	rm -rf $(VENV)

.PHONY: run clean
