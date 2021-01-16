import asyncio
from asyncio import base_events
import aiohttp
import json 
import aiofiles
import aiocsv

session = ""
storedIds = []
startUrl = "https://api.battlemetrics.com/servers?fields[server]=portQuery,name,ip,port&filter[game]=ark&filter[features][2e079b9a-d6f7-11e7-8461-83e84cedb373]=true"
fl = open('token.txt')
token = fl.read()
fl.close()
storage = ""
async def store(data):
    data = json.loads(data)
    storageBlobs = []
    for server in data['data']:
        storageBlob = []
        storageBlob.append(server['attributes']['name'])
        storageBlob.append(server['attributes']['ip'])
        storageBlob.append(server['attributes']['portQuery'])
        storageBlob.append(server['attributes']['port'])
        storedIds.append(int(server['id']))
        storageBlobs.append(storageBlob)
    await storage.writerows(storageBlobs)
    return data['links']['next']
    

async def requestInfo(url):
    headers = {'Authorization': f'Bearer {token}'}
    resp = await session.get(url,headers=headers)
    remaining = resp.headers['X-Rate-Limit-Remaining'] 
    return [await resp.text(),remaining]

async def requestLoop():
    run = True
    requestsLeft = 300
    nextUrl = startUrl
    i = 1
    while run:
        print(i)
        if requestsLeft <= 1:
            await asyncio.sleep(60)
        data = await requestInfo(nextUrl)
        nextUrl = await store(data[0])
        requestsLeft = int(data[1])
        i += 1

async def main():
    global session,storage,storedIds
    session = aiohttp.ClientSession()
    file = await aiofiles.open('output.csv','a',encoding="utf-8", newline="")
    storage = aiocsv.AsyncWriter(file,dialect="unix")
    await requestLoop()
    await session.close()

#print(json.loads(await requestInfo(startUrl)[0]))
loop = asyncio.new_event_loop()
info = loop.run_until_complete(main())