from asyncio.tasks import wait
from locale import Error
#from tracemalloc import start
#from turtle import end_fill
import discord
from discord import guild
from discord import message
from discord import channel
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import ctypes
import ctypes.util
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
import random
import urllib
#from urllib.request import Request, urlopen
import re
from validators.url import url
from youtube_dl import YoutubeDL
#from requests_html import AsyncHTMLSession 
from bs4 import BeautifulSoup as bs
import socket
import requests
#from decimal import Decimal

#from bs4.builder import TreeBuilder
#from bs4.element import nonwhitespace_re

import plotly.express as px

intents = discord.Intents.default()
intents.presences = True
intents.members = True
snoo = commands.Bot(command_prefix=['!s ', 'hey snoo, ', 'hey snoo ', 'snoo, ', 'snoo '], intents=intents)

#data
user_karma = defaultdict(dict)
user_friendship = {}
channel_messages = defaultdict(dict)
users_in_vc = {}
user_vc_time = defaultdict(dict)
top_songs = defaultdict(dict)

#global variables
admin_command_message = "You need to be my master to use this command!"
snoo_color = 0xe0917a
version = "0.4.12"

poll_icon = "https://media.discordapp.net/attachments/908157040155832350/930606118512779364/poll.png"
music_icon = "https://cdn.discordapp.com/attachments/908157040155832350/930609037807087616/snoo_music_icon.png"

@snoo.event
async def on_ready():
	print(f'We have logged in as {snoo.user}')
	
	await snoo.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with my master's sanity"))
	channel = snoo.get_channel(id=865007153109663765)

	await initialize_data()
	asyncio.create_task(async_timer(60 * 6, new_save))
	await channel.send(f"Running version: {version} on {socket.gethostname()}")
	#print(channel.guild.emojis)

async def initialize_data():
	#global user_karma_time
	global user_friendship
	global channel_messages
	global user_karma
	global users_in_vc
	global user_vc_time

	if (not os.path.isdir('Data Files')):
		os.makedirs("Data Files")

	data_channel = snoo.get_channel(913524327775895563)
	async for message in data_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/user_karma.json")

	f = open('Data Files/user_karma.json')

	str_karma_time = json.load(f)

	friend_channel = snoo.get_channel(913524431131918406)
	async for message in friend_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/user_friendship.json")

	f = open('Data Files/user_friendship.json')

	str_friendship = json.load(f)

	messages_channel = snoo.get_channel(913524223870398534)
	async for message in messages_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/channel_messages.json")

	f = open('Data Files/channel_messages.json')

	str_messages = json.load(f)

	songs_channel = snoo.get_channel(922592622248341505)
	async for message in songs_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/top_songs.json")

	f = open('Data Files/top_songs.json')

	str_top_songs = json.load(f)

	vc_channel = snoo.get_channel(917185952978468874)
	async for message in vc_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/user_vc_time.json")

	f = open('Data Files/user_vc_time.json')

	str_vc_time = json.load(f)

	user_vc_channel = snoo.get_channel(924786492872728616)
	async for message in user_vc_channel.history (limit = 1):
		await message.attachments[0].save("Data Files/users_in_vc.json")

	f = open('Data Files/users_in_vc.json')

	str_users_in_vc = json.load(f)

	#convert dictionarys to int:
	for key in str_karma_time:
		for new_key in str_karma_time[key]:
			user_karma[int(key)][int(new_key)] = str_karma_time[key][new_key]

	for key in str_friendship:
		user_friendship[int(key)] = str_friendship[key]

	for key in str_users_in_vc:
		users_in_vc[int(key)] = str_users_in_vc[key]

	for key in str_messages:
		for new_key in str_messages[key]:
			channel_messages[int(key)][int(new_key)] = str_messages[key][new_key]

	for key in str_vc_time:
		for new_key in str_vc_time[key]:
			user_vc_time[int(key)][int(new_key)] = str_vc_time[key][new_key]

	for key in str_top_songs:
		for new_key in str_top_songs[key]:
			top_songs[int(key)][new_key] = str_top_songs[key][new_key]

