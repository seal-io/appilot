#Sets the default shell for executing commands as /bin/bash and specifies command should be executed in a Bash shell.
SHELL := /bin/bash

# Color codes for terminal output
COLOR_RESET=\033[0m
COLOR_CYAN=\033[1;36m
COLOR_GREEN=\033[1;32m

# Defines the targets help, install, dev-install, and run as phony targets. Phony targets are targets that are not really the name of files that are to be built. Instead, they are treated as commands.
.PHONY: help install run

#sets the default goal to help when no target is specified on the command line.
.DEFAULT_GOAL := help

#Disables echoing of commands. The commands executed by Makefile will not be printed on the console during execution.
.SILENT:

#Defines a target named help.
help:
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@echo "  help           	Return this message with usage instructions."
	@echo "  install        	Create a virtual environment and install the dependencies."
	@echo "  run            	Run Appilot."

#Defines a target named install. This target will create a virtual environment, upgrade pip and install the dependencies.
install: create-venv upgrade-pip install-dependencies farewell

#Defines a target named create-venv. This target will create a virtual environment in the .venv folder.
create-venv:
	@echo -e "$(COLOR_CYAN)Creating virtual environment...$(COLOR_RESET)" && \
	python3 -m venv .venv

#Defines a target named upgrade-pip. This target will upgrade pip to the latest version.
upgrade-pip:
	@echo -e "$(COLOR_CYAN)Upgrading pip...$(COLOR_RESET)" && \
	source .venv/bin/activate && \
	pip install --upgrade pip >> /dev/null

#Defines a target named install-dependencies. This target will install the dependencies.
install-dependencies:
	@echo -e "$(COLOR_CYAN)Installing dependencies...$(COLOR_RESET)" && \
	source .venv/bin/activate && \
	pip install -r requirements.txt >> /dev/null

#Defines a target named farewell. This target will print a farewell message.
farewell:
	@echo -e "$(COLOR_GREEN)All done!$(COLOR_RESET)"

#Defines a target named lint. This targeet will do pylint.
lint:
	git ls-files '*.py' | xargs pylint
#Defines a target named run. This target will run Appilot.
run:
	@echo -e "$(COLOR_CYAN)Running Appilot...$(COLOR_RESET)" && \
	source .venv/bin/activate && \
	python3 app.py
