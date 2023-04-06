from bip_utils import Bech32Decoder, Bech32Encoder
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from typing import List, Dict
import requests
import time
from bip_utils import Bech32Decoder, Bech32Encoder
from constants import COSMOS_DIR_API, COSMOS_DIR_REST_PROXY

def convert_to_juno_address(chain: str, address: str) -> str:
    decoded_juno = Bech32Decoder.Decode(chain, address)
    return Bech32Encoder.Encode("juno", decoded_juno)

def convert_address_to_address(fromchain: str, address: str, tochain:str) -> str: 
    decoded_address=Bech32Decoder.Decode(fromchain, address)
    return Bech32Encoder.Encode(tochain, decoded_address)

def getCosmpyClient(cfg):
    ledger_client=LedgerClient(cfg)
    return ledger_client

def get_chain_info(chain):
    url = f"{COSMOS_DIR_API}/{chain}"
    resp = get_API_data_with_retry(url)
    return resp.json()

def get_network_config_args(chain_info):
    chain = chain_info["chain"]
    chain_name = chain["chain_name"]
    try:
        fee_token = chain["fees"]["fee_tokens"][0]
        fee_denom = fee_token["denom"]
        min_gas_price = fee_token["fixed_min_gas_price"]
    except KeyError as ex:
        fee_denom = chain["denom"]
        min_gas_price = 0

    return {
        "chain_id": chain["chain_id"],
        "url": f"rest+{COSMOS_DIR_REST_PROXY}/{chain_name}",
        "fee_minimum_gas_price": min_gas_price,
        "fee_denomination": fee_denom,
        "staking_denomination": "",
    }

def getAPIURl(chain_name):
    return f"{COSMOS_DIR_REST_PROXY}/{chain_name}"


def get_network_config(chain):
        info=get_chain_info(chain)
        cfg_args=get_network_config_args(info)
        return cfg_args


def get_network_bech32_prefix(chain):
    chain_results=get_chain_info(chain)
    bech32_prefix=chain_results["chain"]["bech32_prefix"]
    return bech32_prefix


def convert_assets_data(assets: List[Dict]) -> Dict:
    res_dict = {
        "native": 0,
        "cw20": 0,
    }
    for asset in assets:
        info = asset["info"]
        amount = asset["amount"]
        token_type = list(info.keys())[0]
        if token_type == "native":
            res_dict["native"] = int(amount)
        else:
            res_dict["cw20"] = int(amount)

    return res_dict

def get_API_data_with_retry(url, retries=10, delay=5):
    for i in range(retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
            time.sleep(delay)
    print("Request failed after multiple attempts")
    return None
