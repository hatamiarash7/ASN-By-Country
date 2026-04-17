# AI Coding Agent Instructions for ASN-By-Country

This file provides essential guidance for AI coding agents working in this repository. It summarizes build, test, and run commands, project structure, and key conventions to ensure agents are immediately productive.

## Project Overview

- **Purpose:** Scrape ASN, IPv4, and IPv6 allocation data by country code from RIR delegation statistics.
- **Language:** Python 3.11+
- **CLI Entrypoint:** `src/cli.py` (exposed as `asn-by-country` via pyproject.toml)
- **Output:** Results are written to the `output_data/` directory in various CSV and text formats.

## Build, Test, and Run Commands

- **Install dependencies (recommended):**
  - `make deps` (creates venv, installs all requirements)
- **Run the application:**
  - `make run ARGS="IR US"` (replace ARGS as needed)
  - Or: `python main.py <country_code_1> <country_code_2> ... [options]`
  - Or: `python -m src.cli <country_code_1> <country_code_2> ... [options]`
- **Run tests:**
  - `make test` (unit tests)
  - `make test-cov` (with coverage)
- **Lint and format:**
  - `make lint` (ruff)
  - `make format` (ruff)
  - `make type-check` (mypy)
- **Docker:**
  - `make docker-build` (build image)
  - `make docker-run ARGS="IR"` (run in Docker)

## Project Structure

- `src/` — Main source code
- `tests/` — Unit tests
- `output_data/` — Output files
- `Makefile` — All main dev commands
- `pyproject.toml` — Project config, CLI entrypoint

## Key Conventions

- Use Makefile targets for all common tasks.
- All outputs are written to `output_data/`.
- CLI arguments follow the patterns in the README.
- Use virtual environments for Python dependencies.
- Code style enforced by ruff; type checking by mypy.

## Documentation

- See [README.md](README.md) for detailed usage, examples, and project structure.

---

**Tip:** If you are an AI agent, always prefer Makefile targets for setup, testing, and running the application. Link to this file and the README for further details.
