# SPDX-License-Identifier: GPL-2.0

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

# for help target
define print_y
    @printf '\033[1;33m$(1)\033[0m\n'
endef

define print_g
    @printf '\033[1;32m $(1)\033[0m\n'
endef

define pr_info_y
	@echo -n "---| "
    $(call print_y,$1 )
endef

define pr_info_g
	@echo -n "---| "
    $(call print_g,$1 )
endef

define pr_err
    $(call print_r,[ERROR] $1 )
endef

.PHONY: all format format-python format-shell format-check lint lint-python lint-shell lint-fix test clean help

all: clean format build

build:
	$(call pr_info_y,Run uranus.)
	@DEBUG=$(DEBUG) CONFIG_DIR=$(CONFIG_DIR) $(PYTHON) -m $(MAIN)  $(ARGS)

test:
	$(call pr_info_y,Running test suite...)
	@$(PYTHON) -m unittest discover tests/

# ---------| formatting with ruff & shfmt
format: format-python format-shell

format-python:
ifeq ($(RUFF_BIN),)
	$(call pr_err,ruff not found. Please install ruff to format Python files.)
	@exit 1
else
	$(call pr_info_y,Formatting Python files with ruff...)
	$(RUFF_BIN) format --config ./uranus.toml .
endif

format-shell:
	$(call pr_info_y,Formatting shell scripts with shfmt...)
ifneq ($(SHFMT_BIN),)
	@shell_files=$$(find . -name "*.sh" -not -path "*/.*"); \
	if [ -n "$$shell_files" ]; then \
		$(SHFMT_BIN) -w $$shell_files; \
	else \
		echo "No shell scripts found."; \
	fi
else
	$(call pr_err, shfmt not found. Shell formatting skipped.)
endif

format-check:
ifeq ($(RUFF_BIN),)
	$(call pr_err,ruff not found. Please install ruff to check formatting.)
	@exit 1
else
	$(call pr_info_y,Checking formatting with ruff..)
	$(RUFF_BIN) format --config ./uranus.toml --check .
endif

# ---------| linting with ruff & shellcheck
lint: lint-python lint-shell

lint-python:
ifeq ($(RUFF_BIN),)
	$(call pr_err,ruff not found. Please install ruff to lint Python files.)
	@exit 1
else
	$(RUFF_BIN) check --config ./uranus.toml
endif

lint-shell:
ifneq ($(SHELLCHECK_BIN),)
	$(call pr_info_y,Linting shell scripts with shellcheck...)
	@shell_files=$$(find . -name "*.sh" -not -path "*/.*"); \
	if [ -n "$$shell_files" ]; then \
		$(SHELLCHECK_BIN) $$shell_files; \
	else \
		echo "No shell scripts found."; \
	fi
else
	$(call pr_err, shellcheck not found. Shell linting skipped.)
endif

lint-fix:
ifeq ($(RUFF_BIN),)
	$(call pr_err,ruff not found. Please install ruff to fix lint issues.)
	@exit 1
else
	$(RUFF_BIN) check --config ./uranus.toml --fix
endif

clean:
	$(call pr_info_y,Cleaning build directories and build files....)
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

help:
	@echo
	$(call print_g,██╗   ██╗ ██████╗   █████╗  ███╗   ██╗ ██╗   ██╗ ███████╗)
	$(call print_g,██║   ██║ ██╔══██╗ ██╔══██╗ ████╗  ██║ ██║   ██║ ██╔════╝)
	$(call print_g,██║   ██║ ██████╔╝ ███████║ ██╔██╗ ██║ ██║   ██║ ███████╗)
	$(call print_g,██║   ██║ ██╔══██╗ ██╔══██║ ██║╚██╗██║ ██║   ██║ ╚════██║)
	$(call print_g,╚██████╔╝ ██║  ██║ ██║  ██║ ██║ ╚████║ ╚██████╔╝ ███████║)
	$(call print_g, ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝  ╚═════╝  ╚══════╝)
	$(call print_r,\n      _ _ _ Hardening Debian( 13 - Trixie ) platforms _ _ _)
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
	$(call print_g,Variables:)
	@echo "  DEBUG           Debug flag passed to the application (default: 1)"
	@echo "  PYTHON          Python interpreter to use (default: python3)"
	@echo "  MAIN            Main Python entry point module (default: uranus.main)"
	@echo "  CONFIG_DIR      Configuration directory path (default: ./configs/)"
	@echo "  ARGS            Additional arguments passed to the script"
	@echo "  RUFF_BIN        Path/command for the ruff binary"
	@echo "  SHFMT_BIN       Path/command for the shfmt binary"
	@echo "  SHELLCHECK_BIN  Path/command for the shellcheck binary"
	@echo