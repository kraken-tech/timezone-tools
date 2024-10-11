SHELL=/bin/bash


.PHONY:dev
dev: install_python_packages


.PHONY:install_python_packages
install_python_packages: requirements.txt
	python3 -m pip install -r requirements.txt
