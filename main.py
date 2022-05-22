from hashlib import new
from importlib.resources import contents
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord.ext.commands import CommandNotFound
import os
import validators
import json
import datetime
import threading
import asyncio
import math
import pandas as pd
from collections import defaultdict
from typing import Union
from cryptography.fernet import Fernet
import urllib
from urllib.error import HTTPError
import re
from validators.url import url
from youtube_dl import YoutubeDL
from bs4 import BeautifulSoup as bs
import socket
import requests
import plotly.express as px
from difflib import SequenceMatcher
from copy import deepcopy

intents = discord.Intents.default()
intents.presences = True
intents.members = True
snoo = commands.Bot(command_prefix=['!s ', 'hey snoo, ', 'hey snoo ', 'snoo, ', 'snoo ', 'Hey snoo, ', 'Hey snoo ', 'Snoo, ', 'Snoo ', 'Hey Snoo, ', 'Hey Snoo ', 'hey snoo, ', 'hey snoo '], intents=intents)

# _________________________________________________________________ DATA _________________________________________________________________

profile_data = defaultdict(dict)
#user_karma = defaultdict(dict)
#user_friendship = defaultdict(dict)
channel_messages = defaultdict(dict)
#user_messages = defaultdict(dict)
#users_in_vc = {}
#user_vc_time = defaultdict(dict)
#top_songs = defaultdict(dict)
song_history = defaultdict(dict)
user_candy = defaultdict(dict)
server_config = defaultdict(dict)
#server_awards = defaultdict(dict)
#user_awards = defaultdict(dict)

# _________________________________________________________________ GLOBAL VARS _________________________________________________________________

admin_command_message = "You need to be my master to use this command!"
snoo_color = 0xe0917a
version = "0.4.30 (facebook level data collection)"
default_settings = {"classic nowplaying bar": False}
loading_icon = "<a:loading:977336498322030612>"

poll_icon = "https://media.discordapp.net/attachments/908157040155832350/930606118512779364/poll.png"
music_icon = "https://cdn.discordapp.com/attachments/908157040155832350/930609037807087616/snoo_music_icon.png"
profile_icon = "https://media.discordapp.net/attachments/908157040155832350/931732724203520000/profile.png"
award_icon = "https://cdn.discordapp.com/attachments/908157040155832350/958841770765066280/award_icon.png"

@snoo.event
async def on_ready():
	print(f'We have logged in as {snoo.user}')
	
	await snoo.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with my master's sanity"))
	channel = snoo.get_channel(865007153109663765)

	await initialize_data()
	asyncio.create_task(async_timer(60 * 6, new_save))
	await channel.send(f"Running version: {version} on {socket.gethostname()}")
	
async def initialize_data():
	if (not os.path.isdir('Data Files')):
		os.makedirs("Data Files")

	data_channel = snoo.get_channel(977316868253708359)
	async for message in data_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/profile.json")
	f = open('Data Files/profile.json')
	str_profile = json.load(f)

	messages_channel = snoo.get_channel(913524223870398534)
	async for message in messages_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/channel_messages.json")
	f = open('Data Files/channel_messages.json')
	str_messages = json.load(f)

	history_channel = snoo.get_channel(922592622248341505)
	async for message in history_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/song_history.json")
	f = open('Data Files/song_history.json')
	str_history = json.load(f)

	"""server_awards_channel = snoo.get_channel(959590449952194621)
	async for message in server_awards_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/server_awards.json")

	f = open('Data Files/server_awards.json')

	str_server_awards = json.load(f)

	user_awards_channel = snoo.get_channel(959590569137541170)
	async for message in user_awards_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/user_awards.json")

	f = open('Data Files/user_awards.json')

	str_user_awards = json.load(f)"""

	#convert dictionarys to int:
	for guild in str_profile:
		for user in str_profile[guild]:
			profile_data[int(guild)][int(user)] = str_profile[guild][user]

	for key in str_messages:
		for new_key in str_messages[key]:
			channel_messages[int(key)][int(new_key)] = str_messages[key][new_key]

	for guild in (str_history):
		song_history[int(guild)] = str_history[guild]

	"""for key in str_server_awards:
			server_awards[int(key)] = str_server_awards[key]

	for key in str_user_awards:
		for new_key in str_user_awards[key]:
			user_awards[int(key)][int(new_key)] = str_user_awards[key][new_key]"""

@snoo.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

# _________________________________________________________________ ON MESSAGE _________________________________________________________________

