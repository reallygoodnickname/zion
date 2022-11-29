.PHONY: build clean tests

# Virtual environment directory
VENV_PATH=venv

# Create virtual environment
build:
	@echo "Creating virtual environment..."
	@virtualenv -q $(VENV_PATH) && . $(VENV_PATH)/bin/activate && pip install -qr requirements.txt 

# Destroy virtual environment
clean:
	@echo "Cleaning virtual environment..."
	@rm -rf $(VENV_PATH) htmlcov .coverage

tests: 
	@. $(VENV_PATH)/bin/activate && \
	bandit -r zion/ 
