# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

include utils.mk

# Configurations
PYTHON ?= python3
MAIN := uranus.main

all: clean format
	$(call print_y,Run uranus.)
	$(PYTHON) -m $(MAIN)

# ---------| formating with ruff
format:
	$(call print_y,Fromating files with ruff...)
	ruff format --config ./uranus.toml

format-check:
	$(call print_y,Check fromating ruff file configuration)
	ruff format --config ./uranus.toml --check .

lint:
	ruff check --config ./uranus.toml

lint-fix:
	ruff check --config ./uranus.toml --fix

clean:
	$(call print_y,Cleaning build directories and build files....)
	find . -name "__pycache__" -type d -exec rm -rf {} +

help:
	$(call print_r,\n      X_ _ _ Uranus - Hardening Debian platforms _ _ _X)
	@echo
	$(call help_y,Usage: make <target>)
	@echo
	$(call help_g,Targets:)
	@echo "  all           Run the Uranus application"
	@echo "  format        Format the Python source code with Ruff"
	@echo "  format-check  Check Python code formatting without modifying files"
	@echo "  clean         Remove Python cache directories"
	@echo "  help          Display this help message"
	@echo "  lint          Check Python code with Ruff"
	@echo "  lint-fix      Fix automatically detected lint issues"
	@echo
	$(call help_g,Variables:)
	@echo "  PYTHON        Python interpreter to use (default: python3)"
	@echo "  ROOT          Project root directory"
	@echo "  SRC           Python source directory"
	@echo "  MAIN          Main Python entry point"
	@echo