@snoo.event
async def on_message(message):
	if (message.guild.id not in channel_messages) or (message.channel.id not in channel_messages[message.guild.id]):
		channel_messages[message.guild.id][message.channel.id] = [1]
	else:
		channel_messages[message.guild.id][message.channel.id][len(channel_messages[message.guild.id][message.channel.id]) - 1] += 1

	#if (message.guild.id not in user_messages) or (message.author.id not in user_messages[message.guild.id]):
	#	user_messages[message.guild.id][message.author.id] = [1]
	verify_data(message.guild.id, message.author.id)
	#else:
	profile_data[message.guild.id][message.author.id]["messages"][-1] += 1
	
	#print(channel_messages)

	if (message.author == snoo.user):
		return

	if (message.attachments or validators.url(message.content) or '*image*' in message.content.lower()):
		upvote = None
		downvote = None

		for emoji in message.channel.guild.emojis:
			if (emoji.name == "Upvote"):
				upvote = emoji
			if (emoji.name == "Downvote"):
				downvote = emoji
			if (upvote != None and downvote != None):
				break

		if (upvote == None):
			await message.add_reaction("<:Upvote:919356607563972628>")
		else:
			await message.add_reaction(upvote)

		if (downvote == None):
			await message.add_reaction("<:Downvote:919357445770473503>")
		else:
			await message.add_reaction(downvote)

	if (message.content.lower().startswith('%')):
		if ('scale' in message.content.lower()):
			await message.add_reaction("1️⃣")
			await message.add_reaction("2️⃣")
			await message.add_reaction("3️⃣")
			await message.add_reaction("4️⃣")
			await message.add_reaction("5️⃣")
			await message.add_reaction("6️⃣")
			await message.add_reaction("7️⃣")
			await message.add_reaction("8️⃣")
			await message.add_reaction("9️⃣")
			await message.add_reaction("🔟")
		else:	
			await message.add_reaction("<:cross:905498493840400475>")
			await message.add_reaction("<:check:905498494222098543>")
	
	#replys:
	if (not message.content.lower().startswith("snoo")):
		if (message.content.lower().startswith('hi snoo')):
			await message.channel.send('Hi!')

		if (message.content.lower().startswith('bye snoo')):
			await message.channel.send('Cya!')

		if ('_pat' in message.content.lower() or 'pat' == message.content.lower() or '*pat*' == message.content.lower()):
			await message.channel.send('.(≧◡≦).')

		if ('thanks snoo' in message.content.lower() or 'thank you snoo' in message.content.lower() or 'ty snoo' in message.content.lower() or 'thx snoo' in message.content.lower()):
			await message.channel.send('np!')

		if ('love' in message.content.lower() and 'snoo' in message.content.lower()):
			await message.channel.send("I love you too! :)")

		if ('hate' in message.content.lower() and 'snoo' in message.content.lower()):
			await message.channel.send('Sorry to hear. :(')

		if ('sus' in message.content.lower() or 'amogus' in message.content.lower() or 'amongus' in message.content.lower()):
			await message.add_reaction("<:Koneko_Cringe:858704751432302612>")

		if ('among' in message.content.lower() and 'us' in message.content.lower()):
			await message.add_reaction("<:Koneko_Cringe:858704751432302612>")

	mention = f'<@!{snoo.user.id}>'
	if (mention in message.content and not 'karma' in message.content.lower()):
		await message.channel.send("Pimg")

	#commands
	await snoo.process_commands(message)

#upvote adding and taking away
@snoo.event
async def on_reaction_add(reaction, user) :
	if (user == snoo.user or user == reaction.message.author):
		return
	if (type(reaction.emoji) == str):
		return

	if (reaction.emoji.name == "Upvote") :
		verify_data(reaction.message.guild.id, reaction.message.author.id)
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] += 1

		verify_data(reaction.message.guild.id, user.id)
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] += 1

		if (reaction.message.author.id not in user_candy):
			user_candy[reaction.message.author.id] = 5
		else:
			user_candy[reaction.message.author.id] += 5

		if (user.id not in user_candy):
			user_candy[user.id] = 2
		else:
			user_candy[user.id] += 2

		"""if (reaction.message.reference is not None):
			msg = await reaction.message.channel.fetch_message(reaction.message.reference.message_id)
			if (msg.author != user):
				user_karma[reaction.message.channel.guild.id][msg.author.id][len(user_karma[reaction.message.channel.guild.id][msg.author.id]) - 1] += 1"""

	elif (reaction.emoji.name == "Downvote"):
		verify_data(reaction.message.guild.id, reaction.message.author.id)
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] -= 1

		verify_data(reaction.message.guild.id, user.id)
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] -= 1

		if (reaction.message.author.id not in user_candy):
			user_candy[reaction.message.author.id] = -3
		else:
			user_candy[reaction.message.author.id] -= 3

		if (user.id not in user_candy):
			user_candy[user.id] = -2
		else:
			user_candy[user.id] -= 2

@snoo.event
async def on_reaction_remove(reaction, user):
	if (user == snoo.user or user == reaction.message.author):
		return
	if (type(reaction.emoji) == str):
		return

	if (reaction.emoji.name == "Upvote"):
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] -= 1
		#user_friendship[user.id] -= 1
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] -= 1

		user_candy[reaction.message.author.id] -= 3
		user_candy[user.id] -= 1

		"""if (reaction.message.reference is not None):
			msg = await reaction.message.channel.fetch_message(reaction.message.reference.message_id)
			if (msg.author != user):
				user_karma[reaction.message.channel.guild.id][msg.author.id][len(user_karma[reaction.message.channel.guild.id][msg.author.id]) - 1] -= 1"""

	if (reaction.emoji.name == "Downvote"):
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] += 1
		#user_friendship[user.id] += 1
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] += 1

		user_candy[reaction.message.author.id] += 2
		user_candy[user.id] += 2

"""@snoo.event
async def on_voice_state_update(member, before, after):
	if (not before.channel and after.channel):
		#print(f'{member} has joined vc')
		if (after.channel.guild.id not in users_in_vc):
			users_in_vc[after.channel.guild.id] = []
		if (member.id not in users_in_vc[after.channel.guild.id]):
			users_in_vc[after.channel.guild.id].append(member.id)
	elif (before.channel and not after.channel):
		#print(f'{member} has left vc')
		users_in_vc[before.channel.guild.id].remove(member.id)"""

# _________________________________________________________________ UTILITY _________________________________________________________________

@snoo.command()
async def config(ctx, *, setting):
	verify_settings(ctx.guild.id)

	if (setting == "classic nowplaying bar"):
		if (server_config[ctx.guild.id]["classic nowplaying bar"]):
			server_config[ctx.guild.id]["classic nowplaying bar"] = False
		else:
			server_config[ctx.guild.id]["classic nowplaying bar"] = True
		await ctx.send("👍")

@snoo.command()
async def yt_mp3(ctx, url, *, name = "video"):
	if (validators.url(url) and "youtu" in url):
		ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192',}], 'outtmpl': name + ".mp3",}
		with YoutubeDL(ydl_opts) as ydl:
			msg = await ctx.send(f"Downloading <a:Loading:908094681504706570>")

			ydl.download([url])

			await msg.delete()
			await ctx.send(file=discord.File(name + '.mp3'))
			os.remove(name + ".mp3")
	else:
		await ctx.send("That's not a youtube url!")

