import requests
import json
import csv
import pandas as pd
import datetime


inputWallet = input("Please enter your wallet address: ")

#read Wallets
with open("wallets.txt", "r") as file:
    walletsArray = [line.strip() for line in file.readlines()]

def getexchangedata(wallet, offset, limit): 
    url = f"https://api-mainnet.magiceden.dev/v2/wallets/{wallet}/activities?offset={offset}&limit={limit}"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    response_json = response.json()
    return(response_json)



offset = 0 
limit = 500
allTransactions = getexchangedata(inputWallet, offset, limit)
currentPage = []

# Paginate. Break once the length of the current page is >= the limit, meaning it had less than enough to fill a page.
while True:
    offset += limit
    newPage = getexchangedata(inputWallet, offset, limit)

    for i in newPage:
        allTransactions.append(i)
        #Creating a "Current page" array just to check the length for the limit below
        currentPage.append(i)

    if len(currentPage) < limit:
        break
    currentPage = []
print(len(allTransactions))


#build json to convert to csv
txJson = []
for i in allTransactions:
    dt = datetime.datetime.fromtimestamp(i['blockTime'])
# Format the datetime object as a string in the desired format
    date_string = dt.strftime("%m-%d-%y %H:%M")
    
    try:
        buyer=i['buyer']
    except KeyError:
        buyer='n/a'

    try: 
        seller=i['seller']
    except KeyError:
        seller='n/a'
    
    if buyer != inputWallet:
        purchaseType = 'Seller'
    else:
        purchaseType = 'Buyer'

    txJson.append({
        'signature':i['signature'],
        'type': i['type'],
        'tokenAddress': i['tokenMint'],
        'collection': i['collection'],
        'collectionSymbol': i['collectionSymbol'],
        'blockTime': date_string,
        'price': i['price'],
        'purchaseType': purchaseType,
        'buyer': buyer,
        'seller': seller
    })


txJson2 = json.dumps(txJson)
# print(txJson)

df = pd.read_json(txJson2)

print(df)

df.to_csv("data.csv", index=False)
