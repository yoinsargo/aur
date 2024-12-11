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
            "authorization": "", # like the proof bot you need a token of a discord account that is in rolimons
            }
        r = s.get("https://discord.com/api/v9/channels/442709710408515605/messages?limit=1")
        r = r.json()
        for message in r:
            msgid = message["id"]
            if (msgid) in previousmsg:
                continue
            content = message["content"]
            author = message['author']
            authorid = author["id"]
            authorusername = author["username"]
            avatar = author["avatar"]

            imgurl = None
            if message['attachments']:
                for attachment in message["attachments"]:
                    imgurl = attachment["url"]

            avatarurl = f"https://cdn.discordapp.com/avatars/{authorid}/{avatar}"

            embed = discord.Embed(
                title=f"{authorusername} has posted a new trade advertisement!",
                description=f"{content}",
                color = 0x4287f5
                )
            embed.add_field(name="Posted In", value=f"Rolimon's", inline=True)
            embed.add_field(name="Posted By", value=f"{authorusername}", inline=True)
            embed.add_field(name="Poster User ID", value=f"<@{authorid}>", inline=True) 
                
            embed.set_author(name=f"{authorusername} · <@{authorid}>", icon_url=avatarurl)
            if imgurl:
                embed.set_image(url=imgurl)
            embed.set_footer(text="AUR Trading - AUR.", icon_url="https://cdn.discordapp.com/attachments/732902053290049538/1156618655388422184/AURt.png?ex=65179ad0&is=65164950&hm=ba705b27388f33fddee7f6390ed5b351c159ebc0cbe7e04b0b3cf1b5363f1a80&")
                
            channel_id = 1198658999436972063
            channel = bot.get_channel(channel_id)
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