#dictionary updates
"""@snoo.event
async def on_member_join(member):
	await add_members(member.guild)

@snoo.event
async def on_guild_join(guild):
	await add_members(guild)

async def add_members(guild):
	#user_karma.clear()

	members = guild.fetch_members()
	async for m in members:
		if not (m.id in user_karma[guild.id]):
			user_karma[guild.id][m.id] = [1]
		if not (m.id in user_friendship):
			user_friendship[m.id] = 0"""

#message replys / simple polls
@snoo.event
async def on_message(message):
	if (message.guild.id not in channel_messages) or (message.channel.id not in channel_messages[message.guild.id]):
		channel_messages[message.guild.id][message.channel.id] = [1]
	else:
		channel_messages[message.guild.id][message.channel.id][len(channel_messages[message.guild.id][message.channel.id]) - 1] += 1
	
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

	#if ("i'm" in message.content.lower() and "sad" in message.content.lower()):
	#	await message.channel.send("Don't be! Everything will be alright. <3")

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

		if (reaction.message.guild.id not in user_karma) or (reaction.message.author.id not in user_karma[reaction.message.guild.id]):
			user_karma[reaction.message.guild.id][reaction.message.author.id] = [1]
		else:
			user_karma[reaction.message.guild.id][reaction.message.author.id][len(user_karma[reaction.message.guild.id][reaction.message.author.id]) - 1] += 1

		user_friendship[user.id] += 1

		if (reaction.message.reference is not None):
			msg = await reaction.message.channel.fetch_message(reaction.message.reference.message_id)
			if (msg.author != user):
				user_karma[reaction.message.channel.guild.id][msg.author.id][len(user_karma[reaction.message.channel.guild.id][msg.author.id]) - 1] += 1

	elif (reaction.emoji.name == "Downvote"):
		if (reaction.message.guild.id not in user_karma) or (reaction.message.author.id not in user_karma[reaction.message.guild.id]):
			user_karma[reaction.message.guild.id][reaction.message.author.id] = [1]
		else:
			user_karma[reaction.message.guild.id][reaction.message.author.id][len(user_karma[reaction.message.guild.id][reaction.message.author.id]) - 1] -= 1

		user_friendship[user.id] -= 1

@snoo.event
async def on_reaction_remove(reaction, user):
	if (user == snoo.user or user == reaction.message.author):
		return
	if (type(reaction.emoji) == str):
		return

	if (reaction.emoji.name == "Upvote"):
		user_karma[reaction.message.guild.id][reaction.message.author.id][len(user_karma[reaction.message.guild.id][reaction.message.author.id]) - 1] -= 1
		user_friendship[user.id] -= 1

		if (reaction.message.reference is not None):
			msg = await reaction.message.channel.fetch_message(reaction.message.reference.message_id)
			if (msg.author != user):
				user_karma[reaction.message.channel.guild.id][msg.author.id][len(user_karma[reaction.message.channel.guild.id][msg.author.id]) - 1] -= 1

	if (reaction.emoji.name == "Downvote"):
		user_karma[reaction.message.guild.id][reaction.message.author.id][len(user_karma[reaction.message.guild.id][reaction.message.author.id]) - 1] += 1
		user_friendship[user.id] += 1

@snoo.event
async def on_voice_state_update(member, before, after):
	if (not before.channel and after.channel):
		#print(f'{member} has joined vc')
		if (member.id not in users_in_vc[after.channel.guild.id]):
			users_in_vc[after.channel.guild.id].append(member.id)
	elif (before.channel and not after.channel):
		#print(f'{member} has left vc')
		users_in_vc[before.channel.guild.id].remove(member.id)

#utility
@snoo.command()
async def yt_mp3(ctx, *, url):
	if (validators.url(url) and "youtu" in url):
		ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192',}], 'outtmpl': "video.mp3",}
		with YoutubeDL(ydl_opts) as ydl:
			msg = await ctx.send(f"Downloading <a:Loading:908094681504706570>")

			ydl.download([url])

			await msg.delete()
			await ctx.send(file=discord.File('video.mp3'))
			os.remove("video.mp3")
	else:
		await ctx.send("That's not a youtube url!")

@snoo.command()
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
		await ctx.send("That's not a youtube url!")

