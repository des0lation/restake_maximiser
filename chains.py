# Run this and then click the wand button to get a list of all chains this can be run for
import requests,json,pandas as pd
from datetime import datetime, timedelta
chains = requests.get('https://chains.cosmos.directory/').json()['chains']
chains_list = []
for chain in chains:
  chains_list.append(chain['bech32_prefix'])

pd.DataFrame(chains_list)