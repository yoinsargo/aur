import requests
import json
import discord
from discord import app_commands
import aiohttp
import asyncio
import re
import time
import traceback
import random
from discord.ext import tasks

intents = discord.Intents.default()

intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)

class confirm(discord.ui.View):
    def __init__(self, userid: int, discid: int):
        super().__init__()
        self.userid = userid
        self.discid = discid
    @discord.ui.button(label="Check",style=discord.ButtonStyle.secondary)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.discid:
            return
        
        button.disabled = True
        await interaction.response.edit_message(view=self)
        try:
            check = requests.post(f"https://api.rolimons.com/auth/v1/verifyphrase/{self.userid}")
            print(check)
            check2 = check.json()
            print(check2)
            if check2["success"] == True:
                embed = discord.Embed(title="Successfully Verified!", description="Your credentials are now saved in the bot's database! \n ```/config``` \n Use the /config command to configure the bot.", color=0x00aeef)
                message = await interaction.channel.send(content=f"<@{self.discid}>", embed=embed)

                rolicookie = check.cookies.get("_RoliVerification")

                with open('data.json', 'r') as file:
                    data = json.load(file)

                if str(self.discid) in data:
                    data[str(self.discid)]['userid'] = self.userid
                    data[str(self.discid)]['cookie'] = rolicookie
                    data[str(self.discid)]['run'] = 0
                    data[str(self.discid)]['random'] = 0
                    data[str(self.discid)]['lastposted'] = 0

                else:
                    data[self.discid] = {
                        "userid": self.userid,
                        "cookie": rolicookie,
                        "run": 0,
                        "templates": [],
                        "random": 0,
                        "lastposted": 0,
                        "config": {
                            "offer": [],
                            "request": [],
                            "tags": [],
                            "robux": []
                            },
                        "activated": 0,
                        "passes": 9999,
                        "lastactivated": 0,
                        "timewait": 15,
                        "deactivatedin": 0
                        }

                with open('data.json', 'w') as file:
                    json.dump(data, file, indent=4)

                

            else:
                error = check2["message"]
                embed = discord.Embed(title=f"❌Verification was unsuccessful!", description=f"There has been an error in the verification process. \n \n **Details: ```{error}```**", color=0x000000)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                await interaction.channel.send(content=f"<@{self.discid}> <@732901432122146908>", embed=embed)
                return
        except Exception as e:
            embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            await interaction.channel.send(embed=embed)
            return

