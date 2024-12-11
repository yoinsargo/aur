import requests
import re
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import discord
from discord import app_commands
import aiohttp
import asyncio
import traceback
import time

intents = discord.Intents.default()

intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

@tree.command(name="inventory", description="Generate a user's inventory")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def the_command(interaction, username: str):
    await interaction.response.defer()
    discid = interaction.user.id
    embed = discord.Embed(title=f"Generating {username}'s inventory...", description="<a:aurT:1166031422058934473> Awaiting command info...", color=0xffa200)
    embed.set_footer(text="AUR Utilities - AUR.")
    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")

    message = await interaction.followup.send(embed=embed)

    try:
        data = {
            "usernames": [f"{username}"],
            "excludeBannedUsers": "true"
            }
        userid = requests.post("https://users.roblox.com/v1/usernames/users", json=data).json()
        
        try:

            userid = userid["data"][0]["id"]
        except:
            embed = discord.Embed(title=f"❌Incorrect Username!", description=f"{username} does not exist!", color=0xff0004)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)
            return

        r = requests.get(f"https://www.rolimons.com/player/{userid}").text


        itemdetails = re.findall(r'var item_list\s*=\s*({[^}]*})', r)
        inv = re.findall(r'var scanned_player_assets\s*=\s*({[^}]*})', r)
        player = re.findall(r'var\s+player_details_data\s*=\s*({[^;]+})',r)

        

        if itemdetails and inv:
            itemdetails_json = json.loads(itemdetails[0])
            inv_json = json.loads(inv[0])
            player_json = json.loads(player[0])

            asking = player_json["asking_list"]


            generated_images = []

            total_value = 0

            try:
                bust = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false").json()
                print(bust)
                bust = bust["data"][0]["imageUrl"]
            except:
                embed = discord.Embed(title=f"❌Ratelimit!", description=f"Encountered a ratelimit, Please try again in a bit", color=0xff0004)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
                await message.edit(embed=embed)
                return
            invsize = 0

            for item_id, item_data in inv_json.items():

                hold = 0
                num_items = len(item_data)

                for item in item_data:
                    timestamp = int(item[3])
                    timestamp = timestamp/1000

                current_time = int(time.time())

                if abs(current_time - timestamp) <= 2 * 24 * 60 * 60:
                    hold += 1

                if item_id in itemdetails_json:

                    item_name = itemdetails_json[item_id][0]

                    if itemdetails_json[item_id][1] is not None:
                        item_name = itemdetails_json[item_id][1]

                    if item_name:
                        embed = discord.Embed(title=f"Generating {username}'s inventory...", description="<a:aurT:1166031422058934473> Generating item cards...", color=0xffa200)
                        embed.set_footer(text="AUR Utilities - AUR.")
                        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")

                        thumbnail = itemdetails_json[item_id][10]
                        value = itemdetails_json[item_id][5]
                        rare = itemdetails_json[item_id][9]
                        proj = itemdetails_json[item_id][7]

                        projstatus = 0

                        if proj is not None:
                            projstatus += 1

                        rarestatus = 0

                        if rare is not None:
                            rarestatus += 1

                        total_value += value*num_items

                        askingdata = None

                        try:
                            for asset in asking['assets']:
                                askingid = asset.get('id')
                                if int(askingid) == int(item_id):
                                    askingdata = asset
                        except:
                            askingdata = None

                        dg = 0
                        upg = 0
                        nft = 0




                        if askingdata:
                            try:
                                askingdata["upgrade"]
                                background_image = Image.open('itemcardupg2.png')
                                val = "#3296e3"
                                upg += 1
                            except:
                                try:
                                    askingdata["downgrade"]
                                    background_image = Image.open('itemcarddg2.png')
                                    val = "#3296e3"
                                    dg += 1
                                except:
                                    try:
                                        askingdata["nft"]
                                        background_image = Image.open('itemcardnft2.png')
                                        val = "#3296e3"
                                        nft += 1
                                    except:
                                        background_image = Image.open('item card2.png')
                                        val = "#3296e3"
                        else:
                            background_image = Image.open('item card2.png')
                            val = "#3296e3"

                        response = requests.get(thumbnail)

                        if response.status_code == 200:
                            thumbnail_image = Image.open(BytesIO(response.content))
                            thumbnail_image = thumbnail_image.resize((500, 500))
                            thumbnail_image = thumbnail_image.convert("RGBA")
                            background_image.paste(thumbnail_image, (95, 115), thumbnail_image)

                        draw = ImageDraw.Draw(background_image)
                        custom_font = ImageFont.truetype("mainfont.otf", 40)

                        character_count = len(item_name)

                        if character_count >=10:
                            item_name = item_name[:10]
                            item_name = f"{item_name}..."

                        name = "#fab048"
                        draw.text((75, 740), item_name, fill=name, font=custom_font)

                        custom_font = ImageFont.truetype("mainfont.otf", 70)

                        draw.text((75, 780), format(value, ","), fill=val, font=custom_font)

                        if num_items > 1:
                            custom_font = ImageFont.truetype("mainfont.otf", 100)
                            text_color = "#212121"
                            if upg > 0:
                                pill_color = "#31C667"
                            elif dg > 0:
                                pill_color = "#0881da"
                            elif nft > 0:
                                pill_color = "#ff0004"
                            else:
                                pill_color = "#fab048"

                            text = f'x{num_items}'
                            bbox = draw.textbbox((0, 0), text, font=custom_font)
                            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

                            x1, y1 = 75, 75
                            x2 = x1 + text_width + 10
                            y2 = y1 + text_height + 10

                            radius = (y2 - y1) // 2

                            draw.ellipse([x1, y1, x1 + radius * 2, y2], fill=pill_color)
                            draw.ellipse([x2 - radius * 2, y1, x2, y2], fill=pill_color)
                            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=pill_color)
                            if num_items < 10:
                                text_position = (x1 + 30, y1 + 7.5)
                            else:
                                text_position = (x1 + 40, y1 + 7.5)

                            custom_font = ImageFont.truetype("mainfont.otf", 80)
                            draw.text(text_position, text, fill=text_color, font=custom_font)

                        if hold >= 1:
                            if upg > 0:
                                holdlogo = Image.open('holdingupg.png')
                            elif dg >0:
                                holdlogo = Image.open('holdingdg.png')
                            elif nft >0:
                                holdlogo = Image.open('holdingnft.png')
                            else:
                                holdlogo = Image.open('holding4.png')
                            holdlogo = holdlogo.resize((120, 120))
                            holdlogo = holdlogo.convert("RGBA")
                            background_image.paste(holdlogo, (510, 70), holdlogo)

                        if rarestatus > 0:
                            rare = Image.open("rare.png")
                            rare = rare.resize((100, 100))
                            rare = rare.convert("RGBA")
                            background_image.paste(rare, (80, 620), rare)

                        if projstatus > 0:
                            if rarestatus > 0:
                                proj = Image.open("proj.png")
                                proj = proj.resize((100, 100))
                                proj = proj.convert("RGBA")
                                background_image.paste(proj, (160, 620), proj)
                            else:
                                proj = Image.open("proj.png")
                                proj = proj.resize((100, 100))
                                proj = proj.convert("RGBA")
                                background_image.paste(proj, (80, 620), proj)

                        resize = background_image.resize((140, 180))

                        generated_images.append({
                            "image": resize.copy(),
                            "value": value
                        })

            generated_images = sorted(generated_images, key=lambda x: x["value"], reverse=True)

            col_number = 0
            row_number = 0

            embed = discord.Embed(title=f"Generating {username}'s inventory...", description="Pasting item cards...", color=0xffa200)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)

            inv_background = Image.open('invv2.png')
            inv_background = inv_background.convert("RGBA")

            first_row_item_count = 4
            total_rows = (len(generated_images) - first_row_item_count + 5 - 1) // 5
            items_in_last_row = (len(generated_images) - first_row_item_count) % 5

            print(items_in_last_row)

            for i, image_info in enumerate(generated_images):
                items_per_row = 5
                col_start_x = (col_number * 155) + 20
                row_start_y = (100 + row_number * 220) + 25

                if row_number == 0:
                    img = image_info["image"].copy()
                    img = img.resize((int(img.width * 1.2), int(img.height * 1.2)))
                    img.convert("RGBA")
                    items_per_row = 4
                    col_start_x = (col_number * 197) + 20
                else:
                    img = image_info["image"]
                    img.convert("RGBA")

                if row_number == 1:
                    row_start_y = (100 + row_number * 240) + 25

                if row_number == 2:
                    row_start_y = (100 + row_number * 220) + 25

                if row_number == 3:
                    row_start_y = (100 + row_number * 215) + 25

                inv_background.paste(img, (col_start_x, row_start_y), img)

                col_number += 1
                if col_number >= items_per_row:
                    col_number = 0
                    row_number += 1

            draw = ImageDraw.Draw(inv_background)
            custom_font = ImageFont.truetype("mainfont.otf", 40)

            total_value = format(total_value, ",")

            embed = discord.Embed(title=f"Generating {username}'s inventory...", description="<a:aurT:1166031422058934473> Finalizing...", color=0xffa200)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)

            text_color = "#fab048"
            top_text = f"{username}"
            bottom_text = f"TOTAL VALUE: {total_value}"
            top_font = ImageFont.truetype("mainfont.otf", 40)
            bottom_font = ImageFont.truetype("mainfont.otf", 20)
            print("done")
            top_bbox = draw.textbbox((0, 0), top_text, font=top_font)
            top_text_width, top_text_height = top_bbox[2] - top_bbox[0], top_bbox[3] - top_bbox[1]
            text_x = 20
            print("texttop")

            draw.text((text_x, 20), top_text, fill=text_color, font=top_font)

            bottom_bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
            bottom_text_width, bottom_text_height = bottom_bbox[2] - bottom_bbox[0], bottom_bbox[3] - bottom_bbox[1]
            print("text bottom")

            draw.text((20, 65), bottom_text, fill=text_color, font=bottom_font)

            response = requests.get(bust)

            if response.status_code == 200:
                thumbnail_image = Image.open(BytesIO(response.content))
                thumbnail_image = thumbnail_image.resize((92, 92))
                thumbnail_image = thumbnail_image.convert("RGBA")

                thumbnail_x = max(text_x + top_text_width, 20 + bottom_text_width) + 25

                inv_background.paste(thumbnail_image, (thumbnail_x, 5), thumbnail_image)

            inv_background.save(f"main.png")
            print("upload")

            image_path = 'main.png'

            channel2 = client.get_channel(1245379184952606741)
            with open('main.png', 'rb') as f:
                message2 = await channel2.send(file=discord.File(f, 'main.png'))

            image_url = message2.attachments[0].url


            embed = discord.Embed(title=f"Generated {username}'s inventory below!", description=f"https://www.rolimons.com/player/{userid}", color=0xffa200)
            embed.set_thumbnail(url=bust)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.add_field(name="Username", value=f"{username}", inline=True)
            embed.add_field(name="Total Value", value=f"{total_value}", inline=True)
            embed.set_image(url=image_url)
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)

    except asyncio.TimeoutError:
        embed = discord.Embed(title="❌ Timeout", description="The operation took too long to complete, please use a different user", color=0xff0004)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
        await message.edit(embed=embed)
        return

    except Exception as e:
        dtraceback = traceback.format_exc()
        print(dtraceback)
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0xff0004)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
        await message.edit(embed=embed)
        return

