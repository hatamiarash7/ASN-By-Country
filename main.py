"""This is a simple script to get all ASN's of a given country
"""

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from rich.console import Console

console = Console(log_path=False)

if len(sys.argv) != 2:
    console.log("Usage: python main.py <country code>")
    sys.exit(1)

country = sys.argv[1]

# Create object page
url = 'https://www-public.imtbs-tsp.eu/~maigron/RIR_Stats/RIR_Delegations/Delegations/ASN/'\
    + country + '.html'
page = requests.get(url)

if page.status_code != 200:
    console.log(
        f'Error - {page.status_code} : Did you enter the correct country?')
    sys.exit(1)

# Obtain page's information
soup = BeautifulSoup(page.text, 'lxml')

# Obtain information from tag <table>
table = soup.find('table', attrs={'class': 'delegs ripencc'})

# Obtain headers
headers = []
for header in table.find_all('th'):
    title = header.text
    headers.append(title)


# Create a data frame
data = pd.DataFrame(columns=headers[1:])
with open(file='ranges.txt', mode='w', encoding='UTF-8') as ranges:
    rows = table.find_all('tr')[2:]
    for j in rows:
        with console.status("[bold green]Reading ...", spinner='aesthetic') as status:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
            console.log(f"[red]Find[/red] \t [blue]{row[3]}[/blue]")
            if row[6] == 'Allocated':
                ranges.write(row[3] + (',' if j != rows[-1] else ''))
            length = len(data)
            data.loc[length] = row

# Export to csv
data.to_csv('asn_list.csv', index=False)
