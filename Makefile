# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

# ==============
# CONFIGURATIONS
# ==============
DEBUG ?= 1
PYTHON ?= python3
ARGS ?=
MAIN := uranus.main
CONFIG_DIR := ./configs/

# ============
# OUTPUT STYLE
# ============
define print_r
	@printf '\033[1;31m$(1)\033[0m\n'
endef

define print_y
	@printf '---| \033[1;33m$(1)\033[0m\n'
endef

define print_g
	@printf '---| \033[1;32m$(1)\033[0m\n'
endef

# for help target
define help_y
	@printf '\033[1;33m$(1)\033[0m\n'
endef

define help_g
	@printf '\033[1;32m $(1)\033[0m\n'
endef

.PHONY: all format format-check lint lint-fix clean help

all: clean format
	$(call print_y,Run uranus.)
	@DEBUG=$(DEBUG) CONFIG_DIR=$(CONFIG_DIR) $(PYTHON) -m $(MAIN)  $(ARGS)

# ---------| formatting with ruff
format:
	$(call print_y,Formatting files with ruff...)
	ruff format --config ./uranus.toml .

format-check:
	$(call print_y,Checking formatting with ruff..)
	ruff format --config ./uranus.toml --check .

lint:
	ruff check --config ./uranus.toml

lint-fix:
	ruff check --config ./uranus.toml --fix

clean:
	$(call print_y,Cleaning build directories and build files....)
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

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
	@echo "  MAIN          Main Python entry point"
	@echo "  ARGS          Arguments passed to the script"
	@echo
