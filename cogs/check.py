from discord.ext import commands
from discord import app_commands
from cogs.module.anysf6 import *
from config import *
import discord, datetime, sqlite3, logging, traceback, config

class check(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @app_commands.command(name="check", description="查詢玩家指令")
    @discord.app_commands.describe(discordid = "請輸入你想查詢的DISCORD ID")
    @discord.app_commands.describe(cfnid = "請輸入你想查詢的CFN ID")
    @commands.guild_only()
    async def check(self, interaction: discord.Interaction, discordid: discord.Member = None, cfnid: int = None):
        try:
            await interaction.response.send_message(content=f"指令處理中, 請稍後......", ephemeral = True)
            print(rf'{config.bot_config().path}/data/sf6.db')
            conn = sqlite3.connect(rf'{config.bot_config().path}/data/sf6.db')
            c = conn.cursor()
            if discordid:
                cursor = c.execute(F"SELECT DISCORDID, CFNID, tag FROM userdata WHERE DISCORDID = '{discordid.id}'")
                userdata = cursor.fetchall()
                conn.close()
                if userdata:
                    result = Scaling(userdata[0][1]).run()
                    if type(result) is dict:
                        file = discord.File(rf"{config.bot_config().path}/image/character/{(result['角色名稱']).replace(' ', '')}.png")
                        embedVar = discord.Embed(title=f"查詢結果", description=f"", color=0xc800ff, timestamp=datetime.datetime.now())
                        embedVar.set_thumbnail(url=rf"attachment://{file.filename}")
                        for x, y in result.items():
                            if x == "玩家名稱" or x == "玩家ID":
                                embedVar.add_field(name=x, value=f"```{y}```", inline=True)
                            elif x == "排名" or x == "LP" or x == "MR":
                                embedVar.add_field(name=x, value=f"```{y}```", inline=True)
                            else:
                                embedVar.add_field(name=x, value=f"```{y}```", inline=False)
                        await interaction.followup.send(embed=embedVar, file=file, ephemeral=True)
                    else:
                        await interaction.edit_original_response(content=result)
                else:
                    await interaction.edit_original_response(content=f"找不到對方的CFN ID")
            elif cfnid:
                result = Scaling(cfnid).run()
                if type(result) is dict:
                    file = discord.File(rf"{config.bot_config().path}/image/character/{(result['角色名稱']).replace(' ', '')}.png")
                    embedVar = discord.Embed(title=f"查詢結果", description=f"", color=0xc800ff, timestamp=datetime.datetime.now())
                    embedVar.set_thumbnail(url=rf"attachment://{file.filename}")
                    for x, y in result.items():
                        if x == "玩家名稱" or x == "玩家ID":
                            embedVar.add_field(name=x, value=f"```{y}```", inline=True)
                        elif x == "排名" or x == "LP" or x == "MR":
                            embedVar.add_field(name=x, value=f"```{y}```", inline=True)
                        else:
                            embedVar.add_field(name=x, value=f"```{y}```", inline=False)
                    await interaction.followup.send(embed=embedVar, file=file, ephemeral=True)
                else:
                    await interaction.edit_original_response(content=f"找不到對方的CFN ID")
        except Exception as e:
            logging.error(traceback.print_exc())
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(check(client), guilds = [discord.Object(id = bot_config().GUILD_ID)])
