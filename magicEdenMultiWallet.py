import requests
import json
import csv
import pandas as pd
import datetime

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

#I use current transactions here so that in the loop below, first page will always be the "current page". 
#I append that first page to the "All transactions", and every subsequent page gets appended as 
#"Newpage" in the third loop
currentTransactions = []
allTransactions = []

#Loop 1: Looping through wallet list
for wallet in walletsArray:
    offset = 0 
    limit = 500
    currentTransactions = getexchangedata(wallet, offset, limit)
    for i in currentTransactions:
        i['wallet'] = wallet


    allTransactions.append(currentTransactions)
    currentPage = []

    #Loop 2: Pagination
    while True:
        offset += limit
        newPage = getexchangedata(wallet, offset, limit)
        for i in newPage:
            i['wallet'] = wallet
        print(wallet)

        #Loop 3: Appending subsequent pages, and break once it hits the end (current page < limit)
        for i in newPage:
            allTransactions.append(i)
            
            
            currentPage.append(i)
        if len(currentPage) < limit:
            break
        currentPage = []

print(allTransactions)
#build json to convert to csv
txJson = []

#loop 4: Looping through each wallet transactions, with I being an array of each wallet's tx
for i in allTransactions:
    if len(i) > 0:
        for j in i:
            dt = datetime.datetime.fromtimestamp(j['blockTime'])
        # Format the datetime object as a string in the desired format
            date_string = dt.strftime("%m-%d-%y %H:%M")
            try:
                buyer=j['buyer']
            except KeyError:
                buyer='n/a'

            try: 
                seller=j['seller']
            except KeyError:
                seller='n/a'
            
            if buyer != j['wallet']:
                purchaseType = 'Seller'
            else:
                purchaseType = 'Buyer'

            txJson.append({
                'wallet': j['wallet'],
                'signature':j['signature'],
                'type': j['type'],
                'tokenAddress': j['tokenMint'],
                'collection': j['collection'],
                'collectionSymbol': j['collectionSymbol'],
                'blockTime': date_string,
                'price': j['price'],
                'purchaseType': purchaseType,
                'buyer': buyer,
                'seller': seller
            })

txJson2 = json.dumps(txJson)
        # print(txJson)

df = pd.read_json(txJson2)

print(df)

df.to_csv("data.csv", index=False)