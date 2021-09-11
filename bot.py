#!/usr/bin/python

# bot.py
import os
from dotenv import load_dotenv

# mal api
from mal import *
#json
import json

# discord
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!',intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='ping',help='Sendet einen Ping')
    async def ping(ctx,s: str):
        ctx.send('pong')

bot.run(TOKEN)