@snoo.command()
async def poll(ctx, name, opt_a, opt_b, opt_c = "", opt_d = "", opt_e = "", opt_f = "", opt_g = "",):
	embed = discord.Embed(title = f"{name}", colour = snoo_color)
	embed.set_author(name = "||  POLL", icon_url = poll_icon)

	embed.add_field(name = f"Option  <:A_:908477372397920316>", value = opt_a, inline=False)
	embed.add_field(name = f"Option  <:B_:908477372637011968>", value = opt_b, inline=False)

	if (opt_c != ""):
		embed.add_field(name = f"Option  <:C_:908477373090000916>", value = opt_c, inline=False)
		if (opt_d != ""):
			embed.add_field(name = f"Option  <:D_:908477372607639572>", value = opt_d, inline=False)
			if (opt_e != ""):
				embed.add_field(name = f"Option  <:E_:908477372561506324>", value = opt_e, inline=False)
				if (opt_f != ""):
					embed.add_field(name = f"Option  <:F_:908477372511170620>", value = opt_f, inline=False)
					if (opt_g != ""):
						embed.add_field(name = f"Option  <:G_:908477372829949952>", value = opt_g, inline=False)

	poll = await ctx.send(embed=embed)

	await poll.add_reaction("<:A_:908477372397920316>")
	await poll.add_reaction("<:B_:908477372637011968>")

	if (opt_c != ""):
		await poll.add_reaction("<:C_:908477373090000916>")
		if (opt_d != ""):
			await poll.add_reaction("<:D_:908477372607639572>")
			if (opt_e != ""):
				await poll.add_reaction("<:E_:908477372561506324>")
				if (opt_f != ""):
					await poll.add_reaction("<:F_:908477372511170620>")
					if (opt_g != ""):
						await poll.add_reaction("<:G_:908477372829949952>")

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
async def remove(ctx, *, user: discord.User):
	if (ctx.message.author.id == 401442600931950592):
		user_karma[ctx.guild.id].pop(user.id, None)
		#user_karma.pop(user.id, None)

		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)

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
	#split_user = str(user).split("#", 1)
	#username = split_user[0]

	"""if (user_karma[ctx.guild.id][user_id][len(user_karma[ctx.guild.id][user_id]) - 1] > 0):
		color = 0xFF4400
	else:
		color = 0x9293FF"""
	embed = discord.Embed(colour=snoo_color)

	embed.set_author(name= "||  PROFILE", url=user.avatar_url, icon_url=user.avatar_url)

	#phrase = ""

	"""if (user_id == ctx.message.author.id) :
		phrase = f"You have: **{user_karma[ctx.guild.id][user_id][len(user_karma[ctx.guild.id][user_id]) - 1]}** karma"

	elif (user_id == 864990652956540949):
		phrase = f"I have: **{user_karma[ctx.guild.id][user_id][len(user_karma[ctx.guild.id][user_id]) - 1]}** karma"
	else:
		phrase = f"{username} has: **{user_karma[ctx.guild.id][user_id][len(user_karma[ctx.guild.id][user_id]) - 1]}** karma"""

	embed.add_field(name = f"{user_karma[ctx.guild.id][user_id][len(user_karma[ctx.guild.id][user_id]) - 1]} karma", value = '\u200b', inline = True)
	embed.add_field(name = f"{user_friendship[user_id]} friendship", value = '\u200b', inline = True)
	embed.add_field(name = f"{math.fsum(user_vc_time[ctx.guild.id][user_id])} VC hours", value = '\u200b', inline = False)
	
	await ctx.send(embed=embed)

@snoo.command()
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

	await ctx.send(embed=embed)

@snoo.command()
async def graph(ctx, *, data: Union[discord.TextChannel, discord.User]):
	#print(type(data), data)
	if (type(data) == discord.TextChannel):
		df = pd.DataFrame(channel_messages[ctx.guild.id][data.id], columns = ['Messages'])
	else:
		df = pd.DataFrame(user_karma[ctx.guild.id][data.id], columns = ['Karma'])

	#layout = Layout(plot_bgcolor='rgb(47,49,54)')

	fig = px.line(df, markers=True, template = "seaborn")
	fig['data'][0]['line']['color']="#FF4400"
	#fig.update_layout(paper_bgcolor="#2f3136")
	fig.write_image("graph.png")

	#plt.savefig("graph.png")
	await ctx.send(file=discord.File('graph.png'))

	#plt.clf()
	os.remove("graph.png")

