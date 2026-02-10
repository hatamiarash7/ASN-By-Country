# ASN By Country

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub release](https://img.shields.io/github/release/hatamiarash7/ASN-By-Country.svg)](https://GitHub.com/hatamiarash7/ASN-By-Country/releases/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A Python tool to scrape ASN (Autonomous System Number), IPv4, and IPv6 allocation data by country code from RIR delegation statistics.

## Features

- Fetch network data for any country using ISO 3166-1 alpha-2 codes
- Support for ASN, IPv4, and IPv6 data types
- Multi-threaded fetching for improved performance
- Clean data output in CSV and text formats
- Rich console output with progress tracking
- Docker support for containerized execution

Data source: [RIR Delegations & RIPE NCC Allocations](https://www-public.imtbs-tsp.eu/~maigron/RIR_Stats/index.html)

## Installation

### Using Make (recommended)

```bash
# Clone the repository
git clone https://github.com/hatamiarash7/ASN-By-Country.git
cd ASN-By-Country

# Create virtual environment and install all dependencies
make deps
```

### Using pip

```bash
pip install -r requirements.txt
```

### Using Docker

```bash
docker build -t asn-by-country .
```

## Usage

```bash
python main.py <country_code_1> <country_code_2> ... [options]

# Or using the module
python -m src.cli <country_code_1> <country_code_2> ... [options]
```

### Optional Arguments

- `-d, --data-type <type>`:
  Specify which type of data to fetch. The options are:
  - `asn`: Retrieve only AS numbers (default).
  - `ipv4`: Retrieve only IPv4 addresses.
  - `ipv6`: Retrieve only IPv6 addresses.
  - `all`: Retrieve AS numbers, IPv4 addresses, and IPv6 addresses.

- `-w, --max-workers <N>`: Maximum concurrent workers (default: 5)
- `-q, --quiet`: Suppress progress output
- `-v, --version`: Show version

## Examples

```bash
# Fetch ASN data for multiple countries
python main.py IR US FR

# Fetch only ASN data
python main.py IR --data-type asn

# Fetch all data types
python main.py IR US --data-type all

# Using quiet mode with more workers
python main.py IR US DE --quiet --max-workers 10
```

## Using Makefile

```bash
# Create virtual environment and install dependencies
make deps

# Run the program
make run ARGS="US"
make run ARGS="IR US DE --data-type all"

# Run linters and type checker
make check

# Run tests with coverage
make test-cov

# Clean outputs
make clean

# Show all available targets
make help
```

### Run with Docker

```bash
docker run --rm -v ./results:/app/output_data hatamiarash7/asn-by-country:latest <country_code_1> <country_code_2> ... [options]
```

Using makefile:

```bash
make docker-run ARGS="IR"
make docker-run ARGS="US DE"
```

Build docker image only:

```bash
make docker-build
```

## Result

The output will be generated in the `output_data` directory:

| File Name                 | Description                                                       |
| ------------------------- | ----------------------------------------------------------------- |
| `{Country}_asn_list.csv`  | Contains a list of ASN delegations for the specified country.     |
| `{Country}_ipv4_list.csv` | Contains IPv4-specific ASN delegations for the specified country. |
| `{Country}_ipv6_list.csv` | Contains IPv6-specific ASN delegations for the specified country. |
| `{Country}_ipv4.rsc`      | Contains IPv4-specific MikroTik script for the specified country. |
| `{Country}_ipv6.rsc`      | Contains IPv6-specific MikroTik script for the specified country. |
| `asn_ranges.txt`          | Contains a list of all ASN ranges across countries.               |
| `ipv4_ranges.txt`         | Contains a list of all IPv4 ranges.                               |
| `ipv6_ranges.txt`         | Contains a list of all IPv6 ranges.                               |

## Development

### Project Structure

```text
ASN-By-Country/
├── src/                    # Source code
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration constants
│   ├── mikrotik.py         # Mikrotik rsc generator
│   ├── models.py           # Data models
│   ├── scraper.py          # Web scraping logic
│   └── storage.py          # File storage operations
├── tests/                  # Unit tests
├── Dockerfile
├── Makefile
├── pyproject.toml          # Project configuration
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

### Available Make Targets

| Target                       | Description                 |
| ---------------------------- | --------------------------- |
| `make help`                  | Show all available targets  |
| `make deps`                  | Install all dependencies    |
| `make run ARGS="..."`        | Run the application         |
| `make lint`                  | Run all linters             |
| `make format`                | Format code                 |
| `make type-check`            | Run type checking           |
| `make check`                 | Run all code quality checks |
| `make test`                  | Run tests                   |
| `make test-cov`              | Run tests with coverage     |
| `make test-junit`            | Run tests with JUnit report |
| `make docker-build`          | Build Docker image          |
| `make docker-run ARGS="..."` | Run in Docker               |
| `make clean-all`             | Remove all generated files  |

---

## Support 💛

[![Donate with Bitcoin](https://img.shields.io/badge/Bitcoin-bc1qmmh6vt366yzjt3grjxjjqynrrxs3frun8gnxrz-orange)](https://donatebadges.ir/donate/Bitcoin/bc1qmmh6vt366yzjt3grjxjjqynrrxs3frun8gnxrz) [![Donate with Ethereum](https://img.shields.io/badge/Ethereum-0x0831bD72Ea8904B38Be9D6185Da2f930d6078094-blueviolet)](https://donatebadges.ir/donate/Ethereum/0x0831bD72Ea8904B38Be9D6185Da2f930d6078094)

<div><a href="https://payping.ir/@hatamiarash7"><img src="https://cdn.payping.ir/statics/Payping-logo/Trust/blue.svg" height="128" width="128"></a></div>

## Contributing 🤝

Don't be shy and reach out to us if you want to contribute 😉

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## Issues

Each project may have many problems. Contributing to the better development of this project by reporting them. 👍
