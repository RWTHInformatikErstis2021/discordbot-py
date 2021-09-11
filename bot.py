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

@bot.command(name='search',help='Ausgabe von _n_ Suchergebnissen zu Anime _m_ per Namen im Server-Chat')
async def search(ctx, c: str, s: str):
    try:
        c = int(c)
    except ValueError:
        ctx.send("Fehler: `Syntaxfehler`\n\nBitte Benutze den Command folgendermaßen: !search <Anzahl der Elemente> <Name>'")
    try:
        s = AnimeSearch(s)
        for i in range(c):
            await ctx.send(f'{i+1}. {s.results[i].title} [{s.results[i].mal_id}]')
    except Exception:
        await ctx.send('Fehler: `invalide Animesuche` (Name des Animes muss >3 Zeichen sein) oder Syntaxfehler\n\nBitte Benutze den Command folgendermaßen: !search <Anzahl der Elemente> <Name>')
        return
    await ctx.send("Benutze \"!info <id>\" um Informationen zu einem Anime auszugeben")

@bot.command(name='sp',help='Ausgabe von _n_ Suchergebnissen zu Anime _m_ per Namen im Privatchat')
async def sp(ctx, c: str, s: str):
    try:
        c = int(c)
    except ValueError:
        ctx.send("Fehler: `Syntaxfehler`\n\nBitte Benutze den Command folgendermaßen: !search <Anzahl der Elemente> <Name>'")
    try:
        s = AnimeSearch(s)
        for i in range(c):
            await ctx.author.send(f'{i+1}. {s.results[i].title} [{s.results[i].mal_id}]')
    except Exception:
        await ctx.author.send('Fehler: `invalide Animesuche` (Name des Animes muss >3 Zeichen sein) oder Syntaxfehler\n\nBitte Benutze den Command folgendermaßen: !search <Anzahl der Elemente> <Name>')
        return
    await ctx.author.send("Benutze \"!info <id>\" um Informationen zu einem Anime auszugeben")

@bot.command(name='info',help='Ausgabe von Informationen zu Anime per Anime-id')
async def info(ctx, id: int):
    a = Anime(id)
    embed = discord.Embed(title=a.title, colour=discord.Colour(0x3e038c))
    embed.add_field(name=f"Score:", value=str(a.score)+'/10', inline=False)
    embed.add_field(name=f"Members:", value=str(a.members), inline=False)
    embed.add_field(name=f"Episode Count:", value=str(a.episodes), inline=False)
    embed.add_field(name=f"Rank:", value='#'+str(a.rank), inline=False)
    embed.add_field(name=f"Source:", value=a.source, inline=False)
    embed.add_field(name=f"Aired:", value=a.aired, inline=False)
    embed.add_field(name=f"Genres:", value=", ".join(a.genres), inline=False)
    if not a.opening_themes==[]:
        embed.add_field(name=f"Opening Themes:", value=", ".join(a.opening_themes), inline=False)
    embed.add_field(name=f"Link", value='https://myanimelist.net/anime/'+str(a.mal_id), inline=False)
    await ctx.send(embed=embed)

@bot.command(name='op',help='Ausgabe von Groovy-Commands eines Openings eine Animes per Anime-id')
async def op(ctx,id: int,num: int):
    a = Anime(id)
    await ctx.send('Copy the following command for Groovy to play the Opening Theme: ')
    embed = discord.Embed(title='-p '+a.opening_themes[num-1], colour=discord.Colour(0x3e038c))
    await ctx.send(embed=embed)

# Join watchparty via id
@bot.command(name='watch',help='Füge dich zu einer Watchparty eines Animes per Anime-id hinzu')
async def watch(ctx,id: str):
    with open("userconfig.json",'r+') as f:
        j = json.load(f)
        # old = j[str(id)]
        try:
            if not ctx.author.id in j[str(id)]:
                j[str(id)].append(ctx.author.id)
            else:
                await ctx.send("Fehler: Gruppe bereits beigetreten")
                return
        except KeyError:
            j[str(id)] = [ctx.author.id]
        f.seek(0)
        json.dump(j,f)
    # Frontend message
    a = Anime(id)
    await ctx.send(f"Du bist erfolgreich der Watchparty für `{a.title}` beigetreten.")

# Leave watchparty via id
@bot.command(name='leave',help='Entferne dich aus einer Watchparty eines Animes per Anime-id')
async def leave(ctx,id: str):
    with open("userconfig.json",'r+') as f:
        j = json.load(f)
        try:
            if ctx.author.id in j[str(id)]:
                j[str(id)].remove(ctx.author.id)
            else:
                await ctx.send("Fehler: kein Mitglied der Watchparty")
                return
        except KeyError:
            j[str(id)] = [ctx.author.id]
        f.seek(0)
        json.dump(j,f)
    # Frontend message
    a = Anime(id)
    await ctx.send(f"Du hast die Watchparty für `{a.title}` verlassen.")