class Config(discord.ui.Modal, title='CONFIG'):
    
    offerids = discord.ui.TextInput(
        label='Offer IDs',
        style=discord.TextStyle.long,
        placeholder='Submit a MAXIMUM of 4 item ids, separated by commas with no spaces \n \n e.g 1029025,1365767,1029025',
        required=True,
        max_length=300,
    )

    requestids = discord.ui.TextInput(
        label='Request IDs',
        style=discord.TextStyle.long,
        placeholder='Same as OFFER IDS \n \n Total number of REQUEST ITEMS + REQUEST TAGS should be a MAXIMUM of 4',
        required=False,
        max_length=300,
    )

    requesttags = discord.ui.TextInput(
        label='Request Tags',
        style=discord.TextStyle.long,
        placeholder="ALL TAGS need to be with commas with no spaces \n \n e.g 'rap','adds','upgrade','downgrade','demand'",
        required=False,
        max_length=300,
    )

    requesttags = discord.ui.TextInput(
        label='Request Tags',
        style=discord.TextStyle.long,
        placeholder="ALL TAGS need to be in commas with no spaces \n \n e.g rap,adds,upgrade,downgrade,demand",
        required=False,
        max_length=300,
    )

    robux = discord.ui.TextInput(
        label='Robux',
        style=discord.TextStyle.long,
        placeholder="A SINGLE integer with no commas. \n \n NEEDS to be under 50% of the offer value \n \n e.g 30000",
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        discid = interaction.user.id
        with open('data.json', 'r') as file:
            data = json.load(file)
            
        if str(discid) in data:
            userinfo = data[str(discid)]
            userid = userinfo['userid']
            cookie = userinfo['cookie']
            config = userinfo['config']
            
            headers = {"Content-Type": "Application/json"}
            cookies = {"_RoliVerification": cookie}

            try:
                offer_item_ids = [int(id.strip()) for id in self.offerids.value.split(',') if id.strip()]
                request_item_ids = [int(id.strip()) for id in self.requestids.value.split(',') if id.strip()]
                request_tags = [tag.strip() for tag in self.requesttags.value.split(',') if tag.strip()]
                robux = int(self.robux.value) if self.robux.value else None
            except:
                embed = discord.Embed(title=f"❌ Your config submission has errors!", description=f"Please read the instructions carefully and retry!", color=0x000000)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                await interaction.followup.send(content=f"<@{discid}>",embed=embed)

            json_data = {
                "player_id": userid,
                "offer_item_ids": offer_item_ids,
                "request_item_ids": request_item_ids,
                "request_tags": request_tags,
                }

            if robux is not None:
                json_data["offer_robux"] = robux

            try:
                resp = requests.post(
                    'https://api.rolimons.com/tradeads/v1/createad',
                    headers=headers,
                    cookies=cookies,
                    data=json.dumps(json_data)
                    ).json()
                if resp["success"] == True:
                    embed = discord.Embed(title="Successfully Changed Configuration!", description="Your config are now saved in the bot's database! \n ```/start``` \n Use the /start command to start the bot.", color=0x00aeef)
                    message = await interaction.channel.send(content=f"<@{discid}>", embed=embed)

                    if userinfo['random'] == 1:
                        data[str(discid)]['random'] = 0
                    if userinfo['run'] == 1:
                        data[str(discid)]['run'] = 0

                    data[str(discid)]['lastposted'] = int(time.time())

                    config['offer'] = offer_item_ids
                    config['request'] = request_item_ids
                    config['tags'] = request_tags

                    if robux is not None:
                        config['robux'] = robux
                    else:
                        config['robux'] = 0

                    with open('data.json', 'w') as file:
                        json.dump(data, file, indent=4)


                else:
                    error = resp["message"]
                    embed = discord.Embed(title=f"❌ Config was unsuccessful!", description=f"There has been an error in the configuration process. \n \n **Details: ```{error}```** \n \n Keep in mind the bot does a test post each time you configure.", color=0x000000)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.channel.send(content=f"<@{discid}> <@732901432122146908>", embed=embed)

                
            except Exception as e:
                embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                await interaction.followup.send(embed=embed)
        
            
        
        

class configbuttons(discord.ui.View):
    def __init__(self, discid: int):
        super().__init__()
        self.discid = discid
        self.buttons_disabled = False
    @discord.ui.button(label="Open",style=discord.ButtonStyle.secondary)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.discid:
            return
        
        button.disabled = True
        await interaction.response.send_modal(Config())

        

class randombuttons(discord.ui.View):
    def __init__(self, discid: int):
        super().__init__()
        self.discid = discid
        self.buttons_disabled = False
    @discord.ui.button(label="Yes",style=discord.ButtonStyle.secondary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.discid:
            return

        self.disable_buttons()
        await interaction.response.edit_message(view=self)

        with open('data.json', 'r') as file:
            data = json.load(file)
            
        if str(self.discid) in data:
            data[str(self.discid)]['random'] = 1

        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(title="Successfully turned on random mode!", description="Use the following command to start the bot! \n ```/start```", color=0x00aeef)
        message = await interaction.channel.send(content=f"<@{self.discid}>", embed=embed)
    @discord.ui.button(label="No",style=discord.ButtonStyle.secondary)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.discid:
            return
        
        self.disable_buttons()
        await interaction.response.edit_message(view=self)

        embed = discord.Embed(title="Fill out the config below.", description="Read each box carefully. \n \n **Additional information:** \n \n ...", color=0x00aeef)
        embed.add_field(name="Offer ITEM IDs", value=f"Submit a MAXIMUM of 4 item ids, separated by commas with no spaces \n \n e.g 1029025,1365767,1029025 \n \n If you have more than 1 of an item, put the item id as many as you want to put. \n \n ...", inline=False)
        embed.add_field(name="Request ITEM IDs", value=f"Submit a MAXIMUM of 4 item ids, separated by commas with no spaces \n \n Total number of REQUEST ITEMS + REQUEST TAGS should be a MAXIMUM of 4 \n \n If you want more than 1 of an item, put the item id as many as you want to put. e.g 1029025,1365767,1029025 \n \n ...", inline=False)
        embed.add_field(name="Request TAGS", value=f"ALL TAGS need to be separated by commas with no spaces. \n \n Total number of REQUEST ITEMS + REQUEST TAGS should be a MAXIMUM of 4 \n \n **All possible tags:** \n \n rap,adds,upgrade,downgrade,demand \n \n ...", inline=False)
        embed.add_field(name="Offer ROBUX", value=f"A SINGLE integer with no commas. \n \n NEEDS to be under 50% of the offer value \n \n e.g 30000", inline=False)
        view = configbuttons(self.discid)
        message = await interaction.channel.send(content=f"<@{self.discid}>", embed=embed, view=view)
                

    def disable_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        self.buttons_disabled = True

    

tree = app_commands.CommandTree(client)

@tree.command(name="verify", description="Verify yourself for the trade ad bot")
async def the_command(interaction, userid: int):
    await interaction.response.defer()
    discid = interaction.user.id
    try:
            
        phrase = requests.get(f"https://api.rolimons.com/auth/v1/getphrase/{userid}").json()

        if phrase["success"] == True:
            phrase = phrase["phrase"]
            embed = discord.Embed(title=f"Recieved your phrase!", description=f"Add the following phrase in your ROBLOX About Me: \n ```{phrase}```", color=0x00aeef)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            view = confirm(userid, discid)
            await interaction.followup.send(embed=embed, view=view)
        else:
            embed = discord.Embed(title=f"❌User ID doesnt exist!", description=f"The User ID you inputted is incorrect!", color=0x000000)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            await interaction.followup.send(embed=embed)
            return

    except Exception as e:
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
        await interaction.followup.send(embed=embed)
        return

@tree.command(name="config", description="Configure your Trade AD settings")
async def the_command(interaction):
    await interaction.response.defer()
    discid = interaction.user.id
    try:
            
        with open('data.json', 'r') as file:
            data = json.load(file)
            
        if str(discid) in data:
            userinfo = data[str(discid)]
            userid = userinfo['userid']

            embed = discord.Embed(title=f"Would you like to turn on randomized mode?", description=f"This mode will post trade ads every 15 minutes with random items from your inventory and random tags. \n ", color=0x00aeef)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            view = randombuttons(discid)
            await interaction.followup.send(embed=embed, view=view)
        else:
            embed = discord.Embed(title=f"❌ You need to be verified to do this!", description=f"Please use the following command to verify ```/verify```", color=0x000000)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            await interaction.followup.send(embed=embed)
            return
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(traceback_str)
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
        await interaction.followup.send(embed=embed)
        return

@tree.command(name="start", description="Start the Trade AD bot")
async def the_command(interaction):
    await interaction.response.defer()
    discid = interaction.user.id
    try:
                
        with open('data.json', 'r') as file:
            data = json.load(file)

        if str(discid) in data:
            userinfo = data[str(discid)]
            userid = userinfo['userid']
            cookie = userinfo['cookie']
            random = userinfo['random']
            run = userinfo['run']
            config = userinfo['config']
            offeritems = config['offer']

            if run == 0:
                if random == 1:
                    embed = discord.Embed(title=f"Started bot! [RANDOM MODE]", description=f"Not your preffered config? Use the /config command to change this ```/config``` ", color=0x00aeef)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)

                    data[str(discid)]['run'] = 1

                    with open('data.json', 'w') as file:
                        json.dump(data, file, indent=4)

                    return
                        
                elif offeritems:
                    embed = discord.Embed(title=f"Started bot! [CUSTOM MODE]", description=f"Not your preffered config? Use the /config command to change this ```/config```  \n \n Use the /stop command to stop the bot.", color=0x00aeef)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)

                    data[str(discid)]['run'] = 1

                    with open('data.json', 'w') as file:
                        json.dump(data, file, indent=4)

                    return

                else:
                    embed = discord.Embed(title=f"❌ You do not have a config!", description=f"Please use the following command to make your config ```/config```", color=0x000000)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)
                    return
                    

            else:
                embed = discord.Embed(title=f"❌ The bot is already running!", description=f"Use the following command to stop the bot. ```/stop```", color=0x000000)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                await interaction.followup.send(embed=embed)
                return
        else:
            embed = discord.Embed(title=f"❌ You need to be verified to do this!", description=f"Please use the following command to verify ```/verify```", color=0x000000)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            await interaction.followup.send(embed=embed)
            return

        
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(traceback_str)
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
        await interaction.followup.send(embed=embed)
        return

