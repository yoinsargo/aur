import requests
import re
import json
import time
import discord
import asyncio
from discord.ext import tasks

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True

bot = discord.Client(intents=intents)

previous_items = set()

@tasks.loop(seconds=3)
async def main():
    try:
        itemDetails = json.loads(
            re.findall('item_details = (.*?);', requests.get('https://www.rolimons.com/deals').text)[0]
        )   
        
        for item_id, item_info in itemDetails.items():

            if item_id:
                
                item_name = item_info[0]
                price = item_info[1]
                rap = item_info[2]
                value = item_info[6]
                img = item_info[9]
                condition_to_ignore = item_info[4] == 1
                
                if rap > 0 and price > 0:
                    deal = round((((price - value) / value) * -100), 2)
                    if deal >= -11 and not condition_to_ignore and item_info[8] is not None:
                        if (item_name, price) in previous_items:
                            continue
                        deal = round(deal)
                        deal = int(deal)


                        if deal == 0:
                          title = f"Found rare item selling for it's value!"
                        elif -11<deal<0:
                          deal = -1*deal
                          title = f"Found rare item selling for {deal}% above it's value!"
                        else:
                          title = f"Found rare item for {deal}% deal!"

                        embed = discord.Embed(
                            title= title,
                            description=f"{item_name} \n https://www.rolimons.com/item/{item_id} \n https://www.roblox.com/catalog/{item_id}",
                            color=0x76c9ff
                            )

                        embed.set_author(
                            name="AUR.",
                            icon_url="https://media.discordapp.net/attachments/732902053290049538/1156618655388422184/AURt.png?ex=6515a090&is=65144f10&hm=c07a87a2fc89f9ddb06ccef22a43a69de87327f055c93dbc2c711f830ba58792&=&width=896&height=369"
                            )

                        embed.add_field(name="Price", value=f"{price}", inline=True)
                        embed.add_field(name="RAP", value=f"{rap}", inline=True)
                        embed.add_field(name="Value", value=f"{value}", inline=True)
                        embed.set_thumbnail(url=img)
                        embed.set_footer(text="AUR Deals - AUR.")

                        button = discord.ui.Button(style=discord.ButtonStyle.link, label="Item Link", url=f"https://www.roblox.com/catalog/{item_id}")
                        view = discord.ui.View()
                        view.add_item(button)

                        channel_id = 1156584135566053466
                        channel = bot.get_channel(channel_id)

                        message = await channel.send(f"<@&1156582371517276210>",embed=embed, view=view)
                        await message.publish()
                        previous_items.add((item_name, price))

                    if deal >= 24 and not condition_to_ignore and value >= 5000 and item_info[5] is not None:
                        if (item_name, price) in previous_items:
                            continue
                        deal = round(deal)

                        embed = discord.Embed(
                            title=f"Found valued item for {deal}% deal!",
                            description=f"{item_name} \n https://www.rolimons.com/item/{item_id} \n https://www.roblox.com/catalog/{item_id}",
                            color=0x3696D8
                            )

                        embed.set_author(
                            name="AUR.",
                            icon_url="https://media.discordapp.net/attachments/732902053290049538/1156618655388422184/AURt.png?ex=6515a090&is=65144f10&hm=c07a87a2fc89f9ddb06ccef22a43a69de87327f055c93dbc2c711f830ba58792&=&width=896&height=369"
                            )

                        embed.add_field(name="Price", value=f"{price}", inline=True)
                        embed.add_field(name="RAP", value=f"{rap}", inline=True)
                        embed.add_field(name="Value", value=f"{value}", inline=True)
                        embed.set_thumbnail(url=img)
                        embed.set_footer(text="AUR Deals - AUR.")

                        button = discord.ui.Button(style=discord.ButtonStyle.link, label="Item Link", url=f"https://www.roblox.com/catalog/{item_id}")
                        view = discord.ui.View()
                        view.add_item(button)

                        channel_id = 1156259187970560092
                        channel = bot.get_channel(channel_id)

                        message = await channel.send(f"{role_mention}",embed=embed, view=view)
                        await message.publish()
                        previous_items.add((item_name, price))

                    if deal >= 12 and value >= 150000 and not condition_to_ignore:
                        if (item_name, price) in previous_items:
                            continue
                        deal = round(deal)

                        previous_items.add((item_name, price))

                        embed = discord.Embed(
                            title=f"Found big item for {deal}% deal!",
                            description=f"{item_name} \n https://www.rolimons.com/item/{item_id} \n https://www.roblox.com/catalog/{item_id}",
                            color=0x8F00FF
                            )

                        embed.set_author(
                            name="AUR.",
                            icon_url="https://media.discordapp.net/attachments/732902053290049538/1156618655388422184/AURt.png?ex=6515a090&is=65144f10&hm=c07a87a2fc89f9ddb06ccef22a43a69de87327f055c93dbc2c711f830ba58792&=&width=896&height=369"
                            )

                        embed.add_field(name="Price", value=f"{price}", inline=True)
                        embed.add_field(name="RAP", value=f"{rap}", inline=True)
                        embed.add_field(name="Value", value=f"{value}", inline=True)
                        embed.set_thumbnail(url=img)
                        embed.set_footer(text="AUR Deals - AUR.")

                        button = discord.ui.Button(style=discord.ButtonStyle.link, label="Item Link", url=f"https://www.roblox.com/catalog/{item_id}")
                        view = discord.ui.View()
                        view.add_item(button)

                        channel_id = 1185676878191800360
                        channel = bot.get_channel(channel_id)

                        message = await channel.send(f"<@&1185691784001638400>",embed=embed, view=view)
                        previous_items.add((item_name, price))
                      
                        
                    if deal >= 35 and not condition_to_ignore and value >= 1000 and item_info[5] is None:
                        if (item_name, price) in previous_items:
                            continue
                        deal = round(deal)
                        deal = int(deal)

                        embed = discord.Embed(
                            title=f"Found rap item for {deal}% deal!",
                            description=f"{item_name} \n https://www.rolimons.com/item/{item_id} \n https://www.roblox.com/catalog/{item_id}",
                            color=0x2ECE77
                        )

                        embed.set_author(
                            name="AUR.",
                            icon_url="https://media.discordapp.net/attachments/732902053290049538/1156618655388422184/AURt.png?ex=6515a090&is=65144f10&hm=c07a87a2fc89f9ddb06ccef22a43a69de87327f055c93dbc2c711f830ba58792&=&width=896&height=369"
                        )

                        embed.add_field(name="Price", value=f"{price}", inline=True)
                        embed.add_field(name="RAP", value=f"{rap}", inline=True)
                        embed.add_field(name="Value", value=f"{value}", inline=True)
                        embed.set_thumbnail(url=img)
                        embed.set_footer(text="AUR Deals - AUR.")

                        button = discord.ui.Button(style=discord.ButtonStyle.link, label="Item Link", url=f"https://www.roblox.com/catalog/{item_id}")
                        view = discord.ui.View()
                        view.add_item(button)

                        channel_id = 1139570344882081813
                        channel = bot.get_channel(channel_id)

                        message = await channel.send(f"<@&1143172281372262440>", embed=embed, view=view)
                        await message.publish()
                        previous_items.add((item_name, price))
                    
                                  

    except Exception as e:
        print(f"request failed: {e}")


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="AUR Deals"
        )
    )
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    await main.start()

bot.run('')
