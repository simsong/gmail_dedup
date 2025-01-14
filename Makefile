################################################################
# Create the virtual enviornment for testing and CI/CD
ACTIVATE   = . venv/bin/activate
PY=python3.11
PYTHON=$(ACTIVATE) ; $(PY)
PIP_INSTALL=$(PYTHON) -m pip install --no-warn-script-location
ETC=deploy/etc

run: venv/pyvenv.cfg remove_apple_autosave.py
	$(PYTHON) remove_apple_autosave.py

venv/pyenv.cfg: venv/pyvenv.cfg
	@echo install venv for the development environment
	$(PY) -m venv venv
	$(PYTHON) -m pip install --upgrade pip
	if [ -r requirements.txt ]; then $(PIP_INSTALL) -r requirements.txt ; fi

.PHONY: run