@tree.command(name="stop", description="Stop the Trade AD bot")
async def the_command(interaction):
    await interaction.response.defer()
    discid = interaction.user.id
    try:
                
        with open('data.json', 'r') as file:
            data = json.load(file)

        if str(discid) in data:
            userinfo = data[str(discid)]
            userid = userinfo['userid']
            cookie = userinfo['cookie']
            random = userinfo['random']
            run = userinfo['run']
            config = userinfo['config']
            offeritems = config['offer']

            if run == 1:
                if random == 1:
                    embed = discord.Embed(title=f"Stopped bot! [RANDOM MODE]", description=f"Not your preffered config? Use the /config command to change this ```/config``` ", color=0x00aeef)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)

                    data[str(discid)]['run'] = 0

                    with open('data.json', 'w') as file:
                        json.dump(data, file, indent=4)

                    return
                        
                elif offeritems:
                    embed = discord.Embed(title=f"Stopped bot! [CUSTOM MODE]", description=f"Not your preffered config? Use the /config command to change this ```/config``` ", color=0x00aeef)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)

                    data[str(discid)]['run'] = 0

                    with open('data.json', 'w') as file:
                        json.dump(data, file, indent=4)

                    return

                else:
                    embed = discord.Embed(title=f"❌ You do not have a config!", description=f"Please use the following command to make your config ```/config```", color=0x000000)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)
                    return
                    

            else:
                embed = discord.Embed(title=f"❌ The bot is not running!", description=f"Use the following command to stop the bot. ```/stop```", color=0x000000)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                await interaction.followup.send(embed=embed)
                return
        else:
            embed = discord.Embed(title=f"❌ You need to be verified to do this!", description=f"Please use the following command to verify ```/verify```", color=0x000000)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            await interaction.followup.send(embed=embed)
            return

        
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(traceback_str)
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
        await interaction.followup.send(embed=embed)
        return

