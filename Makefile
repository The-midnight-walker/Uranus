# SPDX-License-Identifier: GPL-2.0
#
# vim: set ts=8 sw=8 noet tw=80 cc=80 fo+=t :

# ==============
# CONFIGURATIONS
# ==============
DEBUG ?= 1
VENV_BIN   ?= ./.venv/bin
PYTHON     ?= $(firstword $(wildcard $(VENV_BIN)/python3) $(shell command -v python3))
RUFF_BIN   ?= $(firstword $(wildcard $(VENV_BIN)/ruff) $(shell command -v ruff))
SHFMT_BIN  ?= $(shell command -v shfmt)
SHELLCHECK_BIN ?= $(shell command -v shellcheck)
ARGS       ?=
MAIN       := uranus.main
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

define pr_err
    $(call print_r,[ERROR] $1 )
endef

.PHONY: all format format-python format-shell format-check lint lint-python lint-shell lint-fix test clean help

all: clean format build

build:
	$(call pr_info_y,Run uranus.)
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
	$(call print_y,Usage: make <target>)
	@echo
	$(call print_g,Targets:)
	@echo "  all             Run the Uranus application (cleans & formats first)"
	@echo "  build           Run the Uranus application"
	@echo "  test            Run Python unit test suite"
	@echo "  format          Format Python code (ruff) and shell scripts (shfmt)"
	@echo "  format-python   Format only Python source code with ruff"
	@echo "  format-shell    Format only shell scripts (.sh) with shfmt"
	@echo "  format-check    Check Python code formatting without modifying files"
	@echo "  lint            Check code quality for both Python and shell scripts"
	@echo "  lint-python     Lint only Python source code with ruff"
	@echo "  lint-shell      Lint only shell scripts (.sh) with shellcheck"
	@echo "  lint-fix        Automatically fix detected Python lint issues"
	@echo "  clean           Remove Python cache directories and compiled files"
	@echo "  help            Display this help message"
	@echo
