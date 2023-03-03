"""This is a simple script to get all ASN's of a given country
"""

import argparse
import warnings
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from rich.console import Console
from rich.progress import track

warnings.simplefilter(action='ignore', category=FutureWarning)

console = Console()

parser = argparse.ArgumentParser(description="Get ASN's of a given country")
parser.add_argument("country", help="Country code")
args = parser.parse_args()

country = args.country.upper()

# Create object page - pylint: disable=line-too-long
url = f"https://www-public.imtbs-tsp.eu/~maigron/RIR_Stats/RIR_Delegations/Delegations/ASN/{country}.html"
response = requests.get(url)
response.raise_for_status()

# Obtain page's information
soup = BeautifulSoup(response.text, 'lxml')

# Obtain information from tag <table>
table = soup.find('table', attrs={'class': 'delegs ripencc'})

# Obtain headers
headers = [header.text for header in table.find_all('th')]

# Create a data frame
data = pd.DataFrame(columns=headers[1:])
with open(file='ranges.txt', mode='w', encoding='UTF-8') as ranges_file:
    rows = table.find_all('tr')[2:]
    for row_index, row in enumerate(track(rows, description="Reading ...")):
        row_data = row.find_all('td')
        row = [i.text for i in row_data]
        if row[6] == 'Allocated':
            SEP = ',' if row_index != len(rows) - 1 else ''
            ranges_file.write(row[3] + SEP)
        data = data.append(dict(zip(headers[1:], row)), ignore_index=True)
        time.sleep(0.002)
    console.log(f"Found\t[green]{len(data)}[/green] ASN's")


# Export to csv
data.to_csv('asn_list.csv', index=False)