"""@snoo.command()
async def yt_mp4(ctx, *, url):
	if (validators.url(url) and "youtu" in url):
		ydl_opts = {'format': 'mp4', 'outtmpl': "video.mp4",}
		with YoutubeDL(ydl_opts) as ydl:
			msg = await ctx.send(f"Downloading <a:Loading:908094681504706570>")

			ydl.download([url])

			await msg.delete()
			await ctx.send(file=discord.File('video.mp4'))
			os.remove("video.mp4")
	else:
		await ctx.send("That's not a youtube url!")"""

@snoo.command()
async def poll(ctx, name, *, opts):
	emojis = ["<:A_:908477372397920316>", "<:B_:908477372637011968>", "<:C_:908477373090000916>", "<:D_:908477372607639572>", "<:E_:908477372561506324>", "<:F_:908477372511170620>", "<:G_:908477372829949952>"]
	opts_list = opts.split(',')
	

	embed = discord.Embed(title = name, colour = snoo_color)
	embed.set_author(name = "||  POLL", icon_url = poll_icon)

	for i in range(len(opts_list)):
		embed.add_field(name = f"Option  {emojis[i]}", value = opts_list[i], inline=False)

	poll = await ctx.send(embed=embed)

	for i in range(len(opts_list)):
		await poll.add_reaction(emojis[i])

@snoo.command()
async def purge(ctx, amount = 0, embed = False, user: discord.User = 123):
	if (ctx.message.author.id == 401442600931950592):
		message_number = 1

		async for message in ctx.message.channel.history (limit = 10000) :
			if (message_number > 1) :
				if (embed == False and user == 123) :
					await message.delete()
					message_number += 1
				if (embed == True) :
					if (user == 123) :
						if (message.attachments or validators.url(message.content)) :
							await message.delete()
							message_number += 1
					else :
						if ((message.attachments or validators.url(message.content)) and message.author == user) :
							await message.delete()
							message_number += 1
				elif (embed == False and user != 123) :
					if (message.author == user) :
						await message.delete()
						message_number += 1
			else :
				message_number += 1
			if (message_number == amount) :
				break
		
		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)

@snoo.command()
async def user(ctx, *, user: discord.User):
	username = await snoo.fetch_user(user.id)
	await ctx.send(username)

@snoo.command()
async def say(ctx, *, args):
	if (ctx.message.author.id == 401442600931950592):
		await ctx.message.delete()
		await ctx.send(args)

#display information
@snoo.command()
async def profile(ctx, *, user: discord.User = 123):
	if (user == 123):
		user_id = ctx.message.author.id
	else:
		user_id = user.id

	user = await snoo.fetch_user(user_id)
	split_user = str(user).split("#", 1)
	username = split_user[0]

	verify_data(ctx.guild.id, user_id)

	embed = discord.Embed(colour=snoo_color)

	embed.set_author(name = f"||  {username.upper()}'S PROFILE", icon_url = profile_icon)

	embed.add_field(name = "Karma:", value = f"earned **{sum(profile_data[ctx.guild.id][user_id]['karma'])}** upvotes", inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = "Friendship:", value = f"given out **{sum(profile_data[ctx.guild.id][user_id]['friendship'])}** karma to others", inline = True)
	embed.add_field(name = "Messages:", value = f"sent **{sum(profile_data[ctx.guild.id][user_id]['messages'])}** messages", inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = "VC hours:", value = f"spent **{math.fsum(profile_data[ctx.guild.id][user_id]['vc_time'])}** hours in vc", inline = True)
	
	await ctx.send(embed=embed)

@snoo.command()
async def candy(ctx, *, user: discord.User = 123):
	if (user == 123):
		user_id = ctx.message.author.id
	else:
		user_id = user.id

	user = await snoo.fetch_user(user_id)
	split_user = str(user).split("#", 1)
	username = split_user[0]

	if (user_id not in user_candy):
		user_candy[user_id] = 0

	embed = discord.Embed(colour=snoo_color)
	embed.set_author(name = f"||  {username.upper()}'S CANDY", icon_url = profile_icon)

	embed.add_field(name = "Candy:", value = f"currently has **{user_candy[user_id]}**<:candy:932697618843336724>", inline = True)

	await ctx.send(embed = embed)

"""@snoo.command()
async def award(ctx, command = "none", arg1: Union[str, discord.User] = "none", arg2: Union[str, discord.User] = "none", arg3 = "none"):
	if (command == "create"):
		server_awards[ctx.guild.id][arg1] = {"desc": arg2 , "image_link": arg3}

		embed = discord.Embed(title = arg1, description = server_awards[ctx.guild.id][arg1]["desc"], color = snoo_color)
		embed.set_author(name = f"||  AWARD", icon_url = award_icon)
		if (validators.url(server_awards[ctx.guild.id][arg1]["image_link"])):
			embed.set_image(url = server_awards[ctx.guild.id][arg1]["image_link"])

		await ctx.send("Got it! Here's what it looks like:", embed = embed)

	elif (command == "give"):
		arg2 = re.search('!(.*)>', arg2).group(1)
		user = await snoo.fetch_user(arg2)
		split_user = str(user).split("#", 1)
		username = split_user[0]
		arg2 = int(arg2)

		if (arg1 in server_awards[ctx.guild.id]):
			if (ctx.guild.id not in user_awards) or (arg2 not in user_awards[ctx.guild.id]):
				user_awards[ctx.guild.id][arg2] = {arg1: 1}
			else:
				if (arg1 in user_awards[ctx.guild.id][arg2]):
					user_awards[ctx.guild.id][arg2][arg1] += 1
				else:
					user_awards[ctx.guild.id][arg2][arg1] = 1

			await ctx.send(f"Gave {username} the award `{arg1}`, they now have **{user_awards[ctx.guild.id][arg2][arg1]}**")
		else:
			#await ctx.send(f"You've never made an award called `{arg1}`, would you like me to make one?")
			await ctx.send(f"You've never made an award called `{arg1}`, use the `create` command to make it first!")
	
	elif (command == "edit"):
		if (ctx.guild.id not in server_awards) or (arg1 not in server_awards[ctx.guild.id]):
			await ctx.send(f"The award `{arg1}` does not exist, use the `create` command to make it first!")
		else:
			server_awards[ctx.guild.id][arg1] = {"desc": arg2 , "image_link": arg3}

		embed = discord.Embed(title = arg1, description = server_awards[ctx.guild.id][arg1]["desc"], color = snoo_color)
		embed.set_author(name = f"||  AWARD", icon_url = award_icon)
		if (validators.url(server_awards[ctx.guild.id][arg1]["image_link"])):
			embed.set_image(url = server_awards[ctx.guild.id][arg1]["image_link"])

		await ctx.send("Here's your edited award!", embed = embed)

	elif (command == "list"):
		embed = discord.Embed(color = snoo_color)
		embed.set_author(name = f"||  AWARDS ON {ctx.guild.name.upper()}", icon_url = award_icon)

		for award in server_awards[ctx.guild.id]:
			embed.add_field(name = award, value = server_awards[ctx.guild.id][award]["desc"], inline = False)

		await ctx.send(embed = embed)

	elif (command == "profile"):
		if (arg1 == "none"):
			user_id = ctx.message.author.id
		else:
			user_id = re.search('!(.*)>', arg1).group(1)

		user_id = int(user_id)

		arg1 = await snoo.fetch_user(user_id)
		split_user = str(arg1).split("#", 1)
		username = split_user[0]
		
		if (user_id not in user_awards[ctx.guild.id]):
			await ctx.send(f"{username} currently doesn't have any awards!")
		else:
			embed = discord.Embed(colour=snoo_color)

			embed.set_author(name = f"||  {username.upper()}'S AWARDS", icon_url = profile_icon)

			for award in user_awards[ctx.guild.id][user_id]:
				embed.add_field(name = f"{award} x{user_awards[ctx.guild.id][user_id][award]}", value = server_awards[ctx.guild.id][award]["desc"], inline = False)
			
			await ctx.send(embed = embed)

	else:
		await ctx.send(f"Command `{command}` not found!")"""
	
