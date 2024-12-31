from discord.ext import commands
from discord import app_commands
from cogs.module.anysf6 import *
import discord, datetime, sqlite3, json, config

class register(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name="register", description="與你的CFN ID和DISCORD ID綁定")
    @discord.app_commands.describe(cfnid = "請輸入你的CFN ID, 可以在你的遊戲profile中找到")
    @discord.app_commands.describe(tag = "請輸入你的個人描述")
    @commands.guild_only()
    async def register(self, interaction: discord.Interaction, cfnid: int, tag: str = None):
        try:
            await interaction.response.send_message(content=f"指令處理中, 請稍後......", ephemeral = True)
            fetch = Scaling(cfnid).fetch_data()
            fetch = json.loads(fetch)
            if fetch["props"]["pageProps"]["common"]["statusCode"] != 200 and fetch["props"]["pageProps"]["fighter_banner_info"]["main_circle"]["leader"]["short_id"] == 0:
                await interaction.edit_original_response(content=f"找不到你提供的CFN ID")
            elif fetch["props"]["pageProps"]["common"]["statusCode"] == 200:
                conn = sqlite3.connect(rf'{config.bot_config().path}/data/sf6.db')
                c = conn.cursor()
                cursor = c.execute(F"SELECT DISCORDID, CFNID FROM userdata WHERE DISCORDID = '{interaction.user.id}'")
                result = cursor.fetchall()
                if result:
                    c.execute(f"UPDATE userdata set CFNID = '{cfnid}', tag = '{tag}' WHERE DISCORDID = '{interaction.user.id}'")
                    conn.commit()
                    file = discord.File(rf"{config.bot_config().path}/image/icon.jpg")
                    embedVar = discord.Embed(title="CFN ID綁定指令", description='', color=0xc800ff, timestamp=datetime.datetime.now())
                    embedVar.set_thumbnail(url=f"attachment://{file.filename}")
                    embedVar.add_field(name="Result", value=f"你的CFN已成功更新綁定!!! \n> 玩家ID: {cfnid} \n> 玩家名稱: {fetch['props']['pageProps']['fighter_banner_info']['personal_info']['fighter_id']} \n> 個人描述: {tag}", inline=True)
                else:
                    c.execute(f"INSERT INTO userdata (DISCORDID,CFNID,tag) VALUES ({interaction.user.id}, {cfnid}, '{tag}')")
                    conn.commit()
                    file = discord.File(rf"{config.bot_config().path}/image/icon.jpg")
                    embedVar = discord.Embed(title="CFN ID綁定指令", description='', color=0xc800ff, timestamp=datetime.datetime.now())
                    embedVar.set_thumbnail(url=f"attachment://{file.filename}")
                    embedVar.add_field(name="Result", value=f"你的CFN已成功綁定!!! \n> 玩家ID: {cfnid} \n> 玩家名稱: {fetch['props']['pageProps']['fighter_banner_info']['personal_info']['fighter_id']} \n> 個人描述: {tag}", inline=True)
                conn.close()
                await interaction.followup.send(embed=embedVar, file=file, ephemeral=True)
                try:
                    await interaction.delete_original_response()
                except discord.errors.HTTPException:
                    pass
        except Exception as e:
            await interaction.edit_original_response(content=f"An error occurred while fetching data: {e}")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(register(client), guilds = [discord.Object(id = bot_config().GUILD_ID)])
