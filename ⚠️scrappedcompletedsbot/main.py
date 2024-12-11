# scrapped this a while ago, there might be many bugs and this requires proxies. its very unfinished and 50% of the function is not automated, thats why it requires so many running instances to work. I wouldn't recommend using it.



import aiohttp, json, asyncio, requests, threading, random, tasksio, ctypes, time, traceback
from aiohttp_socks import ProxyConnector
from httpstuff import ProxyPool
from discord_webhook import DiscordWebhook, DiscordEmbed
import traceback
from datetime import datetime, timezone, timedelta
import os

proxies = open('proxies.txt').read().splitlines()[0:50]

class Bot:
    def __init__(self):
        self.ProxyPool = ProxyPool(proxies.copy())
        self.checkedItems = 0
        self.items = json.load(open('items.json'))
        asyncio.run(self.threads())

    async def threads(self):
        await self.sessions()
        self.checkedItems = 0
        async with tasksio.TaskPool(100) as pool:
            for itemid in self.items:
                await pool.put(self.checkowners(itemid))

    async def checkowners(self, itemid):
        print("Doing:"+ itemid)
        logs = {}
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        
        async with aiohttp.ClientSession() as session:
            cursor = ''
            max_retries = 10000000
            retry_count = 0

            while cursor is not None:
                proxy = self.ProxyPool.get()
                self.ProxyPool.put(proxy)


                try:
                    cookies = {
                        ".ROBLOSECURITY":""
                        }
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0"
                        }
                    
                    
                    response = await self.sessionStorage[proxy].get(
                        f'https://inventory.roblox.com/v2/assets/{itemid}/owners?limit=100&cursor={cursor}', 
                        timeout=30,
                        cookies=cookies,
                        headers=headers
                    )
                    print("Request completed.")

                    if response.status == 200:
                        data = await response.json()

                        for item in data['data']:

                            if item["owner"] is None:
                                owner = -1
                            else:
                                owner = item["owner"]["id"]
                            try:
                                timestamp = datetime.strptime(item["updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
                            except ValueError:
                                timestamp = datetime.strptime(item["updated"], "%Y-%m-%dT%H:%M:%SZ")
                            timestamp2 = timestamp.replace(tzinfo=timezone.utc)
                            timestamp3 = int(timestamp2.timestamp())

                            timenow = datetime.now(timezone.utc)
                            timenow_unix = int(timenow.timestamp())


                            if timenow_unix - timestamp3 <= 7200:

                                print(f"Found item {item['id']}")

                                if int(itemid) not in logs:
                                    logs[int(itemid)] = {}

                                logs[int(itemid)][item["id"]] = {
                                    "updated": timestamp3,
                                    "owner": owner,
                                }
                            

                        cursor = data.get('nextPageCursor') 
                        retry_count = 0
                    else:
                        data = await response.json()
                        if data['errors'][0]['code'] in [1, 11]:
                            break
                except Exception as e:
                    retry_count += 1
                    
                    if retry_count >= max_retries:
                        break

        
        if logs:
            print(logs)

            if os.path.exists('logs.json'):
                with open('logs.json', 'r') as file:
                    try:
                        existing_logs = json.load(file)
                    except json.JSONDecodeError:
                        existing_logs = {}
            else:
                existing_logs = {}

            for itemid, item_logs in logs.items():
                if itemid not in existing_logs:
                    existing_logs[itemid] = {}
                existing_logs[itemid].update(item_logs)

            with open('logs.json', 'w') as file:
                json.dump(existing_logs, file, indent=4)
                

        self.checkedItems += 1
        print(f"Checked {itemid} {self.checkedItems}")

    async def sessions(self):
        self.sessionStorage = {}
        for proxy in self.ProxyPool.raw_proxies:
            self.sessionStorage[proxy] = aiohttp.ClientSession(
                connector = ProxyConnector.from_url(f"http://{proxy}")
            )
    def parse_timestamp(timestamp_str):
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")

Bot()