"""@snoo.command()
async def top(ctx, length = "length"):
	if (length == "length"):
		length = 3

	if (length == "all"):
		length = len(user_karma[ctx.guild.id])

	if (int(length) <= 0):
		await ctx.send("Cannot display values under or equal to 0!")
		length = 3

	if (int(length) > len(user_karma[ctx.guild.id])):
		length = len(user_karma[ctx.guild.id])

	embed = discord.Embed(title="======= | LeaderBoards | =======", colour = snoo_color)

	simple_karma = {}

	for user in user_karma[ctx.guild.id]:
		simple_karma[user] = user_karma[ctx.guild.id][user][len(user_karma[ctx.guild.id][user]) - 1]

	iteration = 1
	for key in dict(sorted(simple_karma.items(), key = lambda item: item[1], reverse = True)):
		place = ""
		if (iteration == 1):
			place = "1st"
		elif (iteration == 2):
			place = "2nd"
		elif (iteration == 3):
			place = "3rd"
		else:
			place = "{}th" .format(iteration)

		user = await snoo.fetch_user(key)
		split_user = str(user).split("#", 1)
		username = split_user[0]

		embed.add_field(name="{}: {} with: {} karma".format(place, username, simple_karma[key]), value="{} friendship".format(user_friendship[key]), inline = False)

		if (iteration >= length):
			break
		
		iteration += 1

	await ctx.send(embed=embed)"""

@snoo.command()
async def graph(ctx, type, *, data: discord.User):
	#if (type(data) == discord.TextChannel):
	#	df = pd.DataFrame(channel_messages[ctx.guild.id][data.id], columns = ['Messages'])
	#else:
	df = pd.DataFrame(profile_data[ctx.guild.id][data.id][type], columns = ['Karma'])
	message = await ctx.send(f"Graphing {loading_icon}")

	#layout = Layout(plot_bgcolor='rgb(47,49,54)')

	fig = px.line(df, markers=False, template = "seaborn")
	fig['data'][0]['line']['color']="#FF4400"
	#fig.update_layout(paper_bgcolor="#2f3136")
	fig.write_image("graph.png")
	print("hi")

	#plt.savefig("graph.png")
	await message.delete()
	await ctx.send(file=discord.File('graph.png'))

	#plt.clf()
	os.remove("graph.png")

# _________________________________________________________________ MUSIC _________________________________________________________________

info = {"video_info": defaultdict(dict)}

def find_video_info(url):
	headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
	resp = requests.get(url,headers=headers)
	soup = bs(resp.text,'html.parser')

	str_soup = str(soup.findAll('script'))

	start = ',"secondaryResults":{"secondaryResults":'
	end = '},"autoplay":{"autoplay":'

	st = str_soup.find(start) + len(start)
	en = str_soup.find(end)

	substring = str_soup[st:en]

	secondary_results = json.loads(substring)
	
	url = "http://www.youtube.com/watch?v=" + soup.find("meta", itemprop="videoId")["content"]
	info["video_info"][url]["id"] = soup.find("meta", itemprop="videoId")["content"]

	info["video_info"][url]["recomended_vids"] = secondary_results["results"]

	"""if ("og:restrictions:age" in str(soup.find_all("meta"))):
		if (soup.find("meta", {"property": "og:restrictions:age"})["content"] == "18+"):
			if (message != None):
				await message.delete()
			await ctx.send("Sorry, but I'm not allowed to play 18+ content since I'm only 6 months old!")
			return"""

	
	info["video_info"][url]["title"] = soup.find("meta", itemprop="name")["content"]
	info["video_info"][url]["publish_date"] = soup.find("meta", itemprop="datePublished")["content"]
	duration = soup.find("meta", itemprop="duration")["content"]
	views = int(soup.find("meta", itemprop="interactionCount")['content'])

	info["video_info"][url]["channel_link"] = "https://www.youtube.com/channel/" + soup.find("meta", itemprop="channelId")["content"]
	info["video_info"][url]["channel_name"] = soup.find("span", itemprop="author").next.next['content']

	info["video_info"][url]["thumbnail"] = soup.find("meta", {"name": "twitter:image"})['content']
	
	info["video_info"][url]["views"] = "{:,}".format(views)

	mins = re.search('PT(.*)M', duration)
	mins = int(mins.group(1))

	secs = re.search('M(.*)S', duration)
	secs = int(secs.group(1))
	
	info["video_info"][url]["duration"] = format_time(secs + mins * 60)
	info["video_info"][url]["secs_length"] = secs + mins * 60

	return url

