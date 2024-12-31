import discord, logging, os
from discord.ext import commands, tasks
from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f'{bot_config().path}/log/SF6BOT.log'),
        logging.StreamHandler()
    ]
)

class SF6(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="?", intents=discord.Intents.all(), application_id = bot_config().APPLICATION_ID)

    async def setup_hook(self):
        await self.load_extension(f"cogs.anysf6")
        await self.load_extension(f"cogs.register")
        await self.load_extension(f"cogs.check")
        await client.tree.sync(guild = discord.Object(id = bot_config().GUILD_ID))

    async def on_ready(self):
        print("Success: SF6 Bot is connected to Discord")

    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            command_name = interaction.command.name
            user = interaction.user
            args = interaction.data.get("options", [])
            args_str = ', '.join(f"{arg['name']}: {arg['value']}" for arg in args) if args else "No arguments"
            logging.info(f"[Command Log] {user} used command: | {command_name} {args_str}")

client = SF6()
client.run(bot_config().TOKEN)