@tree.command(name="inventory2", description="Generate a user's inventory in an updated style")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def the_command(interaction, username: str):
    await interaction.response.defer()
    discid = interaction.user.id
    embed = discord.Embed(title=f"Generating {username}'s inventory...", description="<a:aurT:1166031422058934473> Awaiting command info...", color=0xffa200)
    embed.set_footer(text="AUR Utilities - AUR.")
    embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")

    message = await interaction.followup.send(embed=embed)

    try:
        data = {
            "usernames": [f"{username}"],
            "excludeBannedUsers": "true"
            }
        userid = requests.post("https://users.roblox.com/v1/usernames/users", json=data).json()
        
        try:

            userid = userid["data"][0]["id"]
        except:
            embed = discord.Embed(title=f"❌Incorrect Username!", description=f"{username} does not exist!", color=0xff0004)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)
            return

        r = requests.get(f"https://www.rolimons.com/player/{userid}").text


        itemdetails = re.findall(r'var item_list\s*=\s*({[^}]*})', r)
        inv = re.findall(r'var scanned_player_assets\s*=\s*({[^}]*})', r)
        player = re.findall(r'var\s+player_details_data\s*=\s*({[^;]+})',r)

        

        if itemdetails and inv:
            itemdetails_json = json.loads(itemdetails[0])
            inv_json = json.loads(inv[0])
            player_json = json.loads(player[0])

            asking = player_json["asking_list"]


            generated_images = []

            total_value = 0

            try:
                bust = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false").json()
                print(bust)
                bust = bust["data"][0]["imageUrl"]
            except:
                embed = discord.Embed(title=f"❌Ratelimit!", description=f"Encountered a ratelimit, Please try again in a bit", color=0xff0004)
                embed.set_footer(text="AUR Utilities - AUR.")
                embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
                await message.edit(embed=embed)
                return
            invsize = 0

            for item_id, item_data in inv_json.items():

                hold = 0
                num_items = len(item_data)

                for item in item_data:
                    timestamp = int(item[3])
                    timestamp = timestamp/1000

                current_time = int(time.time())

                if abs(current_time - timestamp) <= 2 * 24 * 60 * 60:
                    hold += 1

                if item_id in itemdetails_json:

                    item_name = itemdetails_json[item_id][0]

                    if itemdetails_json[item_id][1] is not None:
                        item_name = itemdetails_json[item_id][1]

                    if item_name:
                        embed = discord.Embed(title=f"Generating {username}'s inventory...", description="<a:aurT:1166031422058934473> Generating item cards...", color=0xffa200)
                        embed.set_footer(text="AUR Utilities - AUR.")
                        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")

                        thumbnail = itemdetails_json[item_id][10]
                        value = itemdetails_json[item_id][5]
                        rare = itemdetails_json[item_id][9]
                        proj = itemdetails_json[item_id][7]

                        projstatus = 0

                        if proj is not None:
                            projstatus += 1

                        rarestatus = 0

                        if rare is not None:
                            rarestatus += 1

                        total_value += value*num_items

                        askingdata = None

                        try:
                            for asset in asking['assets']:
                                askingid = asset.get('id')
                                if int(askingid) == int(item_id):
                                    askingdata = asset
                        except:
                            askingdata = None

                        dg = 0
                        upg = 0
                        nft = 0




                        if askingdata:
                            try:
                                askingdata["upgrade"]
                                background_image = Image.open('futureupg.png')
                                val = "#3296e3"
                                upg += 1
                            except:
                                try:
                                    askingdata["downgrade"]
                                    background_image = Image.open('futuredg.png')
                                    val = "#3296e3"
                                    dg += 1
                                except:
                                    try:
                                        askingdata["nft"]
                                        background_image = Image.open('futurenft.png')
                                        val = "#3296e3"
                                        nft += 1
                                    except:
                                        background_image = Image.open('futurenormal.png')
                                        val = "#3296e3"
                        else:
                            background_image = Image.open('futurenormal.png')
                            val = "#3296e3"

                        response = requests.get(thumbnail)

                        if response.status_code == 200:
                            thumbnail_image = Image.open(BytesIO(response.content))
                            thumbnail_image = thumbnail_image.resize((500, 500))
                            thumbnail_image = thumbnail_image.convert("RGBA")
                            background_image.paste(thumbnail_image, (95, 115), thumbnail_image)

                        draw = ImageDraw.Draw(background_image)
                        custom_font = ImageFont.truetype("mainfont.otf", 40)

                        character_count = len(item_name)

                        if character_count >=10:
                            item_name = item_name[:10]
                            item_name = f"{item_name}..."

                        name = "#fab048"
                        draw.text((75, 740), item_name, fill=name, font=custom_font)

                        custom_font = ImageFont.truetype("mainfont.otf", 70)

                        draw.text((75, 780), format(value, ","), fill=val, font=custom_font)

                        if num_items > 1:
                            custom_font = ImageFont.truetype("mainfont.otf", 100)
                            text_color = "#212121"
                            if upg > 0:
                                pill_color = "#31C667"
                            elif dg > 0:
                                pill_color = "#0881da"
                            elif nft > 0:
                                pill_color = "#ff0004"
                            else:
                                pill_color = "#fab048"

                            text = f'x{num_items}'
                            bbox = draw.textbbox((0, 0), text, font=custom_font)
                            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

                            x1, y1 = 75, 75
                            x2 = x1 + text_width + 10
                            y2 = y1 + text_height + 10

                            radius = (y2 - y1) // 2

                            draw.ellipse([x1, y1, x1 + radius * 2, y2], fill=pill_color)
                            draw.ellipse([x2 - radius * 2, y1, x2, y2], fill=pill_color)
                            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=pill_color)
                            if num_items < 10:
                                text_position = (x1 + 30, y1 - 7.5)
                            else:
                                text_position = (x1 + 40, y1 - 7.5)

                            custom_font = ImageFont.truetype("mainfont.otf", 80)
                            draw.text(text_position, text, fill=text_color, font=custom_font)

                        if hold >= 1:
                            if upg > 0:
                                holdlogo = Image.open('holdingupg.png')
                            elif dg >0:
                                holdlogo = Image.open('holdingdg.png')
                            elif nft >0:
                                holdlogo = Image.open('holdingnft.png')
                            else:
                                holdlogo = Image.open('holding4.png')
                            holdlogo = holdlogo.resize((120, 120))
                            holdlogo = holdlogo.convert("RGBA")
                            background_image.paste(holdlogo, (510, 70), holdlogo)

                        if rarestatus > 0:
                            rare = Image.open("rare.png")
                            rare = rare.resize((100, 100))
                            rare = rare.convert("RGBA")
                            background_image.paste(rare, (80, 620), rare)

                        if projstatus > 0:
                            if rarestatus > 0:
                                proj = Image.open("proj.png")
                                proj = proj.resize((100, 100))
                                proj = proj.convert("RGBA")
                                background_image.paste(proj, (160, 620), proj)
                            else:
                                proj = Image.open("proj.png")
                                proj = proj.resize((100, 100))
                                proj = proj.convert("RGBA")
                                background_image.paste(proj, (80, 620), proj)

                        resize = background_image.resize((140, 180))

                        generated_images.append({
                            "image": resize.copy(),
                            "value": value
                        })

            generated_images = sorted(generated_images, key=lambda x: x["value"], reverse=True)

            col_number = 0
            row_number = 0

            embed = discord.Embed(title=f"Generating {username}'s inventory...", description="Pasting item cards...", color=0xffa200)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)

            inv_background = Image.open('futureinv2.png')
            inv_background = inv_background.convert("RGBA")

            first_row_item_count = 4
            total_rows = (len(generated_images) - first_row_item_count + 5 - 1) // 5
            items_in_last_row = (len(generated_images) - first_row_item_count) % 5

            print(items_in_last_row)

            for i, image_info in enumerate(generated_images):
                items_per_row = 5
                col_start_x = (col_number * 155) + 20
                row_start_y = (100 + row_number * 220) + 25

                if row_number == 0:
                    img = image_info["image"].copy()
                    img = img.resize((int(img.width * 1.2), int(img.height * 1.2)))
                    img.convert("RGBA")
                    items_per_row = 4
                    col_start_x = (col_number * 197) + 20
                else:
                    img = image_info["image"]
                    img.convert("RGBA")

                if row_number == 1:
                    row_start_y = (100 + row_number * 240) + 25

                if row_number == 2:
                    row_start_y = (100 + row_number * 220) + 25

                if row_number == 3:
                    row_start_y = (100 + row_number * 215) + 25

                inv_background.paste(img, (col_start_x, row_start_y), img)

                col_number += 1
                if col_number >= items_per_row:
                    col_number = 0
                    row_number += 1

            draw = ImageDraw.Draw(inv_background)
            custom_font = ImageFont.truetype("mainfont.otf", 40)

            total_value = format(total_value, ",")

            embed = discord.Embed(title=f"Generating {username}'s inventory...", description="<a:aurT:1166031422058934473> Finalizing...", color=0xffa200)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)

            text_color = "#616161"
            top_text = f"{username}"
            bottom_text = f"TOTAL VALUE: {total_value}"
            top_font = ImageFont.truetype("mainfont.otf", 40)
            bottom_font = ImageFont.truetype("mainfont.otf", 20)
            print("done")
            top_bbox = draw.textbbox((0, 0), top_text, font=top_font)
            top_text_width, top_text_height = top_bbox[2] - top_bbox[0], top_bbox[3] - top_bbox[1]
            text_x = 20
            print("texttop")

            draw.text((text_x, 20), top_text, fill=text_color, font=top_font)

            bottom_bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
            bottom_text_width, bottom_text_height = bottom_bbox[2] - bottom_bbox[0], bottom_bbox[3] - bottom_bbox[1]
            print("text bottom")

            draw.text((20, 65), bottom_text, fill=text_color, font=bottom_font)

            response = requests.get(bust)

            if response.status_code == 200:
                thumbnail_image = Image.open(BytesIO(response.content))
                thumbnail_image = thumbnail_image.resize((92, 92))
                thumbnail_image = thumbnail_image.convert("RGBA")

                thumbnail_x = max(text_x + top_text_width, 20 + bottom_text_width) + 25

                inv_background.paste(thumbnail_image, (thumbnail_x, 5), thumbnail_image)

            inv_background.save(f"main.png")
            print("upload")

            image_path = 'main.png'

            channel2 = client.get_channel(1245379184952606741)
            with open('main.png', 'rb') as f:
                message2 = await channel2.send(file=discord.File(f, 'main.png'))

            image_url = message2.attachments[0].url


            embed = discord.Embed(title=f"Generated {username}'s inventory below!", description=f"https://www.rolimons.com/player/{userid}", color=0xffa200)
            embed.set_thumbnail(url=bust)
            embed.set_footer(text="AUR Utilities - AUR.")
            embed.add_field(name="Username", value=f"{username}", inline=True)
            embed.add_field(name="Total Value", value=f"{total_value}", inline=True)
            embed.set_image(url=image_url)
            embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
            await message.edit(embed=embed)

    except asyncio.TimeoutError:
        embed = discord.Embed(title="❌ Timeout", description="The operation took too long to complete, please use a different user", color=0xff0004)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
        await message.edit(embed=embed)
        return

    except Exception as e:
        dtraceback = traceback.format_exc()
        print(dtraceback)
        embed = discord.Embed(title=f"❌Unknown error!", description=f"Message: {e}", color=0xff0004)
        embed.set_footer(text="AUR Utilities - AUR.")
        embed.set_author(name="AUR.", icon_url="https://cdn.discordapp.com/attachments/1085644383593955450/1143216056979169441/IMG_9715.png")
        await message.edit(embed=embed)
        return
      

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(
      activity=discord.Activity(
      type=discord.ActivityType.watching,
      name="AUR Utilities"
      )
    )
    print("ready")

bot_token = ''
client.run(bot_token)