# Join Watchparty via AnimeSearch
@bot.command(name='ws',help='Füge dich zu einer Watchparty eines Animes per Anime-Suche hinzu')
async def ws(ctx,s: str):
    ans = ""
    try:
        s = AnimeSearch(s)
        for i in range(10):
            await ctx.author.send(f'{i+1}. {s.results[i].title} [{s.results[i].mal_id}]')
        def check(m):
            return m.channel == ctx.author.dm_channel
        ans = await bot.wait_for("message", check=check)
        id = s.results[int(ans.content)-1].mal_id
        with open("userconfig.json",'r+') as f:
            
            j = json.load(f)
            try:
                if not ctx.author.id in j[str(id)]:
                    j[str(id)].append(ctx.author.id)
                else:
                    await ctx.author.send("Fehler: Gruppe bereits beigetreten")
                    return
            except KeyError:
                j[str(id)] = [ctx.author.id]
            f.seek(0)
            json.dump(j,f)
            # Frontend message
        a = Anime(id)
        await ctx.send(f"Du bist erfolgreich der Watchparty für `{a.title}` beigetreten.")
    except Exception:
        await ctx.send("Fehler: `invalide Animesuche` (Name des Animes muss >3 Zeichen sein)")

# Leave Watchparty via AnimeSearch
@bot.command(name='ls',help='Entferne dich aus einer Watchparty eines Animes per Anime-Suche')
async def ls(ctx,s: str):
    ans = ""
    try:
        s = AnimeSearch(s)
        for i in range(10):
            await ctx.author.send(f'{i+1}. {s.results[i].title} [{s.results[i].mal_id}]')
        def check(m):
            return m.channel == ctx.author.dm_channel
        ans = await bot.wait_for("message", check=check)
        id = s.results[int(ans.content)-1].mal_id
        with open("userconfig.json",'r+') as f:
            
            j = json.load(f)
            try:
                if not ctx.author.id in j[str(id)]:
                    j[str(id)].append(ctx.author.id)
                else:
                    await ctx.author.send("Fehler: kein Mitglied der Watchparty")
                    return
            except KeyError:
                j[str(id)] = [ctx.author.id]
            f.seek(0)
            json.dump(j,f)
            # Frontend message
        a = Anime(id)
        await ctx.send(f"Du bist die Watchparty für `{a.title}` verlassen.")
    except Exception:
        await ctx.send("Fehler: `invalide Animesuche` (Name des Animes muss >3 Zeichen sein)")

# Ping Watchparty
@bot.command(name='p',help='Pingt die Mitglieder einer Watchparty per Anime-id an')
async def ping(ctx,id: int):
    with open("userconfig.json",'r') as f:
        j = json.load(f)
        if str(id) in j:
            message = f"Lust auf `{Anime(id).title}`?"      
            for n in j[str(id)]:
                user = bot.get_user(n)
                message += "\n"+user.mention
            await ctx.send(message)
        else:
            await ctx.send(f"{Anime(id).title} hat noch keine Mitglieder!")

# Ping Search
@bot.command(name='ps',help='Pingt die Mitglieder einer Watchparty per Anime-Suche an')
async def ps(ctx,s: str):
    try:
        ans = ""
        s = AnimeSearch(s)
        for i in range(10):
            await ctx.author.send(f'{i+1}. {s.results[i].title} [{s.results[i].mal_id}]')
        def check(m):
            return m.channel == ctx.author.dm_channel
        ans = await bot.wait_for("message", check=check)
        id = s.results[int(ans.content)-1].mal_id
        with open("userconfig.json",'r') as f:
            j = json.load(f)
            if str(id) in j:
                message = f"Lust auf `{Anime(id).title}`?"      
                for n in j[str(id)]:
                    user = bot.get_user(n)
                    message += "\n"+user.mention
                await ctx.send(message)
            else:
                await ctx.send(f"{Anime(id).title} hat noch keine Mitglieder!")
    except Exception:
        await ctx.send("Fehler: `invalide Animesuche` (Name des Animes muss >3 Zeichen sein)")

# List Members of Watchparty as Embed
@bot.command(name='list',help='Listet die Mitglieder einer Watchparty auf')
async def list(ctx,id: int):
    with open("userconfig.json",'r') as f:
        j = json.load(f)
        if str(id) in j:
            embed = discord.Embed(title=Anime(id).title, colour=discord.Colour(0x81c542))
            for i in range(len(j[str(id)])):
                user = bot.get_user(j[str(id)][i])
                embed.add_field(name=f"{i+1}.", value=str(user.name), inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{Anime(id).title} hat noch keine Mitglieder!")

@bot.command(name='clear',help='Alle Nachrichten des Bots und Commands an den Bot im aktuellen Textchannel löschen')
async def clear(ctx,n: int = 100):
    async for message in ctx.channel.history(limit=n):
        if message.author == bot.user:
            await message.delete()
        elif message.content.startswith("!") or message.content.startswith("~"):
            await message.delete()
bot.run(TOKEN)