import requests
import time
import discord
import asyncio
import json

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True

bot = discord.Client(intents=intents)

role_mention = "<@&1157241573537497149>"

previousmsg = set()

async def main():
    try:
        s = requests.session()
        s.headers = {
            "authorization": "", # you need a token of a discord account which is in rolimons for this to work
            }
        r = s.get("https://discord.com/api/v9/channels/535250426061258753/messages?limit=1")
        r = r.json()
        for message in r:
            if message['attachments']:
                msgid = message["id"]
                if (msgid) in previousmsg:
                    continue
                content = message["content"]
                author = message['author']
                authorid = author["id"]
                authorusername = author["username"]
                for attachment in message["attachments"]:
                    imgurl = attachment["url"]

                embed = discord.Embed(
                        color = 0xed1c24
                    )
                embed.add_field(name="Posted By", value=f"{authorusername}", inline=True)
                embed.add_field(name="Poster User ID", value=f"{authorid}", inline=True)  # Removed extra parenthesis  
                
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/732902053290049538/1156618655388422184/AURt.png?ex=65179ad0&is=65164950&hm=ba705b27388f33fddee7f6390ed5b351c159ebc0cbe7e04b0b3cf1b5363f1a80&")
                embed.set_footer(text="AUR PROOFS - AUR.")
                    
                channel_id = 1295098727543078964
                channel = bot.get_channel(channel_id)
                await channel.send(f"{content}")
                await channel.send(imgurl)
                await channel.send(embed=embed)
                    

                previousmsg.add((msgid))
        
    except Exception as e:
        print(f"an error occured: {e}")


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="AUR Trading"
        )
    )
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    while True:
        await main()
        await asyncio.sleep(10)

bot.run('')
