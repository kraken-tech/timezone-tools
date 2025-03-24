SHELL=/bin/bash


.PHONY:dev
dev: install_python_packages


.PHONY:install_python_packages
install_python_packages: requirements.txt
	# Install the `timezone_tools` package (in editable mode) and the development dependencies.
	python3 -m pip install -r requirements.txt -e .
