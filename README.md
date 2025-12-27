# ASN By Country

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![GitHub release](https://img.shields.io/github/release/hatamiarash7/ASN-By-Country.svg)](https://GitHub.com/hatamiarash7/ASN-By-Country/releases/) [![CodeQL](https://github.com/hatamiarash7/ASN-By-Country/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/hatamiarash7/ASN-By-Country/actions/workflows/codeql-analysis.yml) [![GitGuardian](https://github.com/hatamiarash7/ASN-By-Country/actions/workflows/gitguardian.yml/badge.svg?branch=main)](https://github.com/hatamiarash7/ASN-By-Country/actions/workflows/gitguardian.yml) [![Release](https://github.com/hatamiarash7/ASN-By-Country/actions/workflows/release.yml/badge.svg)](https://github.com/hatamiarash7/ASN-By-Country/actions/workflows/release.yml)

It's a simple script to get ASN delegations list of specific country. I'm using **RIR Delegations & RIPE NCC Allocations** from [here](https://www-public.imtbs-tsp.eu/~maigron/RIR_Stats/index.html).

## Usage

```bash
python main.py <country_code_1> <country_code_2> ... [options]
```

### Optional Arguments

- `--data-type <type>`:
  Specify which type of data to fetch. The options are:

  - `asn`: Retrieve only AS numbers (default).
  - `ipv4`: Retrieve only IPv4 addresses.
  - `ipv6`: Retrieve only IPv6 addresses.
  - `all`: Retrieve AS numbers, IPv4 addresses, and IPv6 addresses.

  **Default**: `asn`

## Examples

```bash
python main.py IR US FR

python main.py IR --data-type asn

python main.py IR US --data-type all
```

## use makefile

create virtual environment and install dependency

```bash
make env
make deps
```

Run the program

```bash
make run ARGS="US"
```

Clean outputs

```bash
make clean
```

### Run with Docker

```bash
docker run --rm  -v /results:/app/output_data hatamiarash7/asn-by-country:latest <country_code_1> <country_code_2> ... [options]
```

use makefile

```bash
make docker-run ARGS="IR"
make docker-run ARGS="US DE"
```

build docker image only

```bash
make docker-build
```

## Result

The output of the ASN By Country script will be generated in the `output_data` directory. The following files will be created based on the specified country codes, and they will contain ASN delegation information for both IPv4 and IPv6 addresses.

### File List and Descriptions

| File Name                 | Description                                                   |
| ------------------------- | ------------------------------------------------------------- |
| `{Country}_asn_list.csv`  | Contains a list of ASN delegations for specified country.     |
| `{Country}_ipv4_list.csv` | Contains IPv4-specific ASN delegations for specified country. |
| `{Country}_ipv6_list.csv` | Contains IPv6-specific ASN delegations for specified country. |
| `asn_ranges.txt`          | Contains a list of all ASN ranges across countries.           |
| `ipv4_ranges.txt`         | Contains a list of all IPv4 ranges.                           |
| `ipv6_ranges.txt`         | Contains a list of all IPv6 ranges.                           |

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
