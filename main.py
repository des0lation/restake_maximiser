#Define Balance and Chain
balance = 1000
chain = 'cosmoshub'

#Getting Chain Data
url = f'https://chains.cosmos.directory/{chain}'
data = requests.get(url).json()['chain']
decimals = data['decimals']
params = data['params']
block_time = params['actual_block_time']
total_bonded = int(params['bonded_tokens'])
block_reward = float(params['annual_provision'])/float(params['blocks_per_year'])
community_tax = params['community_tax']
apr = (1-community_tax)*block_reward * (365*86400/block_time)/total_bonded
token = data['fees']['fee_tokens'][0]['denom'].replace("u",'')



#Running calculate_effective on every validator
def get_max(balance):
    aprs = []
    for i in range(0,len(names)):
      aprs.append(calculate_effective(balance,df.iloc[i][3],df.iloc[i][1],df.iloc[i][2],block_time,apr))
    x = aprs.index(max(aprs))
    return max(aprs),df.iloc[x][0],aprs

#Calculating the effective apy based on your balance
def calculate_effective(staked,minimum,commission,frequency,block_time,apr):
  own_block_reward =staked * apr/(365*86400/block_time)
  time_till_compound = block_time*minimum/block_reward
  seconds_year = 365 * 86400
  periods = min(seconds_year/frequency,seconds_year/time_till_compound)
  effective_apy = (1-commission) * (1+apr/(periods))**(periods) - 1
  return effective_apy

# Define a function to convert the time strings into seconds
def to_seconds(time_string):
    if type(time_string) is list:
      return 86400/len(time_string)
    elif 'every' in time_string:
      time_string = time_string.replace('every ','')
      if 'hour' in time_string:
        unit = 3600
        time_string = time_string.replace('hour','').replace('s','').replace(' ','')
      elif 'minute' in time_string:
        unit = 60
        time_string = time_string.replace('minutes','')
      return unit*int(time_string)
    else:
        return 86400
times = []
names = []
minimums = []
commissions = []
vals =   requests.get("https://validators.cosmos.directory/chains/cosmoshub").json()['validators']
for val in vals:
  try:
    if val['active']  == True and val['commission']['rate'] > 0:
      times.append(to_seconds(val['restake']['run_time']))
      names.append(val['moniker'])
      minimums.append(int(val['restake']['minimum_reward'])/10**6)
      commissions.append(val['commission']['rate'])
  except:
    continue
data = {"Name":names,"Commission":commissions,"Freq":times,"Minimum Reward":minimums}
df = pd.DataFrame(data)
results = get_max(balance)
aprs = results[-1]
data = {"Name":names,"Commission":commissions,"Freq":times,"Minimum Reward":minimums,"APR":aprs}
df = pd.DataFrame(data)


print(str(100*results[0])+"% restaking with "+results[1].strip(),"is the max apr you will get on cosmos excluding 0% commission validators with a balance of",balance,token)
df