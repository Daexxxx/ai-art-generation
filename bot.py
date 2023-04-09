from fileinput import filename
import discord
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image
import warnings
import os
import io
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import requests
from io import BytesIO

load_dotenv()

stability_api = client.StabilityInference(
    key=os.getenv('dreamstudio'),
    verbose=True,
)

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    description="Make art.",
    intents=intents,
)


@bot.command()
async def dream(ctx, *, prompt):
    """
    Generate Image With Stable Diffusion
    """
    msg = await ctx.send(f"“prompt: {prompt}”\n> Generating...")
    answers = stability_api.generate(prompt=prompt)
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
                msg = await ctx.send(
                    "You have triggered the filter, please try again")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                arr = io.BytesIO(artifact.binary)
                img.save(arr, format='PNG')
                arr.seek(0)
                file = discord.File(arr, filename='art.png')
                await msg.edit(content=f"“prompt: {prompt}” \n")
                await ctx.send(file=file)

## This command will generate AI art for a specific dimension. I chose 738 x 251 for my purposes
@bot.command()
async def load(ctx, *, prompt):
    msg = await ctx.send(f"“{prompt}”\n> Generating...")
    answers = stability_api.generate(prompt=prompt, width=512, height= 512)
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
                msg = await ctx.send(
                    "You have triggered the filter, please try again")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                arr = io.BytesIO(artifact.binary)
                img.save(arr, format='PNG')
                arr.seek(0)
                file = discord.File(arr, filename='art.png')
                await msg.edit(content=f"“{prompt}” \n")
                await ctx.send(file=file)

@bot.command()
async def listcommands(ctx):
    """
    Displays all the available commands.
    """
    embed = discord.Embed(title="List of commands:", description="", color=discord.Color.blue())

    for command in bot.commands:
        if command.name not in ['load', 'help', 'listcommands']:
            embed.add_field(name=f"!{command.name}", value=command.help or "No description available.", inline=False)

    await ctx.send(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))