#music
info = {"queue": [], "paused": False, "voice": None, "channel": discord.channel, "task": None, "looping": False, "autoplay": True, "nowplaying": discord.message, "video_info": defaultdict(dict)}

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
async def play(ctx, *, search = "null", autoplay = "null"):
	if (autoplay == "null"):
		info["channel"] = ctx.channel
	info["voice"] = get(snoo.voice_clients, guild = ctx.guild)
	info["looping"] = False
	message = None

	if (autoplay == "null"):
		if (ctx.message.reference is None):
			message = await ctx.send(f"Searching for `{search}` <a:Loading:908094681504706570>")
			if (validators.url(search) and "youtu" in search):
				url = search
			else:
				result = search_yt(search)
				if (result != "null"):
					url = result
				else:
					await ctx.send("I wasn't able to find anything. Try something else?")
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
						await ctx.send("I wasn't able to find anything. Try something else?")
						await message.delete()
						return
			else:
				if (len(msg.embeds) >= 1): 
					print(msg.embeds[0].url)
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
						await ctx.send("I wasn't able to find anything. Try something else?")
						await message.delete()
						return

		if (type(ctx.message.author.voice) == type(None)):
			await ctx.send("Make sure you're in a voice channel first!")
			return

		channel = ctx.message.author.voice.channel

		if info["voice"] and info["voice"].is_connected():
			await info["voice"].move_to(channel)
		else:
			info["voice"] = await channel.connect()
	else:
		url = autoplay

	info["queue"].append(url)

	if (url not in info["video_info"]):
		#session = AsyncHTMLSession()
		#response = await session.get(url)
		#await response.html.arender()

		"""hdr = {'User-Agent': 'Mozilla/5.0'}
		req = Request(url, headers=hdr)
		page = urlopen(req)
		soup = bs(page, 'html.parser')"""

		headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
		resp = requests.get(url,headers=headers)
		soup = bs(resp.text,'html.parser')

		str_soup = str(soup.findAll('script'))

		start = ',"secondaryResults":{"secondaryResults":'
		end = '},"autoplay":{"autoplay":'

		st = str_soup.find(start) + len(start)
		en = str_soup.find(end)

		substring = str_soup[st:en]

		with open("soup.txt", "w", encoding="utf-8") as f:
			f.write(str_soup)

		await ctx.send(file = discord.File("soup.txt"))
		secondary_results = json.loads(substring)

		if ("compactVideoRenderer" in secondary_results["results"][0]):
			info["video_info"][url]["recomended_vid"] = 'http://www.youtube.com/watch?v=' + secondary_results["results"][0]["compactVideoRenderer"]["videoId"]
		else:
			info["video_info"][url]["recomended_vid"] = 'http://www.youtube.com/watch?v=' + secondary_results["results"][1]["compactVideoRenderer"]["videoId"]

		if ("og:restrictions:age" in str(soup.find_all("meta"))):
			if (soup.find("meta", {"property": "og:restrictions:age"})["content"] == "18+"):
				if (message != None):
					await message.delete()
				await ctx.send("Sorry, but I'm not allowed to play 18+ content since I'm only 6 months old!")
				return

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
	
	if (autoplay == "null"):
		queued = False

		if (not info["voice"].is_playing() and not info["paused"]):
			await play_url(url)
			info["nowplaying"] = await ctx.send(embed = nowplaying_embed())
			info["task"] = asyncio.create_task(async_timer(1, update_nowplaying))
		else:
			queued = True

			embed=discord.Embed(title = info["video_info"][url]["title"], url = url, description = f'by [{info["video_info"][url]["channel_name"]}]({info["video_info"][url]["channel_link"]})', color=snoo_color)

			embed.set_thumbnail(url=info["video_info"][url]["thumbnail"])
			embed.set_author(name = "||  QUEUED", icon_url=music_icon)

			await ctx.send(embed=embed)

		if (message != None):
			await message.delete()

		if (not queued):
			await check_if_song_ended(url, info["video_info"][url]["secs_length"])
	else:
		await play_url(url, True)
		await check_if_song_ended(url, info["video_info"][url]["secs_length"])

