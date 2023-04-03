# KleoDelegationAnalysis
Kleo Delegator Analysis

Finished: 

delegationsOnOtherChains.py - checks delegators on sourcechain and queries total balance on "chain to analyse"


to do towards AKASH/INJ Push: 
- Percentage conversion of existing Kleo Delegators into delegators on the new chain (comparison script to be written)
- Affect on existing chain delegations from the airdrop campaign (do we get more delegators on our other validators from the exposure) (snapshot script for chains)
- Number of new-to-Kleo delegators to the new chain vs existing delegators
- Percentage of retained delegators after 6 months the validate payback assumptions
- Percentage of airdrop claimed vs clawed back


Work In Progress: 
compareCurrentandPastSnapshot.py - analysis based on current (api read) and past snapshots (saved json file)
delegatorSnapshotProcessing.py - helper file with functions for processing 
utils - helper file 
publicKeyUtils.py - for INJ address derivation