@tree.command(name="postinterval", description="Change the time between each post on the trade ad bot [MINIMUM 15 MINUTES]")
async def the_command(interaction, minutes: int):
    await interaction.response.defer()
    discid = interaction.user.id
    try:
                
        with open('data.json', 'r') as file:
            data = json.load(file)

        if str(discid) in data:
            userinfo = data[str(discid)]
            userid = userinfo['userid']
            cookie = userinfo['cookie']
            random = userinfo['random']
            run = userinfo['run']
            config = userinfo['config']
            offeritems = config['offer']
            passes = userinfo['passes']
            active = userinfo['activated']
            lastactive = userinfo['lastactivated']
            deactive = userinfo['deactivatedin']

            if minutes < 15:
                embed = discord.Embed(title=f"❌ Too low!", description=f"Your post time is too low. [MINIMUM 15 MINUTES]", color=0x000000)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                await interaction.followup.send(embed=embed)
                return

            else:
                data[str(discid)]['timewait'] = minutes

                with open('data.json', 'w') as file:
                    json.dump(data, file, indent=4)

                    embed = discord.Embed(title=f"Changed time!", description=f"The bot will now post your trade ads every **{minutes}** minutes!", color=0x00aeef)
                    embed.set_footer(text="AUR Utilities - AUR.")
                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                    await interaction.followup.send(embed=embed)
                    return

           
        else:
            embed = discord.Embed(title=f"❌ You need to be verified to do this!", description=f"Please use the following command to verify ```/verify```", color=0x000000)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
            await interaction.followup.send(embed=embed)
            return

        
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(traceback_str)
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0x000000)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
        await interaction.followup.send(embed=embed)
        return

