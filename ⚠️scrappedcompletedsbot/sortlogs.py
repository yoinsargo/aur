import json
from collections import defaultdict
import requests
import time
import discord
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True

bot = discord.Client(intents=intents)

async def main():
    r = requests.get("https://api.rolimons.com/items/v1/itemdetails").json()
    items = r["items"]

    with open("logs.json", 'r') as file:
        logs = json.load(file)

    with open("emoji.json", 'r') as file:
        emojis = json.load(file)
    trades = defaultdict(lambda: defaultdict(list))

    for itemid, item_logs in logs.items():
        for item_id, details in item_logs.items():
            timestamp = details["updated"]
            owner = details["owner"]

            # Group by timestamp and owner
            trades[timestamp][owner].append(itemid)

    trade_results = []

    for timestamp, owners in trades.items():
        if len(owners) == 2:  # We only care about trades between two owners
            owners_list = list(owners.items())  # Convert the dictionary into a list of (owner, items)

            owner1, owner1_items = owners_list[0]  # First owner and their items
            owner2, owner2_items = owners_list[1]  # Second owner and their items

            try:
                owner1name = requests.post("https://apis.roblox.com/user-profile-api/v1/user/profiles/get-profiles",
                                       json = {"userIds":[int(owner1)],"fields":["names.combinedName","names.username","names.displayName","names.alias"]}).json()
                owner1name = owner1name["profileDetails"][0]["names"]["username"]
                
            except:
                owner1name = "Unknown"

            try:
                owner2name = requests.post("https://apis.roblox.com/user-profile-api/v1/user/profiles/get-profiles",
                                       json = {"userIds":[int(owner2)],"fields":["names.combinedName","names.username","names.displayName","names.alias"]}).json()

                owner2name = owner2name["profileDetails"][0]["names"]["username"]

            except:
                owner2name = "Unknown"

            side1 = []
            side2 = []

            side1total = 0
            side2total = 0

            for item in owner1_items:
                name = str(item)  # Default name is the item ID in case no match is found
                value = "Unknown"
                emoji = ""
                emojiname = ""

                # Loop through items to find the name and value
                for dataitem, dataitemdata in items.items():
                    if int(dataitem) == int(item):
                        name = dataitemdata[0]
                        value = dataitemdata[4]

                        side1total += value
                        break  # Exit loop once match is found

                # Loop through emojis to find the emoji and emojiname
                for emojiitem, emojiid in emojis.items():
                    if int(emojiitem) == int(item):
                        emoji = int(emojiid)
                        emojiname = int(emojiitem)
                        break  # Exit loop once match is found
                side2.append(f"<:{emojiname}:{emoji}> **{name} ({value:,})**")

            for item in owner2_items:
                name = str(item)  # Default name is the item ID in case no match is found
                value = "Unknown"
                emoji = ""
                emojiname = ""

                # Loop through items to find the name and value
                for dataitem, dataitemdata in items.items():
                    if int(dataitem) == int(item):
                        name = dataitemdata[0]
                        value = dataitemdata[4]
                        break  # Exit loop once match is found

                # Loop through emojis to find the emoji and emojiname
                for emojiitem, emojiid in emojis.items():
                    if int(emojiitem) == int(item):
                        emoji = emojiid
                        emojiname = emojiitem

                        side2total += value
                        break  # Exit loop once match is found

                side1.append(f"<:{emojiname}:{emoji}> **{name} ({value:,})**")

            side1 = '\n'.join(side1)
            side2 = '\n'.join(side2)


            embed = discord.Embed(
                title=f"New Completed Trade",
                description=f"**{owner1name} and {owner2name} have traded!**",
                color=0x7d12fe
                )

            embed.set_author(
                name="AUR.",
                icon_url="https://media.discordapp.net/attachments/732902053290049538/1156618655388422184/AURt.png?ex=6515a090&is=65144f10&hm=c07a87a2fc89f9ddb06ccef22a43a69de87327f055c93dbc2c711f830ba58792&=&width=896&height=369"
                )

            embed.add_field(name=f"{owner1name}'s side ({side2total:,})", value=f"{side1}", inline=False)
            embed.add_field(name=f"{owner2name}'s side ({side1total:,})", value=f"{side2}", inline=False)
            embed.add_field(name="Completed", value=f"<t:{timestamp}:R>", inline=False)
            embed.set_footer(text="AUR COMPLETEDS - AUR.")

            if side1total <= 100000 or side2total <= 100000:
                channel_id = 1293990460242530396
            elif side1total <= 500000 or side2total <= 500000:
                channel_id = 1293990508468768902
            elif side1total <= 1000000 or side2total <= 1000000:
                channel_id = 1293990542606340107

            channel = bot.get_channel(channel_id)

            message = await channel.send(embed=embed)

            time.sleep(5)

    return trade_results

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="COMPLETED TRADES"
        )
    )
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    await main()

bot.run('')
