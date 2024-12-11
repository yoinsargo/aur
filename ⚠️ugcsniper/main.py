# I've last used this back in January 2024, and im not sure if it still works or not. I'd test on an account with low robux, use at your own risk.




import discord
import requests
import re
import time
import json
import asyncio
import uuid

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True

bot = discord.Client(intents=intents)

previous_items = set()

def get_xcsrf():
    cookies = {
        '.ROBLOSECURITY': "" # You need a your roblosecurity for this
    }

    r = requests.post("https://auth.roblox.com/v1/logout", cookies=cookies)

    if r.status_code == 200 or r.status_code == 403:
        xcsrf_token = r.headers.get("x-csrf-token")
        return xcsrf_token, cookies
    else:
        print('Cannot grab token. Invalid cookie.')
        return None

cookies = {
        '.ROBLOSECURITY': "" # here too
    }

r = requests.post("https://auth.roblox.com/v1/logout", cookies=cookies)
if r.status_code == 200 or r.status_code == 403:
    xcsrf_token = r.headers.get("x-csrf-token")
    print(xcsrf_token)
else:
    print('Cannot grab token. Invalid cookie.')

async def check_deals():
    time.sleep(5)
    try:
        session = requests.Session()
        cookies = {
            'marketplace_new_sort_type': 'deal_percent_high_to_low'
        }
        session.cookies.update(cookies)
        response = session.get('https://www.rolimons.com/marketplace/new')

        if response.status_code == 200:
            response_text = response.text
            match = re.search(r'var item_details = (\{.*?\});', response_text)
            if match:
                item_details_json = match.group(1)
                item_details = json.loads(item_details_json)

                for item_id, item_info in item_details.items():
                    price = item_info[5]
                    itemname = item_info[0]
                    rap = item_info[6]
                    stock = item_info[3]
                    thumbnail = item_info[4]
                    if rap is not None and price is not None and rap > 1 and price > 0 and int(item_id) != 14354427873:
                        deal = round((((price-rap)/rap)*100)*-1)
                        if price in [1, 2, 3, 4] or deal >= 95 and stock <= 200:
                            print(itemname)

                            datas = requests.get(f"https://economy.roblox.com/v2/assets/{item_id}/details")
                            datas = datas.json()

                            collectibleid = datas["CollectibleItemId"]
                            collectibleproductid = datas["CollectiblesItemDetails"]["CollectibleLowestAvailableResaleProductId"]
                            collectibleinstanceid = datas["CollectiblesItemDetails"]["CollectibleLowestAvailableResaleItemInstanceId"]

                            datas2 = requests.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleid}/resellers?cursor=&limit=100")
                            datas2 = datas2.json()

                            sellid = datas2["data"][0]["seller"]["sellerId"]
                            sellusername = datas2["data"][0]["seller"]["name"]
                            serial = datas2["data"][0]["serialNumber"]

                            xcsrf_token, cookies = get_xcsrf()

                            headers = {"x-csrf-token": xcsrf_token}

                            idemuuid = str(uuid.uuid4())

                            payload = {"collectibleItemId": collectibleid,
                                       "expectedCurrency":1,
                                       "expectedPrice": price,
                                       "expectedPurchaserId":"", # put your roblox id here
                                       "expectedPurchaserType":"User",
                                       "expectedSellerId":sellid,
                                       "expectedSellerType":"User",
                                       "idempotencyKey": idemuuid,
                                       "collectibleItemInstanceId": collectibleinstanceid,
                                       "collectibleProductId": collectibleproductid
                                       }

                            r = requests.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleid}/purchase-resale", headers=headers,json=payload,cookies=cookies)
                            r = r.json()
                            print(r)

                            if r["purchaseResult"] == "Purchase transaction success.":
                                embed = discord.Embed(
                                    title=f"Sniped UGC item for {deal}% deal!",
                                    description=f"{itemname} \n https://www.rolimons.com/item/{item_id}",
                                    color=0xeb3434
                                    )
                                embed.set_author(
                                    name="AUR.",
                                    icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png"
                                    )

                                embed.add_field(name="Price", value=f"{price}", inline=True)
                                embed.add_field(name="Serial", value=f"{serial}", inline=True)
                                embed.add_field(name="Sniped on", value= "Synraider", inline=True)
                                embed.add_field(name="Bought From", value=f"{sellusername}", inline=True)
                                embed.set_thumbnail(url=thumbnail)
                                embed.set_footer(text="AUR Sniper - AUR.")

                                channel_id = 1188545677924503632
                                channel = bot.get_channel(channel_id)
                                message = await channel.send("<@732901432122146908>", embed=embed)

                        elif deal >= 84:
                            
                            if (itemname, price) in previous_items:
                                continue
                            embed = discord.Embed(
                                title=f"Found item for {deal}% deal!",
                                description=f"{itemname} \n https://www.rolimons.com/item/{item_id}",
                                color=0xFF00E7
                            )
                            embed.set_author(
                                name="AUR.",
                                icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png"
                            )
                            embed.add_field(name="Price", value=f"{price}", inline=True)
                            embed.add_field(name="RAP", value=f"{rap}", inline=True)
                            embed.add_field(name="Stock", value=f"{stock}", inline=True)
                            embed.set_thumbnail(url=thumbnail)
                            embed.set_footer(text="AUR Deals - AUR.")

                            button = discord.ui.Button(style=discord.ButtonStyle.link, label="Item Link", url=f"https://www.roblox.com/catalog/{item_id}")
                            view = discord.ui.View()
                            view.add_item(button)
                            
                            channel_id = 1139150536101335171
                            channel = bot.get_channel(channel_id)
                            message = await channel.send("<@&1143172110722793522>", embed=embed, view=view)
                            await message.publish()

                            price = int(price)
                            previous_items.add((itemname, price))

            else:
                print("item_details variable not found in the response.")

        else:
            print(f"Failed to fetch the webpage. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e} ")


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="AUR Sniper"
        )
    )
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    while True:
        await check_deals()
        

bot.run('')
