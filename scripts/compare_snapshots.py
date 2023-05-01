import pandas as pd

def compareaddresstoothersnapshot(addressestocheck: pd.DataFrame, snapshottocheck: pd.DataFrame ):
    #df1 is the snapshot analysis of delegators on another chain
    df1 = addressestocheck
    #df2 is the actual snapshot
    df2 = snapshottocheck

    # extract addresses from df1 into a set for faster membership testing
    addresses = set(df1['address'])

    # create a new dataframe with all of the addresses from df2 that are in df1
    df3 = df2[df2['address'].isin(addresses)]

    # print out the resulting dataframe
    print(df3)

    print(df3["value"].sum())
    print(df2["value"].sum())
    print(len(df3))
    print(len(df1))


if __name__ == "__main__":
    addressestocheck=pd.read_csv('results/junobalancesOnakash.csv', usecols=[1, 2], names=['balance', 'address'])
    snapshottocheck = pd.read_csv('snapshots/akash2023-05-01_17-38-01.csv')
    compareaddresstoothersnapshot(addressestocheck,snapshottocheck)