.PHONY: build clean

# Virtual environment directory
VENV_PATH=venv

# Create virtual environment
build:
	@echo "Creating virtual environment..."
	@virtualenv $(VENV_PATH) && . $(VENV_PATH)/bin/activate && pip install -r requirements.txt

# Destroy virtual environment
clean:
	@echo "Cleaning virtual environment..."
	@rm -rf $(VENV_PATH)