async def play_url(url, display_ui = False):
	if (info["voice"].is_playing()):
		info["voice"].stop()

	if ("watch?v=" in url):
		song_url = url.split("watch?v=",1)[1]
	elif ("youtu.be" in url):
		song_url = url.split("be/",1)[1]

	if (song_url not in top_songs[info["voice"].guild.id]):
		top_songs[info["voice"].guild.id][song_url] = 1
	else:
		top_songs[info["voice"].guild.id][song_url] += 1

	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	if not info["voice"].is_playing():
		with YoutubeDL(YDL_OPTIONS) as ydl:
			vid = ydl.extract_info(url, download=False)
		URL = vid['url']

		info["voice"].play(FFmpegPCMAudio(source = URL, **FFMPEG_OPTIONS))
		info["voice"].is_playing()
		info["start_time"] = datetime.datetime.now()

	if (display_ui):
		msg = None
		async for message in info["channel"].history (limit = 5):
			if (len(message.embeds) >= 1):
				if (str(message.embeds[0].author.name) == "||  NOW PLAYING"):
					msg = message
					break

		if (msg == None):
			await info["nowplaying"].delete()
			info["nowplaying"] = await info["channel"].send(embed = nowplaying_embed())

def nowplaying_embed():
	embed=discord.Embed(title = info["video_info"][info["queue"][0]]["title"], url = info["queue"][0], description = f'by [{info["video_info"][info["queue"][0]]["channel_name"]}]({info["video_info"][info["queue"][0]]["channel_link"]})', color=snoo_color)

	embed.set_thumbnail(url=info["video_info"][info["queue"][0]]["thumbnail"])
	embed.set_author(name = "||  NOW PLAYING", icon_url=music_icon)

	embed.add_field(name="Views:", value = info["video_info"][info["queue"][0]]["views"], inline=True)
	embed.add_field(name="Upload Date:", value = info["video_info"][info["queue"][0]]["publish_date"], inline=True)

	time_since_start = datetime.datetime.now() - info["start_time"]
	playing_for = format_time(time_since_start.seconds)
	watch_prsnt = time_since_start.seconds * (100 / info["video_info"][info["queue"][0]]["secs_length"])

	play_bar = f'{playing_for} / {info["video_info"][info["queue"][0]]["duration"]} '

	playbar_length = 14

	play_bar += "<:PlayBar:925476587439288381>" * round(watch_prsnt * (playbar_length / 100))
	play_bar += "<:GreyPlayBar:925476587493785700>" * (playbar_length - round(watch_prsnt * (playbar_length / 100)))

	embed.add_field(name='Duration:', value = play_bar, inline=False)

	return embed

@snoo.command()
async def nowplaying(ctx):
	info["nowplaying"] = await ctx.send(embed = nowplaying_embed())

async def update_nowplaying():
	if (len(info["queue"]) > 0):
		await info["nowplaying"].edit(embed = nowplaying_embed())

async def play_next():
	current_url = info["queue"][0]

	if (not info["looping"]):
		del info["queue"][0]

	if (len(info["queue"]) > 0):
		await play_url(info["queue"][0], not info["looping"])
		await check_if_song_ended(info["queue"][0], info["video_info"][info["queue"][0]]["secs_length"] + 1)
	elif (info["autoplay"]):
		await play(info["channel"], autoplay = info["video_info"][current_url]["recomended_vid"])
		print(info["queue"])

"""@snoo.command()
async def pause(ctx):
	if info["voice"].is_playing():
		info["voice"].pause()
		info["paused"] = True
		await ctx.message.add_reaction("⏸️")
	else:
		info["voice"].resume()
		info["paused"] = False
		await ctx.message.add_reaction("▶️")"""

@snoo.command()
async def stop(ctx):
	if info["voice"].is_playing():
		info["queue"].clear()
		info["video_info"].clear()
		info["voice"].stop()
		info["task"].cancel()
		await info["voice"].disconnect()

		embed=discord.Embed(title = "Have a nice day!", description = f"", color=snoo_color)
		embed.set_author(name = "||  STOPPED", icon_url=music_icon)
		await ctx.send(embed=embed)

