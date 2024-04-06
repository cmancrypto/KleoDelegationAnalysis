import requests
import json

url="https://graphql.mainnet.stargaze-apis.com/graphql"

#queries stargaze API to get owner of a token, requires collection Addr and Token Id, returns owner address as a string
def query_stargaze_token_owner(collectionAddr : str,tokenId : str) -> str:
    query="""query Token($collectionAddr: String!, $tokenId: String!) {
      token(collectionAddr: $collectionAddr, tokenId: $tokenId) {
        id
        owner {
          address
        }
      }
    }"""
    variables={
    "collectionAddr" : collectionAddr,
        "tokenId": tokenId
    }
    headers={"content-type": "application/json; charset=utf-8"}
    data=json.dumps({"query": query,"variables":variables})
    response=requests.post(url=url,data=data,headers=headers,)
    response_json=response.json()
    owner=response_json["data"]["token"]["owner"]["address"]
    return owner



if __name__ == "__main__":
    query_stargaze_token_owner(collectionAddr = "stars166kqwcu8789xh7nk07fcrdzek54205u8gzas684lnas2kzalksqsg5xhqf", tokenId = str(910))