import pandas as pd
import numpy as np

# read csv
df = pd.read_csv('train.csv')

# number of players
num_players = df.playerId.nunique()

# player with most goal
condition = (df.outcome == 'گُل') | (df.outcome == 'گُل به خودی')

goal_values = df[condition]['playerId'].value_counts().keys().tolist()
goal_counts = df[condition]['playerId'].value_counts().tolist()

player_most_goal = goal_values[0]

# players with most and least goal per shoot
d = {}
players = df.playerId.unique()
for player in players:
  goals  = (df[condition]['playerId'].values == player).sum()
  shoots = (df['playerId'].values == player).sum()
  d[player] = round(goals/shoots,2)

player_most_perc = max(d, key=d.get)
player_least_perc = min(d, key=d.get)

# far most distance
dists = []
for i in range(len(df)):
  a = np.array((df['x'][i], df['y'][i]))
  b = np.array((0,0))
  dists.append(np.linalg.norm(a-b))
dists.sort(reverse=True)
far_dist = dists[0]

# write to file
with open('output.txt', 'w') as f:
  f.write('%d' % num_players)
  f.write('\n')
  f.write(player_most_goal)
  f.write('\n')
  f.write('%s' %player_most_perc)
  f.write(',')
  f.write('%s' %player_least_perc)
  f.write('\n')
  f.write('%d' % far_dist)