@snoo.command()
async def queue(ctx):
	if (info["voice"].is_playing()):
		if (len(info["queue"]) > 1):
			embed=discord.Embed(title = "Now playing", description = "", color=snoo_color)
			embed.set_author(name = "||  QUEUE", icon_url=music_icon)
			
			songs = ""
			durations = ""
			#channels = ""

			for i in range(len(info["queue"])):
				if (i == 0):
					embed.add_field(name = f'<a:MusicBars:917119951603646505> {info["video_info"][info["queue"][i]]["title"]}', value = info["video_info"][info["queue"][i]]["channel_name"], inline = True)
					embed.add_field(name = "Duration", value = info["video_info"][info["queue"][i]]["duration"], inline = True)
					embed.add_field(name = "Looping", value = info["looping"], inline = False)

					embed.set_thumbnail(url=info["video_info"][info["queue"][i]]["thumbnail"])
				else:
					songs += f"**{i}** " + info["video_info"][info["queue"][i]]["title"][0 : 45]
					if (len(info["video_info"][info["queue"][i]]["title"]) > 30):
						songs += "...\n"
					else:
						songs += "\n"

					#channels += info["video_info"][info["queue"][i]]["channel_name"] + "\n"
					durations += info["video_info"][info["queue"][i]]["duration"] + "\n"

			embed.add_field(name = "Next Up", value = songs, inline=True)
			#embed.add_field(name = "Channel", value = channels, inline=True)
			embed.add_field(name = "Duration", value = durations, inline=True)
			
			await ctx.send(embed=embed)
		else:
			await ctx.send(embed = nowplaying_embed())

@snoo.command()
async def skip(ctx):
	if (len(info["queue"]) > 1 or info["autoplay"]):
		info["channel"] = ctx.channel
		await play_next()
	else:
		await ctx.send("This is the last song in queue, I have nothing to skip to!")

async def check_if_song_ended(url, delay):
	await asyncio.sleep(delay)

	if (len(info["queue"]) <= 0):
		return

	if (url == info["queue"][0]):
		if (len(info["queue"]) > 1 or info["looping"] or info["autoplay"]):
			await play_next()
		else:
			await info["voice"].disconnect()
			info["task"].cancel()

			embed=discord.Embed(title = "Play something new!", description = f"", color=snoo_color)
			embed.set_author(name = "||  QUEUE ENDED", icon_url=music_icon)
			await info["channel"].send(embed=embed)

			info["queue"].clear()
			info["video_info"].clear()

@snoo.command()
async def loop(ctx):
	if (info["voice"].is_playing()):
		if (info["looping"]):
			info["looping"] = False
			await ctx.send("I will no longer loop!")
		else:
			info["looping"] = True
			await ctx.send("I'll now loop the current song!")

@snoo.command()
async def autoplay(ctx):
	if (info["voice"].is_playing()):
		if (info["autoplay"]):
			info["autoplay"] = False
			await ctx.send("I'll no longer automaticaly play videos!")
		else:
			info["autoplay"] = True
			await ctx.send("I'll do my best to choose an relevant video to play next!")

@snoo.command()
async def shuffle(ctx):
	if (info["voice"].is_playing()):
		nowplaying = info["queue"][0]
		info["queue"].remove(info["queue"][0])

		random.shuffle(info["queue"])

		info["queue"].insert(0, nowplaying)
		await ctx.send("I have shuffled the current queue!")

#debugging
@snoo.command()
async def test(ctx):
	if (ctx.message.author.id == 401442600931950592):
		for key in channel_messages:
			for new_key in channel_messages[key]:
				channel_messages[key][new_key].append(0)
	else:
		await ctx.send(admin_command_message)

@snoo.command()
async def hash(ctx, hash = "f"):
	if (ctx.message.author.id == 401442600931950592):
		hash = ""
		if (hash != "f") :
			for key in user_karma:
				username = await snoo.fetch_user(key)
				hash += "{}({}): {} (**{}**)\n" .format(key, type(key), user_karma[key], username)
		else :
			for key in user_friendship:
				username = await snoo.fetch_user(key)
				hash += "{}: {} (**{}**)\n" .format(key, user_friendship[key], username)
		
		await ctx.send(hash)
	else:
		await ctx.send(admin_command_message)