@tasks.loop(seconds=1)
async def postads():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)

        for discid, userdata in data.items():
            userid = userdata['userid']
            cookie = userdata['cookie']
            random_value = userdata['random']
            run = userdata['run']
            config = userdata['config']
            offeritems = config['offer']
            lastposted = userdata["lastposted"]
            timewait = userdata["timewait"]

            if run == 1:

                await asyncio.sleep(1)
                if int(time.time())-lastposted >= (timewait*60):
                    if random_value == 1:
                        request_tags = ["rap", "adds", "upgrade", "downgrade", "demand"]
                        itemids = []
                        x = requests.get(f"https://inventory.roblox.com/v1/users/{userid}/assets/collectibles?sortOrder=Asc&limit=100").json()

                        try:
                            for i in x['data']:
                                hold = i['isOnHold']

                                if hold == False:
                                    itemids.append(i['assetId'])
                                
                        except:
                            error = x["errors"][0]["message"]

                            data[str(discid)]['run'] = 0

                            with open('data.json', 'w') as file:
                                json.dump(data, file, indent=4)

                            channel_id = 1240714238465671178
                            channel = client.get_channel(channel_id)

                            embed = discord.Embed(title=f"❌ Trade AD post was unsuccessful!", description=f"There has been an error in the posting process, the bot has been turned off for this. \n \n **Details: ```{error}```**", color=0x000000)
                            embed.set_footer(text="AUR Utilities - AUR.")
                            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                            await channel.send(content=f"<@{discid}>", embed=embed)
                            continue

                        headers = {"Content-Type": "Application/json"}
                        cookies = {"_RoliVerification": cookie}

                        if len(itemids) >= 4:
                            randomoffer = random.sample(itemids, 4)
                        else:
                            randomoffer = itemids
                        RequestTags = random.sample(request_tags, random.randint(1, min(4, len(request_tags))))

                        json_data = {
                            "player_id": userid,
                            "offer_item_ids": randomoffer,
                            "request_item_ids": [],
                            "request_tags": RequestTags
                            }

                        try:
                            resp = requests.post(
                                'https://api.rolimons.com/tradeads/v1/createad',
                                headers=headers,
                                cookies=cookies,
                                data=json.dumps(json_data)
                                ).json()

                            if resp["success"] == True:

                                data[str(discid)]['lastposted'] = int(time.time())

                                with open('data.json', 'w') as file:
                                    json.dump(data, file, indent=4)

                                channel_id = 1240714238465671178
                                channel = client.get_channel(channel_id)

                                embed = discord.Embed(title=f"Posted a trade ad! [RANDOM MODE]", description=f"The bot has successfully posted a trade ad on the following account: \n ```{userid}```", color=0x00aeef)
                                embed.set_footer(text="AUR Utilities - AUR.")
                                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                                await channel.send(content=f"<@{discid}>",embed=embed)
                                continue

                            else:
                                error = resp["message"]

                                if error == "Ad creation cooldown has not elapsed":
                                    data[str(discid)]['lastposted'] = int(time.time())

                                    with open('data.json', 'w') as file:
                                        json.dump(data, file, indent=4)
                                        
                                    channel_id = 1240714238465671178
                                    channel = client.get_channel(channel_id)
                                    
                                    embed = discord.Embed(title=f"❌ Trade AD post was unsuccessful!", description=f"There has been an error in the posting process, however the bot is still running. \n \n **Details: ```{error}```** \n \n Keep in mind the bot does a test post each time you configure.", color=0x000000)
                                    embed.set_footer(text="AUR Utilities - AUR.")
                                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                                    await channel.send(content=f"<@{discid}>", embed=embed)
                                    continue

                                else:
                                    data[str(discid)]['run'] = 0

                                    with open('data.json', 'w') as file:
                                        json.dump(data, file, indent=4)

                                    channel_id = 1240714238465671178
                                    channel = client.get_channel(channel_id)

                                    embed = discord.Embed(title=f"❌ Trade AD post was unsuccessful!", description=f"There has been an error in the posting process, the bot has been stopped for this. \n \n **Details: ```{error}```**", color=0x000000)
                                    embed.set_footer(text="AUR Utilities - AUR.")
                                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                                    await channel.send(content=f"<@{discid}>", embed=embed)
                                    continue
                        except Exception as e:
                            print(e)

                    else:
                        requestitems = config['request']
                        tags = config['tags']
                        robux = config['robux']

                        headers = {"Content-Type": "Application/json"}
                        cookies = {"_RoliVerification": cookie}

                        json_data = {
                            "player_id": userid,
                            "offer_item_ids": offeritems,
                            "request_item_ids": requestitems,
                            "request_tags": tags
                            }
                        if robux != 0:
                            json_data["offer_robux"] = robux

                        try:
                            resp = requests.post(
                                'https://api.rolimons.com/tradeads/v1/createad',
                                headers=headers,
                                cookies=cookies,
                                data=json.dumps(json_data)
                                ).json()

                            if resp["success"] == True:

                                data[str(discid)]['lastposted'] = int(time.time())

                                with open('data.json', 'w') as file:
                                    json.dump(data, file, indent=4)
                                
                                channel_id = 1240714238465671178
                                channel = client.get_channel(channel_id)

                                embed = discord.Embed(title=f"Posted a trade ad! [CUSTOM MODE]", description=f"The bot has successfully posted a trade ad on the following account: \n ```{userid}```", color=0x00aeef)
                                embed.set_footer(text="AUR Utilities - AUR.")
                                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                                await channel.send(content=f"<@{discid}>",embed=embed)
                                continue

                            else:
                                error = resp["message"]

                                if error == "Ad creation cooldown has not elapsed":
                                    data[str(discid)]['lastposted'] = int(time.time())

                                    with open('data.json', 'w') as file:
                                        json.dump(data, file, indent=4)

                                    channel_id = 1240714238465671178
                                    channel = client.get_channel(channel_id)
                                    
                                    embed = discord.Embed(title=f"❌ Trade AD post was unsuccessful!", description=f"There has been an error in the posting process, however the bot is still running. \n \n **Details: ```{error}```** \n \n Keep in mind the bot does a test post each time you configure.", color=0x000000)
                                    embed.set_footer(text="AUR Utilities - AUR.")
                                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                                    await channel.send(content=f"<@{discid}>", embed=embed)
                                    continue

                                else:
                                    data[str(discid)]['run'] = 0

                                    with open('data.json', 'w') as file:
                                        json.dump(data, file, indent=4)

                                    channel_id = 1240714238465671178
                                    channel = client.get_channel(channel_id)

                                    embed = discord.Embed(title=f"❌ Trade AD post was unsuccessful!", description=f"There has been an error in the posting process, the bot has been stopped for this. \n \n **Details: ```{error}```**", color=0x000000)
                                    embed.set_footer(text="AUR Utilities - AUR.")
                                    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1240712031724900493/1240723622566559765/AURblue.png?ex=6647996b&is=664647eb&hm=56232c01c38995d863eb1e475ac9b4481a63e20af1f09486e55e173461e3d5be&")
                                    await channel.send(content=f"<@{discid}>", embed=embed)
                                    continue
                        except Exception as e:
                            print(e)
                                            
    except Exception as e:
        print(e)


@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(
      activity=discord.Activity(
      type=discord.ActivityType.watching,
      name="AUR Trade ADS"
      )
    )
    print("ready")
    await postads.start()
    

bot_token = ''
client.run(bot_token)

