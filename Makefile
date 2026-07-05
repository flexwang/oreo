VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

all: $(VENV)
	$(PYTHON) main.py

$(VENV): requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	touch $(VENV)

clean:
	rm -rf $(VENV)

.PHONY: all clean
