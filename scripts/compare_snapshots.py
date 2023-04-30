import pandas as pd

#df1 is the snapshot analysis of delegators on another chain
df1 = pd.read_csv('results/rebusbalancesOnakash.csv', usecols=[1, 2], names=['balance', 'address'])
#df2 is the actual snapshot
df2 = pd.read_csv('snapshots/akash2023-04-29_19-01-03.csv')

# extract addresses from df1 into a set for faster membership testing
addresses = set(df1['address'])

# create a new dataframe with all of the addresses from df2 that are in df1
df3 = df2[df2['address'].isin(addresses)]

# print out the resulting dataframe
print(df3)

print(df3["value"].sum())
print(df2["value"].sum())