def find_url(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)      
    return [x[0] for x in url]

def search_yt(search):
	query_string = urllib.parse.urlencode({'search_query' : search})
	html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
	search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())

	if (len(search_results) > 0):
		return 'http://www.youtube.com/watch?v=' + search_results[0]
	else:
		return "null"

def format_time(secs):
	hours, remainder = divmod(secs, 3600)
	minutes, seconds = divmod(remainder, 60)

	if (seconds < 10):
		seconds = "0" + str(seconds)

	if (hours >= 1):
		if (minutes < 10):
			minutes = "0" + str(minutes)
		return f"{hours}:{minutes}:{seconds}"
	else:
		return f"{minutes}:{seconds}"

@snoo.command()
async def plays(ctx, *, searchs = "null"):
	searchs_list = searchs.split(',')
	for search in searchs_list:
		await play(ctx, search = search)

@snoo.command()
async def play(ctx, *, search = "null", autoplay = "null"):
	if (autoplay == "null"):
		if (ctx.guild.id not in info):
			info[ctx.guild.id] = {}

		info[ctx.guild.id]["channel"] = ctx.channel
		info[ctx.guild.id]["voice"] = get(snoo.voice_clients, guild = ctx.guild)
		info[ctx.guild.id]["paused"] = False
		info[ctx.guild.id]["looping"] = False
		info[ctx.guild.id]["autoplay"] = True
		info[ctx.guild.id]["past queue"] = []
		message = None

		if (type(ctx.message.author.voice) == type(None)):
			await ctx.send("Make sure you're in a voice channel first!")
			return

		channel = ctx.message.author.voice.channel

		if info[ctx.guild.id]["voice"] and info[ctx.guild.id]["voice"].is_connected():
			await info[ctx.guild.id]["voice"].move_to(channel)
		else:
			info[ctx.guild.id]["voice"] = await channel.connect()

		if (ctx.message.reference is None):
			message = await ctx.send(f"Searching for `{search}` {loading_icon}")
			if (validators.url(search) and "youtu" in search):
				url = search
			else:
				result = search_yt(search)
				if (result != "null"):
					url = result
				else:
					await message.edit(content = "I wasn't able to find anything. Try something else?")
					return
		else:
			msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			if (len(find_url(msg.content)) >= 1):
				temp_url = find_url(msg.content)[0]
				if ("youtu" in temp_url):
					url = temp_url
				else:
					message = await ctx.send(f"Searching for `{msg.content}` <a:Loading:908094681504706570>")
					result = search_yt(msg.content)
					if (result != "null"):
						url = result
					else:
						await message.edit(content = "I wasn't able to find anything. Try something else?")
						return
			else:
				if (len(msg.embeds) >= 1): 
					if (str(msg.embeds[0].url) != "Embed.Empty"):
						if ("youtu" in msg.embeds[0].url):
							url = msg.embeds[0].url
						else:
							await ctx.send("That's not a YouTube link, I'm unable to play it!")
							return
					else:		
						await ctx.send("Sorry but I'm unable to understand what the content of that message is.")
						return
				elif (msg.content == ""):
					await ctx.send("Sorry but I'm unable to understand what the content of that message is.")
					return
				else:
					message = await ctx.send(f"Searching for `{msg.content}` <a:Loading:908094681504706570>")
					result = search_yt(msg.content)
					if (result != "null"):
						url = result
					else:
						await message.edit(content = "I wasn't able to find anything. Try something else?")
						return

	else:
		url = autoplay

	if (url not in info["video_info"]):
		url = find_video_info(url)

	if ("queue" not in info[ctx.guild.id]):
		info[ctx.guild.id]["queue"] = [url]
	else:
		info[ctx.guild.id]["queue"].append(url)
	
	if (autoplay == "null"):
		#queued = False

		if (not info[ctx.guild.id]["voice"].is_playing() and not info[ctx.guild.id]["paused"]):
			await play_url(ctx.guild.id, url)
			info[ctx.guild.id]["nowplaying"] = await ctx.send(embed = nowplaying_embed(ctx.guild.id, url))
			if (message != None):
				await message.delete()

			info[ctx.guild.id]["nowplaying_edits"] = 0	
			info[ctx.guild.id]["task"] = asyncio.create_task(async_timer(1, update_nowplaying, ctx.guild.id))
		else:
			#queued = True

			embed=discord.Embed(title = info["video_info"][url]["title"], url = url, description = f'by [{info["video_info"][url]["channel_name"]}]({info["video_info"][url]["channel_link"]})', color=snoo_color)

			embed.set_thumbnail(url=info["video_info"][url]["thumbnail"])
			embed.set_author(name = "||  QUEUED", icon_url=music_icon)

			#await ctx.send(embed=embed)

			if (message != None):
				await message.edit(content="", embed = embed)
			else:
				print("there was no message to edit and snoo was unable to send a conformation embed")
				await ctx.send(embed = embed)

		#if (not queued):
			#await check_if_song_ended(ctx.guild.id, url, info["video_info"][url]["secs_length"])
	else:
		await play_url(ctx.guild.id, url, True)
		#await check_if_song_ended(ctx.guild.id, url, info["video_info"][url]["secs_length"])

async def play_url(guild, url, display_ui = False):
	if (info[guild]["voice"].is_playing()):
		info[guild]["voice"].stop()

	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	if not info[guild]["voice"].is_playing():
		with YoutubeDL(YDL_OPTIONS) as ydl:
			vid = ydl.extract_info(url, download=False)
		URL = vid['url']

		info[guild]["voice"].play(FFmpegPCMAudio(source = URL, **FFMPEG_OPTIONS))

		info[guild]["voice"].is_playing()
		info[guild]["start_time"] = datetime.datetime.now()

	if (display_ui):
		msg = None
		async for message in info[guild]["channel"].history (limit = 5):
			if (len(message.embeds) >= 1):
				if (str(message.embeds[0].author.name) == "||  NOW PLAYING"):
					msg = message
					break

		if (msg == None):
			await info[guild]["nowplaying"].delete()
			info[guild]["nowplaying"] = await info[guild]["channel"].send(embed = nowplaying_embed(guild, url))

