from discord.ext import commands
from discord import app_commands
from cogs.module.anysf6 import *
from config import *
import discord, datetime, sqlite3, config

async def fetch_challenger_data(content, user_id):
    conn = sqlite3.connect(rf'{config.bot_config().path}/data/sf6.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT DISCORDID, CFNID, tag FROM userdata WHERE {'DISCORDID' if user_id else 'CFNID'} = '{content}'")
    challenger = cursor.fetchall()
    conn.close()
    return challenger

async def get_embed(userdata, user, content):
    if not userdata[0][2] or userdata[0][2] == "None":
        return discord.Embed(title=f"{user} {content}!!!", description=f"記住打街霸唔好嬲, 輸贏只係過程一點", color=0xc800ff, timestamp=datetime.datetime.now())
    else:
        return discord.Embed(title=f"{user} {content}!!!", description=userdata[0][2], color=0xc800ff, timestamp=datetime.datetime.now())

async def add_embed(embedVar, file, user, avatar, result):
    embedVar.set_thumbnail(url=rf"attachment://{file.filename}")
    embedVar.set_author(name=f'{user}', icon_url=f'{avatar}')
    for x, y in result.items():
        if x == "玩家名稱" or x == "玩家ID":
            embedVar.add_field(name=x, value=f"```{y}```", inline=True)
        elif x == "排名" or x == "LP" or x == "MR":
            embedVar.add_field(name=x, value=f"```{y}```", inline=True)
        else:
            embedVar.add_field(name=x, value=f"```{y}```", inline=False)
    return embedVar

async def process(interaction, challenger, status, text):
    await interaction.response.send_message(content=f"指令處理中, 請稍後......", ephemeral = True)
    challenger = await fetch_challenger_data(challenger, status)
    channel = await interaction.client.fetch_channel(bot_config().anysf6_channel_id)
    user = await interaction.client.fetch_user(challenger[0][0])
    await channel.send(f"{interaction.user.name}話: {user.name} {text}")

class comment(discord.ui.View):
    def __init__(self, content):
        super().__init__(timeout=None)
        self.content = content

    @discord.ui.button(label="👍 Good Game", style=discord.ButtonStyle.green)
    async def goodgame(self, interaction: discord.Interaction, Button: discord.ui.Button):
        try:
            await process(interaction, self.content, True, "Good Game 👍")
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

    @discord.ui.button(label="🖕 屌9佢", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, Button: discord.ui.Button):
        try:
            await process(interaction, self.content, True, "我唔撚同你打呀, 屌你老母 🖕")
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

class vs_accept(discord.ui.View):
    def __init__(self, content):
        super().__init__(timeout=None)
        self.content = content

    @discord.ui.button(label="🥊接受對戰", style=discord.ButtonStyle.blurple)
    async def accept(self, interaction: discord.Interaction, Button: discord.ui.Button):
        try:
            await interaction.response.send_message(content=f"指令處理中, 請稍後......", ephemeral = True)
            userdata = await fetch_challenger_data(interaction.user.id, True)
            challenger = await fetch_challenger_data(self.content, False)
            if userdata:
                if interaction.user.avatar:
                    avatar = interaction.user.avatar.url
                else:
                    avatar = interaction.user.default_avatar.url
                result = Scaling(userdata[0][1]).run()
                file = discord.File(rf"{config.bot_config().path}/image/character/{(result['角色名稱']).replace(' ', '')}.png")
                embedVar = await get_embed(userdata, interaction.user.name, '接受對戰')
                embedVar = await add_embed(embedVar, file, interaction.user.name, avatar, result)
                channel = await interaction.client.fetch_channel(bot_config().anysf6_channel_id)
                view = comment(interaction.user.id)
                message = await channel.send(f"<@{challenger[0][0]}>", embed=embedVar, file=file, view=view)
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

    @discord.ui.button(label="👍 Good Game", style=discord.ButtonStyle.green)
    async def goodgame(self, interaction: discord.Interaction, Button: discord.ui.Button):
        try:
            await process(interaction, self.content, False, "Good Game 👍")
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

    @discord.ui.button(label="🖕 屌9佢", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, Button: discord.ui.Button):
        try:
            await process(interaction, self.content, False, "我唔撚同你打呀, 屌你老母 🖕")
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

class anysf6(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name="anysf6", description="約戰指令")
    @commands.guild_only()
    async def anysf6(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(content=f"指令處理中, 請稍後......", ephemeral = True)
            userdata = await fetch_challenger_data(interaction.user.id, True)
            if userdata:
                if interaction.user.avatar:
                    avatar = interaction.user.avatar.url
                else:
                    avatar = interaction.user.default_avatar.url
                result = Scaling(userdata[0][1]).run()
                if type(result) is dict:
                    file = discord.File(rf"{config.bot_config().path}/image/character/{(result['角色名稱']).replace(' ', '')}.png")
                    embedVar = await get_embed(userdata, interaction.user.name, '申請對戰')
                    embedVar = await add_embed(embedVar, file, interaction.user.name, avatar, result)
                    channel = await interaction.client.fetch_channel(bot_config().anysf6_channel_id)
                    await interaction.edit_original_response(content=f"你的對戰申請已成功傳送到<#{bot_config().anysf6_channel_id}>")
                    view = vs_accept(result["玩家ID"])
                    await channel.send("@here", embed=embedVar, file=file, view=view)
                else:
                    await interaction.edit_original_response(content=result)
            else:
                await interaction.edit_original_response(content=f"找不到你的CFN ID, 請先用/register command")
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(anysf6(client), guilds = [discord.Object(id = bot_config().GUILD_ID)])
