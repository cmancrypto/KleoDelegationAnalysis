import utils

cfg=utils.getAkashCFG()
client=utils.getCosmpyClient(cfg)

address="akash1xwseskrmnxrvesmad0xtyfvl3lx7xzkkx67x06"

s=client.query_staking_summary(address)
print(s.total_staked)