def nowplaying_embed(guild, url):
	embed=discord.Embed(title = info["video_info"][url]["title"], url = url, description = f'by [{info["video_info"][url]["channel_name"]}]({info["video_info"][url]["channel_link"]})', color=snoo_color)

	embed.set_thumbnail(url=info["video_info"][url]["thumbnail"])
	embed.set_author(name = "||  NOW PLAYING", icon_url=music_icon)

	embed.add_field(name="Views:", value = info["video_info"][url]["views"], inline=True)
	embed.add_field(name="Upload Date:", value = info["video_info"][url]["publish_date"], inline=True)

	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	playing_for = format_time(time_since_start.seconds)
	watch_prsnt = time_since_start.seconds * (100 / info["video_info"][url]["secs_length"])

	play_bar = f'{playing_for} / {info["video_info"][url]["duration"]} '

	playbar_length = 14

	playbar = "<:PlayBar:925476587439288381>"
	grey_playbar = "<:GreyPlayBar:925476587493785700>"

	verify_settings(guild)

	if (server_config[guild]["classic nowplaying bar"]):
		playbar = "📕"
		grey_playbar = "🖼️"

	play_bar += playbar * round(watch_prsnt * (playbar_length / 100))
	play_bar += grey_playbar * (playbar_length - round(watch_prsnt * (playbar_length / 100)))

	embed.add_field(name='Duration:', value = play_bar, inline=False)

	return embed

@snoo.command()
async def nowplaying(ctx):
	await info[ctx.guild.id]["nowplaying"].delete()
	info[ctx.guild.id]["nowplaying"] = await ctx.send(embed = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0]))
	info[ctx.guild.id]["channel"] = ctx.channel

async def update_nowplaying(guild):
	try:
		if (len(info[guild]["queue"]) > 0):
			if (info[guild]["voice"].is_playing()):
				await info[guild]["nowplaying"].edit(embed = nowplaying_embed(guild, info[guild]["queue"][0]))
			elif (not await check_if_song_ended(guild)):
				await play_url(guild, info[guild]["queue"][0])
		info[guild]["nowplaying_edits"] += 1
		if (info[guild]["nowplaying_edits"] > 300):
			info[guild]["nowplaying_edits"] = 0
			await info[guild]["nowplaying"].delete()
			info[guild]["nowplaying"] = await info[guild]["channel"].send(embed = nowplaying_embed(guild, info[guild]["queue"][0]))

	except:
		print("Update Failed")

async def play_next(guild):
	current_url = info[guild]["queue"][0]
	info[guild]["past queue"].append(current_url)

	if (not info[guild]["looping"]):
		del info[guild]["queue"][0]

	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	watch_prsnt = time_since_start.seconds * (1 / info["video_info"][current_url]["secs_length"])
	watch_prsnt = round(watch_prsnt, 2)
	print(watch_prsnt)

	if (len(info[guild]["queue"]) > 0):
		await play_url(guild, info[guild]["queue"][0], not info[guild]["looping"])
		#await check_if_song_ended(guild, info[guild]["queue"][0], info["video_info"][info[guild]["queue"][0]]["secs_length"] + 1)
	elif (info[guild]["autoplay"]):
		for i in range(5):
			if ("compactVideoRenderer" not in info["video_info"][current_url]["recomended_vids"][i]):
				continue
			else:
				info["video_info"][current_url]["recomended_vid"] = 'http://www.youtube.com/watch?v=' + info["video_info"][current_url]["recomended_vids"][i]["compactVideoRenderer"]["videoId"]

			if (info["video_info"][current_url]["recomended_vid"] not in info[guild]["past queue"] and "hour" not in info["video_info"][current_url]["recomended_vids"][i]["compactVideoRenderer"]["title"]["simpleText"].lower()):
				#print(info["video_info"][current_url]["title"], info["video_info"][current_url]["recomended_vids"][i]["compactVideoRenderer"]["title"]["simpleText"])
				#print(similar(info["video_info"][current_url]["title"], info["video_info"][current_url]["recomended_vids"][i]["compactVideoRenderer"]["title"]["simpleText"]))
				break

		await play(info[guild]["channel"], autoplay = info["video_info"][current_url]["recomended_vid"])

	for user in get_users_in_vc(True)[guild]:
		if (guild not in song_history or user not in guild[user]):
			song_history[guild][user] = [{info["video_info"][current_url]["id"]: [{"retention": watch_prsnt, "listen_time": time_since_start.seconds}]}]
		elif (info["video_info"][current_url]["id"] not in song_history[guild][len(song_history[guild]) - 1]):
			song_history[guild][user][-1][info["video_info"][current_url]["id"]] = [{"retention": watch_prsnt, "listen_time": time_since_start.seconds}]
		else:
			song_history[guild][-1][user][info["video_info"][current_url]["id"]].append({"retention": watch_prsnt, "listen_time": time_since_start.seconds})
	#info[guild]["task"].cancel()
	#info[guild]["task"] = asyncio.create_task(async_timer(1, update_nowplaying, guild))

@snoo.command()
async def pause(ctx):
	if info["voice"].is_playing():
		info["voice"].pause()
		await ctx.message.add_reaction("⏸️")
	else:
		info["voice"].resume()
		await ctx.message.add_reaction("▶️")

@snoo.command()
async def stop(ctx):
	if info[ctx.guild.id]["voice"].is_playing():
		info[ctx.guild.id]["queue"].clear()
		info[ctx.guild.id]["voice"].stop()
		info[ctx.guild.id]["task"].cancel()
		await info[ctx.guild.id]["voice"].disconnect()
		#info.pop(ctx.guild.id)

		embed=discord.Embed(title = "Have a nice day!", description = f"", color=snoo_color)
		embed.set_author(name = "||  STOPPED", icon_url=music_icon)
		#await ctx.send(embed=embed)
		await ctx.send(embed = embed)

