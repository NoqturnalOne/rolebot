import json
import discord
from discord.ext import commands

info = {}
messages = []
config_file_name = 'config.json'
bot = commands.Bot(command_prefix='`')

def load_info():
    global info
    with open(config_file_name, 'r') as f:
        info = json.load(f)

def save_info():
    global info
    with open(config_file_name, 'w') as f:
        json.dump(info, f, indent=2)

async def get_roles(msg, emoji):
    global info
    server = msg.server
    choices = info.get('choices', [])
    roles = [c['role'] for c in choices if c['emoji'] == emoji.name]
    roles = [role for role in server.roles if role.name in roles]
    return roles
    
@bot.event
async def on_ready():
    print(bot.user.name, 'is ready')

@bot.command(pass_context=True)
async def reload(ctx):
    global info
    load_info()

@bot.command(pass_context=True)
async def roles(ctx):
    global info
    server = ctx.message.server
    if not server: return
    choices = [c['role'] for c in info.get('choices', [])]
    roles = [role for role in server.roles if role.name in choices]
    roles = '\n'.join(str(role) for role in roles)
    await bot.say(roles)

@bot.command(pass_context=True)
async def emojis(ctx):
    server = ctx.message.server
    if not ctx.message.server: return
    choices = [c['emoji'] for c in info.get('choices', [])]
    emojis = ''.join(str(e) for e in server.emojis if e.name in choices)
    await bot.say(emojis)

@bot.command(pass_context=True)
async def react(ctx):
    global info
    global messages
    choices = info.get('choices', [])
    if len(choices) == 0:
        return await bot.say('No choices setup')
    msg = await bot.say('React to this message to add/remove roles')
    messages.append(msg.id)
    choices = [c['emoji'] for c in choices]
    emojis = [e for e in ctx.message.server.emojis if e.name in choices]
    for emoji in emojis:
        await bot.add_reaction(msg, emoji)
    await bot.delete_message(ctx.message)

@bot.event
async def on_reaction_add(reaction, user):
    global messages
    if user.bot: return
    if reaction.message.id not in messages: return
    roles = await get_roles(reaction.message, reaction.emoji)
    await bot.add_roles(user, *roles)

@bot.event
async def on_reaction_remove(reaction, user):
    global messages
    if user.bot: return
    if reaction.message.id not in messages: return
    roles = await get_roles(reaction.message, reaction.emoji)
    await bot.remove_roles(user, *roles)

load_info()
bot.run(info['token'])