@snoo.command()
async def ping(ctx):
	delay_time = datetime.datetime.now() - ctx.message.created_at
	delay_ms = delay_time.total_seconds() * 1000
	delay_ms = round(delay_ms, 2)
	await ctx.send(str(delay_ms) + "ms")

"""@snoo.command()
async def rehash(ctx, type = "normal"):
	if (ctx.message.author.id == 401442600931950592):
		guild = ctx.message.channel.guild
			
		if (type == "full") :
			user_karma.clear()
			user_friendship.clear()
			
		await add_members(guild)

		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)"""

#system
@snoo.command()
async def add(ctx):
	if (ctx.message.author.id == 401442600931950592):
		await add_entry()

		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)

def add_entry():
	for server in user_karma:
		for user in user_karma[server]:
			user_karma[server][user].append(user_karma[server][user][len(user_karma[server][user]) - 1])

	for server in channel_messages:
		for channel in channel_messages[server]:
			channel_messages[server][channel].append(0)

	for server in user_vc_time:
		for user in user_vc_time[server]:
			user_vc_time[server][user].append(0)

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
	global user_karma
	global user_friendship
	global channel_messages
	global user_vc_time

	for server in users_in_vc:
		for user in users_in_vc[server]:
			if (user not in user_vc_time[server]):
				user_vc_time[server][user] = [0.1]
				#user_vc_time[server][user] = round(user_vc_time[server][user], 1)
			else:
				#user_vc_time[server][user][len(user_vc_time[server][user]) - 1] += 0.1
				user_vc_time[server][user][len(user_vc_time[server][user]) - 1] = round(user_vc_time[server][user][len(user_vc_time[server][user]) - 1] + 0.1, 1)
				#user_vc_time[server][user][len(user_vc_time[server][user]) - 1] = round(user_vc_time[server][user][len(user_vc_time[server][user]) - 1], 1)

	data_channel = snoo.get_channel(913524327775895563)
	async for message in data_channel.history (limit = 1):
		await message.delete()

	with open("Data Files/user_karma.json", "w") as outfile:
		json.dump(user_karma, outfile)

	await data_channel.send(file=discord.File("Data Files/user_karma.json"))

	friend_channel = snoo.get_channel(913524431131918406)
	async for message in friend_channel.history (limit = 1):
		await message.delete()

	with open("Data Files/user_friendship.json", "w") as outfile:
		json.dump(user_friendship, outfile)

	await friend_channel.send(file=discord.File("Data Files/user_friendship.json"))

	messages_channel = snoo.get_channel(913524223870398534)
	async for message in messages_channel.history (limit = 1):
		await message.delete()

	with open("Data Files/channel_messages.json", "w") as outfile:
		json.dump(channel_messages, outfile)

	await messages_channel.send(file=discord.File("Data Files/channel_messages.json"))

	vc_channel = snoo.get_channel(917185952978468874)
	async for message in vc_channel.history (limit = 1):
		await message.delete()

	with open("Data Files/user_vc_time.json", "w") as outfile:
		json.dump(user_vc_time, outfile)

	await vc_channel.send(file=discord.File("Data Files/user_vc_time.json"))

	user_vc_channel = snoo.get_channel(924786492872728616)
	async for message in user_vc_channel.history (limit = 1):
		await message.delete()

	with open("Data Files/users_in_vc.json", "w") as outfile:
		json.dump(users_in_vc, outfile)

	await user_vc_channel.send(file=discord.File("Data Files/users_in_vc.json"))

	songs_channel = snoo.get_channel(922592622248341505)
	async for message in songs_channel.history (limit = 1):
		await message.delete()

	with open("Data Files/top_songs.json", "w") as outfile:
		json.dump(top_songs, outfile)

	await songs_channel.send(file=discord.File("Data Files/top_songs.json"))

	print("Saved")

async def async_timer(timeout, func):
	while True:
		await asyncio.sleep(timeout)
		await func()


#run snoo
check_time()

with open('Token/filekey.key', 'rb') as filekey:
	key = filekey.read()

fernet = Fernet(key)

with open('Token/token.txt', 'rb') as enc_file:
    encrypted = enc_file.read()

snoo.run(fernet.decrypt(encrypted).decode('UTF-8'))