@snoo.command()
async def queue(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (len(info[ctx.guild.id]["queue"]) > 1):
			embed=discord.Embed(title = "Now playing", description = "", color=snoo_color)
			embed.set_author(name = "||  QUEUE", icon_url=music_icon)
			
			songs = ""
			durations = ""
			#channels = ""

			for i in range(20):
				if (i + 1 > len(info[ctx.guild.id]["queue"]) > 1):
					break
				if (i == 0):
					embed.add_field(name = f'<a:MusicBars:917119951603646505> {info["video_info"][info[ctx.guild.id]["queue"][i]]["title"]}', value = info["video_info"][info[ctx.guild.id]["queue"][i]]["channel_name"], inline = True)
					embed.add_field(name = "Duration", value = info["video_info"][info[ctx.guild.id]["queue"][i]]["duration"], inline = True)
					embed.add_field(name = "Looping", value = info[ctx.guild.id]["looping"], inline = False)

					embed.set_thumbnail(url=info["video_info"][info[ctx.guild.id]["queue"][i]]["thumbnail"])
				else:
					chr_per_row = 40
					print(len(songs))
					if (len(songs) < 1024 - chr_per_row):
						songs += f"**{i}** " + info["video_info"][info[ctx.guild.id]["queue"][i]]["title"][0 : chr_per_row]
						if (len(info["video_info"][info[ctx.guild.id]["queue"][i]]["title"]) > chr_per_row):
							songs += "...\n"
						else:
							songs += "\n"
					else:
						break

					#channels += info["video_info"][info["queue"][i]]["channel_name"] + "\n"
					durations += info["video_info"][info[ctx.guild.id]["queue"][i]]["duration"] + "\n"

			embed.add_field(name = "Next Up", value = songs, inline=True)
			#embed.add_field(name = "Channel", value = channels, inline=True)
			embed.add_field(name = "Duration", value = durations, inline=True)
			
			await ctx.send(embed=embed)
		else:
			await ctx.send(embed = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0]))

@snoo.command()
async def skip(ctx):
	if (len(info[ctx.guild.id]["queue"]) > 1 or info[ctx.guild.id]["autoplay"]):
		info[ctx.guild.id]["channel"] = ctx.channel
		await info[ctx.guild.id]["nowplaying"].delete()
		info[ctx.guild.id]["nowplaying"] = await ctx.send(embed = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0]))
		await play_next(ctx.guild.id)
	else:
		await ctx.send("This is the last song in queue, I have nothing to skip to!")

async def check_if_song_ended(guild):#, url):#, delay):
	#await asyncio.sleep(delay)
	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	if (time_since_start.seconds + 1 < info["video_info"][info[guild]["queue"][0]]["secs_length"]):
		return False

	#if (len(info[guild]["queue"]) <= 0):
		#return

	#if (url == info[guild]["queue"][0]):
	if (len(info[guild]["queue"]) > 1 or info[guild]["looping"] or info[guild]["autoplay"]):
		await play_next(guild)
	else:
		await info[guild]["voice"].disconnect()
		info[guild]["task"].cancel()

		embed=discord.Embed(title = "Play something new!", description = f"", color=snoo_color)
		embed.set_author(name = "||  QUEUE ENDED", icon_url=music_icon)
		await info[guild]["channel"].send(embed=embed)

		info[guild]["queue"].clear()
	return True

