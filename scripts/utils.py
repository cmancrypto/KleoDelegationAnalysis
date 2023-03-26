from bip_utils import Bech32Decoder, Bech32Encoder
from cosmpy.aerial.client import LedgerClient, NetworkConfig


def convert_to_juno_address(chain: str, address: str) -> str:
    decoded_juno = Bech32Decoder.Decode(chain, address)
    return Bech32Encoder.Encode("juno", decoded_juno)

def convert_address_to_address(fromchain: str, address: str, tochain:str) -> str: 
    decoded_address=Bech32Decoder.Decode(fromchain, address)
    return Bech32Encoder.Encode(tochain, decoded_address)

def getCosmpyClient(cfg):
    ledger_client=LedgerClient(cfg)
    return ledger_client

def getAkashCFG():
    cfg= NetworkConfig(
    chain_id="akashnet-2",
    url="grpc+https://grpc-akash-ia.cosmosia.notional.ventures:443",
    fee_minimum_gas_price=0,
    fee_denomination="uakt",
    staking_denomination="uakt",
    )

    return cfg
