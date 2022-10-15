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
	@rm -rf $(VENV_PATH) htmlcov

tests: clean build
	@source $(VENV_PATH)/bin/activate && \
	coverage run -m unittest discover -vs tests/ && \
	coverage report && \
   	coverage html && \
	bandit -r zion/ 