@snoo.command()
async def loop(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (info[ctx.guild.id]["looping"]):
			info[ctx.guild.id]["looping"] = False
			await ctx.send("I will no longer loop!")
		else:
			info[ctx.guild.id]["looping"] = True
			await ctx.send("I'll now loop the current song!")

@snoo.command()
async def autoplay(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (info[ctx.guild.id]["autoplay"]):
			info[ctx.guild.id]["autoplay"] = False
			await ctx.send("I'll no longer automaticaly play videos!")
		else:
			info[ctx.guild.id]["autoplay"] = True
			await ctx.send("I'll do my best to choose an relevant video to play next!")

"""@snoo.command()
async def shuffle(ctx):
	if (info["voice"].is_playing()):
		nowplaying = info["queue"][0]
		info["queue"].remove(info["queue"][0])

		random.shuffle(info["queue"])

		info["queue"].insert(0, nowplaying)
		await ctx.send("I have shuffled the current queue!")"""

# _________________________________________________________________ DEBUGING _________________________________________________________________
@snoo.command()
async def test(ctx):
	if (ctx.message.author.id == 401442600931950592):
		for key in channel_messages:
			for new_key in channel_messages[key]:
				channel_messages[key][new_key].append(0)
	else:
		await ctx.send(admin_command_message)

@snoo.command()
async def ping(ctx):
	delay_time = datetime.datetime.now() - ctx.message.created_at
	delay_ms = delay_time.total_seconds() * 1000
	delay_ms = round(delay_ms, 2)
	await ctx.send(str(delay_ms) + "ms")

# _________________________________________________________________ SYSTEM _________________________________________________________________
def total_to_per_day(in_dict):
	new_dict = deepcopy(in_dict)
	for guild in in_dict:
		for user in in_dict[guild]:
			for day in range(len(in_dict[guild][user])):
				if (day == 0):
					continue
				#print(dict[guild][user][day], dict[guild][user][day - 1], dict[guild][user][day] - dict[guild][user][day - 1])
				new_dict[guild][user][day] = in_dict[guild][user][day] - in_dict[guild][user][day - 1]
	if (new_dict == in_dict):
		print("true")
	return new_dict

"""def unite_data():
	new_dict = defaultdict(dict)
	for guild in user_messages:
		for user in user_messages[guild]:
			if (guild not in new_dict or user not in new_dict[guild]):
				new_dict[guild][user] = {"messages": [0], "vc_time": [0], "friendship": [0], "karma": [0]}
			new_dict[guild][user]["messages"] = user_messages[guild][user]
	for guild in user_vc_time:
		for user in user_vc_time[guild]:
			if (guild not in new_dict or user not in new_dict[guild]):
				new_dict[guild][user] = {"messages": [0], "vc_time": [0], "friendship": [0], "karma": [0]}
			new_dict[guild][user]["vc_time"] = user_vc_time[guild][user]
	for guild in user_friendship:
		for user in user_friendship[guild]:
			if (guild not in new_dict or user not in new_dict[guild]):
				new_dict[guild][user] = {"messages": [0], "vc_time": [0], "friendship": [0], "karma": [0]}
			new_dict[guild][user]["friendship"] = user_friendship[guild][user]
	for guild in user_karma:
		for user in user_karma[guild]:
			if (guild not in new_dict or user not in new_dict[guild]):
				new_dict[guild][user] = {"messages": [0], "vc_time": [0], "friendship": [0], "karma": [0]}
			new_dict[guild][user]["karma"] = user_karma[guild][user]

	return new_dict
	final_dict = defaultdict(dict)
	for guild in new_dict:
		for user in new_dict[guild]:
			list_len = max(len(new_dict[guild][user]["messages"]), len(new_dict[guild][user]["vc_time"]), len(new_dict[guild][user]["friendship"]), len(new_dict[guild][user]["karma"]))
			final_dict[guild][user] = [0] * list_len
			while (len(new_dict[guild][user]["messages"]) < list_len):
				new_dict[guild][user]["messages"].insert(0, 0)
			while (len(new_dict[guild][user]["vc_time"]) < list_len):
				new_dict[guild][user]["vc_time"].insert(0, 0)
			while (len(new_dict[guild][user]["friendship"]) < list_len):
				new_dict[guild][user]["friendship"].insert(0, 0)
			while (len(new_dict[guild][user]["karma"]) < list_len):
				new_dict[guild][user]["karma"].insert(0, 0)
			for i in range(list_len):
				final_dict[guild][user][i] = {"messages": new_dict[guild][user]["messages"][i], "vc_time": new_dict[guild][user]["vc_time"][i], "friendship": new_dict[guild][user]["friendship"][i], "karma": new_dict[guild][user]["karma"][i]}

	return final_dict"""

def get_users_in_vc(exclude_snoo = False):
	users_in_vc = {}

	for guild in snoo.guilds:
		for vc in guild.voice_channels:
			if (len(vc.members) > 0):
				users_in_vc[guild.id] = []
				for member in vc.members:
					if (exclude_snoo and member == snoo.user):
						continue
					users_in_vc[guild.id].append(member.id)
	
	return users_in_vc

def verify_settings(guild):
	if (guild not in server_config):
		server_config[guild] = deepcopy(default_settings)

def verify_data(guild, user):
	if (guild not in profile_data or user not in profile_data[guild]):
		profile_data[guild][user] = {"messages": [0], "vc_time": [0], "friendship": [0], "karma": [0]}

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

@snoo.command()
async def add(ctx):
	if (ctx.message.author.id == 401442600931950592):
		add_entry()
		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)

def add_entry():
	for guild in profile_data:
		for user in profile_data[guild]:
			for data in profile_data[guild][user]:
				profile_data[guild][user][data].append(0)

	for server in channel_messages:
		for channel in channel_messages[server]:
			channel_messages[server][channel].append(0)

	for server in song_history:
		for user in song_history[server]:
			song_history[server][user].append({})

def check_time():
	threading.Timer(60, check_time).start()

	now = datetime.datetime.now()
	current_time = now.strftime("%H:%M")

	if (current_time == "05:00"):
		add_entry()

@snoo.command()
async def save(ctx):
	if (ctx.message.author.id == 401442600931950592):
		await new_save()

		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)

async def new_save():
	print("Saving...")

	users_in_vc = get_users_in_vc()
	for server in users_in_vc:
		for user in users_in_vc[server]:
			verify_data(server, user)

			profile_data[server][user]["vc_time"][-1] = round(profile_data[server][user]["vc_time"][-1] + 0.1, 1)

			if (user not in user_candy):
				user_candy[user] = 1
			else:
				user_candy[user] += 1

	data_channel = snoo.get_channel(977316868253708359)
	with open("Data Files/profile.json", "w") as outfile:
		json.dump(profile_data, outfile)
	await data_channel.send(file=discord.File("Data Files/profile.json"))

	messages_channel = snoo.get_channel(913524223870398534)
	with open("Data Files/channel_messages.json", "w") as outfile:
		json.dump(channel_messages, outfile)
	await messages_channel.send(file=discord.File("Data Files/channel_messages.json"))

	songs_channel = snoo.get_channel(922592622248341505)
	with open("Data Files/song_history.json", "w") as outfile:
		json.dump(song_history, outfile)
	await songs_channel.send(file=discord.File("Data Files/song_history.json"))

	"""server_awards_channel = snoo.get_channel(959590449952194621)

	with open("Data Files/server_awards.json", "w") as outfile:
		json.dump(server_awards, outfile)

	await server_awards_channel.send(file=discord.File("Data Files/server_awards.json"))

	user_awards_channel = snoo.get_channel(959590569137541170)

	with open("Data Files/user_awards.json", "w") as outfile:
		json.dump(user_awards, outfile)

	await user_awards_channel.send(file=discord.File("Data Files/user_awards.json"))"""

	print("Saved")

async def async_timer(interval, func, arg = None):
	while True:
		if (arg == None):
			await asyncio.gather(asyncio.sleep(interval), func(),)
		else:
			await asyncio.gather(asyncio.sleep(interval), func(arg),)

# _________________________________________________________________ RUN _________________________________________________________________

check_time()

with open('Token/filekey.key', 'rb') as filekey:
	key = filekey.read()

fernet = Fernet(key)

with open('Token/token.txt', 'rb') as enc_file:
    encrypted = enc_file.read()

snoo.run(fernet.decrypt(encrypted).decode('UTF-8'))