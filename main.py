import ctypes
from hashlib import new
from http import server
from importlib.resources import contents
from xmlrpc.client import FastMarshaller
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
from urllib.parse import urlparse, parse_qs
from contextlib import suppress
import re
from validators.url import url
from youtube_dl import YoutubeDL
from bs4 import BeautifulSoup as bs
import socket
import requests
import plotly.express as px
from difflib import SequenceMatcher
from copy import deepcopy
from random import shuffle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

intents = discord.Intents.default()
intents.presences = True
intents.members = True
snoo = commands.Bot(command_prefix=['!s ', 'hey snoo, ', 'hey snoo ', 'snoo, ', 'snoo ', 'Hey snoo, ', 'Hey snoo ', 'Snoo, ', 'Snoo ', 'Hey Snoo, ', 'Hey Snoo ', 'hey snoo, ', 'hey snoo '], intents=intents)

# _________________________________________________________________ DATA _________________________________________________________________

profile_data = defaultdict(dict)
channel_messages = defaultdict(dict)
song_history = defaultdict(dict)
server_config = defaultdict(dict)
playlists = defaultdict(dict)
language = defaultdict(dict)
missing_translations = defaultdict(dict)
video_info = defaultdict(dict)

# _________________________________________________________________ GLOBAL VARS _________________________________________________________________

admin_command_message = "you need to be my master to use this command!"
snoo_color = 0xe0917a
version = "0.4.33 (completely redo play for playlists) BETA"
lang_set = "English"

default_settings = {"votes": True, "downvote": True, "slim nowplaying": True, "large nowplaying thumbnail": True}
settings_info = {
	"votes": {"dev": False},
	"downvote": {"dev": False},
	"slim nowplaying": {"dev": False},
	"large nowplaying thumbnail": {"dev": False}
}

new_playlist = {"title": "new playlist", "desc": "", "cover": "https://cdn.discordapp.com/attachments/908157040155832350/999112912352333854/snoo_cover.png", "songs": []}

loading_icon = "<a:loading:977336498322030612>"
poll_icon = "https://media.discordapp.net/attachments/908157040155832350/930606118512779364/poll.png"
music_icon = "https://cdn.discordapp.com/attachments/908157040155832350/930609037807087616/snoo_music_icon.png"
profile_icon = "https://media.discordapp.net/attachments/908157040155832350/931732724203520000/profile.png"
award_icon = "https://cdn.discordapp.com/attachments/908157040155832350/958841770765066280/award_icon.png"
settings_icon = "https://cdn.discordapp.com/attachments/908157040155832350/985595253174190080/snoo_icon.png"

@snoo.event
async def on_ready():
	print(f'We have logged in as {snoo.user}')
	
	await snoo.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with my master's sanity"))
	channel = snoo.get_channel(865007153109663765)

	await initialize_data()
	verify_lang()
	str_json(missing_translations)
	await channel.send(file=discord.File('Cache/string.json'))
	asyncio.create_task(async_timer(60 * 6, new_save))
	await channel.send(f"running version: {version} on {socket.gethostname()}")
	
async def initialize_data():
	if (not os.path.isdir('Data Files')):
		os.makedirs("Data Files")
	if (not os.path.isdir('Cache')): 
		os.makedirs("Cache")
		
	global language
	f = open('System/language.json', encoding='utf8')
	language = json.load(f)

	channel = snoo.get_channel(977316868253708359)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save("Data Files/profile.json")
	f = open('Data Files/profile.json')
	str_profile = json.load(f)

	channel = snoo.get_channel(913524223870398534)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save("Data Files/channel_messages.json")
	f = open('Data Files/channel_messages.json')
	str_messages = json.load(f)

	channel = snoo.get_channel(922592622248341505)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save("Data Files/song_history.json")
	f = open('Data Files/song_history.json')
	str_history = json.load(f)

	channel = snoo.get_channel(985597229022724136)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save("Data Files/server_config.json")
	f = open('Data Files/server_config.json')
	str_config = json.load(f)

	global playlists
	channel = snoo.get_channel(999117002323001354)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save("Data Files/playlists.json")
	f = open('Data Files/playlists.json')
	playlists = json.load(f)

	global video_info
	channel = snoo.get_channel(993332319454760960)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save("Data Files/video_info.json")
	f = open('Data Files/video_info.json')
	video_info = json.load(f)

	#convert dictionarys to int:
	for guild in str_profile:
		for user in str_profile[guild]:
			profile_data[int(guild)][int(user)] = str_profile[guild][user]

	for guild in str_messages:
		for channel in str_messages[guild]:
			channel_messages[int(guild)][int(channel)] = str_messages[guild][channel]

	for guild in str_history:
		for user in str_history[guild]:
			song_history[int(guild)][int(user)] = str_history[guild][user]

	for guild in str_config:
		server_config[int(guild)] = str_config[guild]

	"""for guild in str_playlists:
		for user in str_playlists[guild]:
			playlists[int(guild)][int(user)] = str_playlists[guild][user]"""

def verify_lang():
	loop_lang_cat("settings_info")
	loop_lang_cat("error")
	loop_lang_cat("notifs")
	loop_lang_cat("ui", "title")
	loop_lang_cat("ui", "field")

def loop_lang_cat(cat, cat2 = None):
	if (cat2 == None):
		for val in language["English"][cat]:
			for lang in language:
				if (lang == "English"):
					continue
				if (val not in language[lang][cat]):
					if (lang not in missing_translations):
						missing_translations[lang] = {}
					if (cat not in missing_translations[lang]):
						missing_translations[lang][cat] = {}
					missing_translations[lang][cat][val] = language["English"][cat][val]
					language[lang][cat][val] = language["English"][cat][val]
	else:
		for val in language["English"][cat][cat2]:
			for lang in language:
				if (lang == "English"):
					continue
				if (val not in language[lang][cat][cat2]):
					if (lang not in missing_translations):
						missing_translations[lang] = {}
					if (cat not in missing_translations[lang]):
						missing_translations[lang][cat] = {}
					if (cat2 not in missing_translations[lang][cat]):
						missing_translations[lang][cat][cat2] = {}
					missing_translations[lang][cat][cat2][val] = language["English"][cat][cat2][val]
					language[lang][cat][cat2][val] = language["English"][cat][cat2][val]

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
		channel_messages[message.guild.id][message.channel.id][-1] += 1

	verify_data(message.guild.id, message.author.id)
	profile_data[message.guild.id][message.author.id]["messages"][-1] += 1

	if (message.author == snoo.user):
		return

	verify_settings(message.guild.id)

	if (server_config[message.guild.id]["votes"]):
		if (message.attachments or validators.url(message.content) or '*image*' in message.content.lower()):
			upvote = None
			downvote = None

			for emoji in message.channel.guild.emojis:
				if (emoji.name.lower() == "upvote"):
					upvote = emoji
					if (not server_config[message.guild.id]["downvote"]):
						break
				if (emoji.name.lower() == "downvote"):
					downvote = emoji
				if (upvote != None and downvote != None):
					break

			if (upvote == None):
				await message.add_reaction("<:Upvote:919356607563972628>")
			else:
				await message.add_reaction(upvote)
			if (server_config[message.guild.id]["downvote"]):
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

	#commands
	await snoo.process_commands(message)

#upvote adding and taking away
@snoo.event
async def on_reaction_add(reaction, user) :
	if (user == snoo.user or user == reaction.message.author):
		return
	if (type(reaction.emoji) == str):
		return

	if (reaction.emoji.name.lower() == "upvote") :
		verify_data(reaction.message.guild.id, reaction.message.author.id)
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] += 1

		verify_data(reaction.message.guild.id, user.id)
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] += 1

	elif (reaction.emoji.name.lower() == "downvote"):
		verify_data(reaction.message.guild.id, reaction.message.author.id)
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] -= 1

		verify_data(reaction.message.guild.id, user.id)
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] -= 1

@snoo.event
async def on_reaction_remove(reaction, user):
	if (user == snoo.user or user == reaction.message.author):
		return
	if (type(reaction.emoji) == str):
		return

	if (reaction.emoji.name.lower() == "upvote"):
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] -= 1
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] -= 1

	if (reaction.emoji.name.lower() == "downvote"):
		profile_data[reaction.message.guild.id][reaction.message.author.id]["karma"][-1] += 1
		profile_data[reaction.message.guild.id][user.id]["friendship"][-1] += 1

# _________________________________________________________________ UTILITY _________________________________________________________________

@snoo.command()
async def config(ctx, *, setting = None):
	verify_settings(ctx.guild.id)
	if (setting != None):
		setting = setting.lower()
		if (setting in server_config[ctx.guild.id]):
			if (server_config[ctx.guild.id][setting]):
				server_config[ctx.guild.id][setting] = False
			else:
				server_config[ctx.guild.id][setting] = True
			await ctx.send("👍")
		else:
			await ctx.send(language[lang_set]["error"]["setting_not_found"])
	else:
		embed = discord.Embed(colour=snoo_color)
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['settings'].upper()}", icon_url = settings_icon)
		for config in server_config[ctx.guild.id]:
			if (settings_info[config]["dev"]):
				continue
			embed.add_field(name = config.upper(), value = language[lang_set]["settings_info"][config], inline = True)
			embed.add_field(name = '\u200b', value = '\u200b', inline = True)
			if (server_config[ctx.guild.id][config]):
				embed.add_field(name = "<:on1:985591109998759986><:on2:985591107524104324>", value = "\u200b", inline = True)
			else:
				embed.add_field(name = "<:off1:985591110799884309><:off2:985591108929208320>", value = "\u200b", inline = True)
		await ctx.send(embed=embed)

@snoo.command()
async def poll(ctx, name, *, opts):
	emojis = ["<:A_:908477372397920316>", "<:B_:908477372637011968>", "<:C_:908477373090000916>", "<:D_:908477372607639572>", "<:E_:908477372561506324>", "<:F_:908477372511170620>", "<:G_:908477372829949952>"]
	opts_list = opts.split(',')
	

	embed = discord.Embed(title = name, colour = snoo_color)
	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['poll'].upper()}", icon_url = poll_icon)

	for i in range(len(opts_list)):
		embed.add_field(name = f"{language[lang_set]['ui']['field']['option']}  {emojis[i]}", value = opts_list[i], inline=False)

	poll = await ctx.send(embed=embed)

	for i in range(len(opts_list)):
		await poll.add_reaction(emojis[i])

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

	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['profile'].format(username).upper()}", icon_url = profile_icon)

	embed.add_field(name = language[lang_set]['ui']['field']['karma']['title'], value = language[lang_set]['ui']['field']['karma']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['karma'])), inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = language[lang_set]['ui']['field']['friendship']['title'], value = language[lang_set]['ui']['field']['friendship']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['friendship'])), inline = True)
	embed.add_field(name = language[lang_set]['ui']['field']['messages']['title'], value = language[lang_set]['ui']['field']['messages']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['messages'])), inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = language[lang_set]['ui']['field']['vc_hours']['title'], value = language[lang_set]['ui']['field']['vc_hours']['desc'].format(math.fsum(profile_data[ctx.guild.id][user_id]['vc_time'])), inline = True)
	
	await ctx.send(embed=embed)

@snoo.command()
async def graph(ctx, type, *, data: discord.User):
	#if (type(data) == discord.TextChannel):
	#	df = pd.DataFrame(channel_messages[ctx.guild.id][data.id], columns = ['Messages'])
	#else:
	df = pd.DataFrame(profile_data[ctx.guild.id][data.id][type], columns = [type])
	message = await ctx.send(f"Graphing {loading_icon}")

	#layout = Layout(plot_bgcolor='rgb(47,49,54)')

	fig = px.line(df, markers=False, template = "seaborn")
	fig['data'][0]['line']['color']="#FF4400"
	#fig.update_layout(paper_bgcolor="#2f3136")
	fig.write_image("Cache/graph.png")

	#plt.savefig("graph.png")
	await message.delete()
	await ctx.send(file=discord.File('Cache/graph.png'))

	#plt.clf()
	#os.remove("graph.png")

@snoo.command()
async def extract(ctx, url = None):
	if (url == None):
		if (info[ctx.guild.id]["voice"].is_playing()):
			url = info[ctx.guild.id]["queue"][0]
		else:
			await ctx.send(language[lang_set]["error"]["no_url"])

	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
	with YoutubeDL(YDL_OPTIONS) as ydl:
		try:
			vid = ydl.extract_info(url, download=False)
		except:
			print("Failed to fetch video info")
			await ctx.send(language[lang_set]["error"]["extract"])
			return
	str_json(vid)
	await ctx.send(file=discord.File('Cache/string.json'))

@snoo.command()
async def playlist(ctx, *, arg1 = None):
	if (arg1 in playlists):
		embed = discord.Embed(title = playlists[arg1]["title"], desc = playlists[arg1]["desc"], color = snoo_color)
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['playlist'].upper()}", icon_url=music_icon)
		embed.set_thumbnail(url = playlists[arg1]["cover"])
		for song in playlists[arg1]["songs"]:
			embed.add_field(name = video_info[song]["title"], value = video_info[song]["channel_name"], inline = True)
			embed.add_field(name = '\u200b', value = '\u200b', inline = True)
			embed.add_field(name = format_time(video_info[song]["secs_length"]), value = "\u200b", inline = True)
		await ctx.send(embed = embed)

# _________________________________________________________________ MUSIC _________________________________________________________________

info = {}

@snoo.command()
async def find_playlist(ctx, playlist):
	await ctx.send(find_videos_playlist(playlist))

def find_videos_playlist(playlist):
	linklist = []
	if ("&playnext" in playlist):
		en = playlist.find("&playnext")
		playlist = playlist[:en]
	if ("watch?v=" in playlist):
		start = '.com/'
		end = 'list'
		st = playlist.find(start) + len(start)
		en = playlist.find(end)
		playlist = playlist.replace(playlist[st:en], "playlist?")

	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
	driver.get(playlist)
	page = driver.page_source
	soup = bs(page,'html.parser')

	if ("music" in playlist):
		dirs = soup.findAll('a', {'class': 'yt-simple-endpoint style-scope yt-formatted-string'})[1:]
	else:
		dirs = soup.findAll('a', {'class': 'yt-simple-endpoint style-scope ytd-playlist-video-renderer'})

	for link in dirs:
		if ("watch?v=" in link["href"]):
			start = 'watch?v='
			end = '&list'
			st = link["href"].find(start) + len(start)
			en = link["href"].find(end)
			linklist.append(link["href"][st:en])
	
	return linklist

def find_video_info(id, only_source = False):
	YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
	with YoutubeDL(YDL_OPTIONS) as ydl:
		try:
			vid = ydl.extract_info(id, download=False)
		except:
			print("Failed to fetch video info", id)
			return False

	#id = vid["id"]
	if (only_source):
		video_info[id]["source"] = vid["url"]
		return True

	video_info[id] = {}
	video_info[id]["source"] = vid["url"]
	video_info[id]["title"] = vid["title"]
	video_info[id]["views"] = vid["view_count"]
	video_info[id]["secs_length"] = vid["duration"]
	video_info[id]["publish_date"] = vid["upload_date"]
	video_info[id]["channel_link"] = vid["channel_url"]
	video_info[id]["channel_name"] = vid["uploader"]
	video_info[id]["thumbnail"] = vid["thumbnails"][-1]["url"]

	headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
	resp = requests.get('http://www.youtube.com/watch?v=' + id, headers=headers)
	soup = bs(resp.text,'html.parser')
	str_soup = str(soup.findAll('script'))

	start = ',"secondaryResults":{"secondaryResults":'
	end = '},"autoplay":{"autoplay":'
	st = str_soup.find(start) + len(start)
	en = str_soup.find(end)
	substring = str_soup[st:en]
	secondary_results = json.loads(substring)

	video_info[id]["recomended_vids"] = []
	for i in range(len(secondary_results["results"])):
		if ("compactVideoRenderer" not in secondary_results["results"][i]):
			continue
		elif ("hour" not in secondary_results["results"][i]["compactVideoRenderer"]["title"]["simpleText"].lower()):
			video_info[id]["recomended_vids"].append(secondary_results["results"][i]["compactVideoRenderer"]["videoId"])

	return True

def search_yt(search):
	query_string = urllib.parse.urlencode({'search_query' : search})
	html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
	search_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())

	if (len(search_results) > 0):
		return search_results[0]
	else:
		return True

def search_and_find_info(search):
	if (not verify_yt_id(search)):
		result = search_yt(search)
		if (result == None):
			return None
	else:
		result = search
	
	if (result not in video_info):
		if (not find_video_info(result)):
			return None
	
	return result

@snoo.command()
async def play(ctx, *, search = None, autoplay = None):
	skip_search = False
	playlist = None
	message = None
	id = None

	if (autoplay == None):
		if (ctx.guild.id not in info):
			info[ctx.guild.id] = {"channel": ctx.channel, "voice": get(snoo.voice_clients, guild = ctx.guild), "paused": False, "looping": False, "autoplay": True, "queue": [], "past queue": []}
		
		if (type(ctx.message.author.voice) == type(None)):
			await ctx.send(language[lang_set]["error"]["no_vc"])
			return

		searching = f'{language[lang_set]["notifs"]["searching"]} {loading_icon}'

		if (ctx.message.reference is None):
			if (validators.url(search) and "youtube" in search and "list=" in search):
				playlist = find_videos_playlist(search)
			elif (verify_yt_id(yt_id(search))):
				id = yt_id(search)
		else:
			msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
			if (len(find_url(msg.content)) >= 1):
				temp_url = find_url(msg.content)[0]
				if ("youtube" in temp_url and "list=" in temp_url):
					playlist = find_videos_playlist(temp_url)
				elif (verify_yt_id(yt_id(temp_url))):
					id = yt_id(temp_url)
				else:
					search = msg.content
			else:
				if (len(msg.embeds) >= 1): 
					if (str(msg.embeds[0].url) != "Embed.Empty"):
						if (verify_yt_id(yt_id(msg.embeds[0].url))):
							id = yt_id(msg.embeds[0].url)
						else:
							await ctx.send(language[lang_set]["error"]["not_youtube"])
							return
					else:		
						await ctx.send(language[lang_set]["error"]["no_content"])
						return
				elif (msg.content == ""):
					await ctx.send(language[lang_set]["error"]["no_content"])
					return
				else:
					search = msg.content

		if (id == None):
			if (playlist == None):
				if (search[0] == "[" and search[-1] == "]"):
					playlist = search.strip('][').split(', ')
				elif (search in playlists):
					playlist = playlists[search]["songs"]
			
			if (playlist != None):
				if (len(info[ctx.guild.id]["queue"]) < 1):
					search = playlist[0]
					playlist = playlist[1:]
				else:
					skip_search = True

			if (not skip_search):
				if (not verify_yt_id(search)):
					message = await ctx.send(searching.format(search))
					result = search_yt(search)
					if (result != None):
						id = result
					else:
						await message.edit(content = language[lang_set]["error"]["nothing_found"])
						return
				else:
					id = search
	else:
		id = autoplay

	if (not skip_search):
		found_info = True
		if (id not in video_info):
			print("new video")
			found_info = find_video_info(id)

		if (not valid_url(video_info[id]["source"])):
			print("url expired")
			found_info = find_video_info(id, True)

		if (not found_info):
			if (message != None):
				await message.edit(content = language[lang_set]["error"]["age_restricted"])
			else:
				await ctx.send(language[lang_set]["error"]["age_restricted"])
			return

		if (autoplay == None):
			channel = ctx.message.author.voice.channel

			if info[ctx.guild.id]["voice"] and info[ctx.guild.id]["voice"].is_connected():
				await info[ctx.guild.id]["voice"].move_to(channel)
			else:
				info[ctx.guild.id]["voice"] = await channel.connect()

		info[ctx.guild.id]["queue"].append(id)

		if (autoplay == None):
			if (len(info[ctx.guild.id]["queue"]) <= 1):
				await play_url(ctx.guild.id, id)

				embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
				if (server_config[ctx.guild.id]["large nowplaying thumbnail"]):
					info[ctx.guild.id]["thumbnail"] = await ctx.send(embed = embeds[1])
				info[ctx.guild.id]["nowplaying"] = await ctx.send(embed = embeds[0])

				if (message != None):
					await message.delete()

				info[ctx.guild.id]["nowplaying_edits"] = 0
				info[ctx.guild.id]["task"] = asyncio.create_task(async_timer(1, update_nowplaying, ctx.guild.id))
			else:
				#queued = True

				embed = discord.Embed(title = video_info[id]["title"], url = 'http://www.youtube.com/watch?v=' + id, description = f'[{video_info[id]["channel_name"]}]({video_info[id]["channel_link"]})', color=snoo_color)

				embed.set_thumbnail(url = video_info[id]["thumbnail"])
				embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()}", icon_url = music_icon)

				#await ctx.send(embed=embed)

				if (message != None):
					await message.edit(content="", embed = embed)
				else:
					print("there was no message to edit and snoo was unable to edit a conformation embed")
					await ctx.send(embed = embed)
		else:
			await play_url(ctx.guild.id, id)

		threading.Thread(target = find_autoplay, args = (ctx.guild.id, id, )).start()

	if (playlist != None):
		for i in range(len(playlist)):
			playlist[i] = yt_id(playlist[i])
			#print(playlist[i])
			#print(threading.Thread(target = search_and_find_info, args = (playlist[i], )).start())

		embed = discord.Embed(color = snoo_color)
		
		embed_msg = None
		edit_needed = False
		i = 0
		total_time = 0
		while (i < len(playlist)):
			if (playlist[i] in video_info):
				info[ctx.guild.id]["queue"].append(playlist[i])
				total_time += video_info[playlist[i]]["secs_length"]
				if (i < 25):
					embed.add_field(name = f'**{i + 1}** {video_info[playlist[i]]["title"]}', value = video_info[playlist[i]]["channel_name"], inline = False)
				else:
					embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["full"].format(i - 24, format_time(total_time)))

				if (edit_needed):
					if (i == 0):
						embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
					embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()} {i + 1} / {len(playlist)}", icon_url = music_icon)
					await embed_msg.edit(embed = embed)
					edit_needed = False

				i += 1
			else:
				if (embed_msg == None):
					if (i > 0):
						embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
					embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()} {i} / {len(playlist)}", icon_url = music_icon)
					embed_msg = await ctx.send(embed = embed)

				playlist[i] = search_and_find_info(playlist[i])
				if (playlist[i] == None):
					playlist.pop(i)

				edit_needed = True
		
		embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()}", icon_url = music_icon)
		if (i < 25):
			embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))
		if (embed_msg == None):
			embed_msg = await ctx.send(embed = embed)
		else:
			await embed_msg.edit(embed = embed)

		threading.Thread(target = find_autoplay, args = (ctx.guild.id, playlist[-1], )).start()

		for song in playlist:
			if (song == None):
				continue
			if (not valid_url(video_info[song]["source"])):
				threading.Thread(target = find_video_info, args = (song, True, )).start()

async def play_url(guild, id):
	if (info[guild]["voice"].is_playing()):
		info[guild]["voice"].stop()

	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	info[guild]["voice"].play(FFmpegPCMAudio(source = video_info[id]["source"], **FFMPEG_OPTIONS))
	info[guild]["voice"].is_playing()
	info[guild]["start_time"] = datetime.datetime.now()

def find_autoplay(guild, id):
	for vid in video_info[id]["recomended_vids"]:
		if (vid not in info[guild]["past queue"]):
			info[guild]["recomended_vid"] = vid
			if (vid not in video_info):
				print("finding autoplay info...")
				find_video_info(vid)
			break

def nowplaying_embed(guild, id):
	verify_settings(guild)

	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	playing_for = format_time(time_since_start.seconds)
	watch_prsnt = time_since_start.seconds * (100 / video_info[id]["secs_length"])

	play_bar = f'{playing_for}   '

	"""playbar_length = 14
	if (server_config[guild]["large nowplaying thumbnail"]):"""
	playbar_length = 18

	bar1 = "<:bar1:994058965279322144>"
	bar2 = ["<:bar31:994069492026048713>", "<:bar21:994063956178124882>", "<:bar2:994058964918616074>", "<:bar22:994063957117632572>", "<:bar12:994069492953010196>"]
	bar3 = "<:bar3:994058963509334018>"

	bar1r = "<:bar1R:995467490052280320>"
	bar2rR = ["<:bar31:994069492026048713>", "<:bar21r:995476810194223135>", "<:bar2r:995476813495152690>", "<:bar22r:995476811637067836>", "<:bar12r:995476812173942816>"]
	bar2rL = ["<:bar31rr:995479103954239610>", "<:bar21rr:995479102066798612>", "<:bar2rr:995479104453361675>", "<:bar22rr:995479102976962695>", "<:bar12:994069492953010196>"]
	bar3r = "<:bar3R:995467514144378992>"

	segments_prsnt = watch_prsnt * (playbar_length / 100)
	fill_error = 0.5
	empty_error = 0.5

	if (segments_prsnt > 1):
		play_bar += bar1r
		fill_error = 1.5
	if (playbar_length - segments_prsnt > 1):
		empty_error = 1.5
	play_bar += bar1 * round(segments_prsnt - fill_error)
	for i in range(5):
		if (segments_prsnt % 1 < (i + 1) * 0.2):
			if (segments_prsnt > 1 and playbar_length - segments_prsnt > 1):
				play_bar += bar2[i]
			elif (segments_prsnt < 1):
				play_bar += bar2rR[i]
			elif (playbar_length - segments_prsnt < 1):
				play_bar += bar2rL[i]
			break
	play_bar += bar3 * (playbar_length - round(segments_prsnt + empty_error))
	if (playbar_length - segments_prsnt > 1):
		play_bar += bar3r

	play_bar += f'   {format_time(video_info[id]["secs_length"])}'
	
	embed=discord.Embed(title = video_info[id]["title"], url = 'http://www.youtube.com/watch?v=' + id, description = f'[{video_info[id]["channel_name"]}]({video_info[id]["channel_link"]})\n\n{play_bar}', color=snoo_color)
	thumbnail_embed = None
	if (server_config[guild]["large nowplaying thumbnail"]):
		thumbnail_embed = discord.Embed(color = snoo_color)

		thumbnail_embed.set_image(url=video_info[id]["thumbnail"])
	else:
		embed.set_thumbnail(url=video_info[id]["thumbnail"])
	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['nowplaying'].upper()}", icon_url=music_icon)

	if (not server_config[guild]["slim nowplaying"]):
		embed.add_field(name = language[lang_set]['ui']['field']['views'], value = "{:,}".format(video_info[id]["views"]), inline=True)
		publish_date = str(video_info[id]["publish_date"])
		embed.add_field(name = language[lang_set]['ui']['field']['upload_date'], value = datetime.datetime(int(publish_date[0:4]), int(publish_date[4:6]), int(publish_date[6:8])).strftime("%b %d %Y"), inline=True)

	#embed.add_field(name='Duration:', value = play_bar, inline=False)

	return [embed, thumbnail_embed]

@snoo.command()
async def nowplaying(ctx):
	embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
	if (server_config[ctx.guild.id]["large nowplaying thumbnail"]):
		await info[ctx.guild.id]["thumbnail"].delete()
		info[ctx.guild.id]["thumbnail"] = await ctx.send(embed = embeds[1])
	await info[ctx.guild.id]["nowplaying"].delete()
	info[ctx.guild.id]["nowplaying"] = await ctx.send(embed = embeds[0])
	info[ctx.guild.id]["channel"] = ctx.channel

async def update_nowplaying(guild):
	try:
		if (len(info[guild]["queue"]) > 0 and info[guild]["nowplaying_edits"] >= 0):
			if (info[guild]["voice"].is_playing()):
				await info[guild]["nowplaying"].edit(embed = nowplaying_embed(guild, info[guild]["queue"][0])[0])
			elif (not await check_if_song_ended(guild)):
				print("refetching video info...")
				find_video_info(info[guild]["queue"][0])
				await play_url(guild, info[guild]["queue"][0])
		info[guild]["nowplaying_edits"] += 1
		if (info[guild]["nowplaying_edits"] > 300):
			info[guild]["nowplaying_edits"] = 0

			embeds = nowplaying_embed(guild, info[guild]["queue"][0])
			if (server_config[guild]["large nowplaying thumbnail"]):
				await info[guild]["thumbnail"].delete()
				info[guild]["thumbnail"] = await info[guild]["channel"].send(embed = embeds[1])
			await info[guild]["nowplaying"].delete()
			info[guild]["nowplaying"] = await info[guild]["channel"].send(embed = embeds[0])
	except:
		print("update failed")

async def play_next(guild):
	current_url = info[guild]["queue"][0]
	info[guild]["past queue"].append(current_url)
	if (not info[guild]["looping"]):
		del info[guild]["queue"][0]

	if (len(info[guild]["queue"]) > 0):
		await play_url(guild, info[guild]["queue"][0])
	elif (info[guild]["autoplay"]):
		await play(info[guild]["channel"], autoplay = info[guild]["recomended_vid"])

	await info[guild]["thumbnail"].edit(embed = nowplaying_embed(guild, info[guild]["queue"][0])[1])
	
	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	watch_prsnt = time_since_start.seconds * (1 / video_info[current_url]["secs_length"])
	watch_prsnt = round(watch_prsnt, 2)

	for user in get_users_in_vc(True)[guild]:
		if (guild not in song_history or user not in song_history[guild]):
			song_history[guild][user] = [{current_url: [{"retention": watch_prsnt, "listen_time": time_since_start.seconds}]}]
		elif (current_url not in song_history[guild][user][-1]):
			song_history[guild][user][-1][current_url] = [{"retention": watch_prsnt, "listen_time": time_since_start.seconds}]
		else:
			song_history[guild][user][-1][current_url].append({"retention": watch_prsnt, "listen_time": time_since_start.seconds})

"""@snoo.command()
async def pause(ctx):
	if (not info[ctx.guild.id]["paused"]):
		info[ctx.guild.id]["voice"].pause()
		info[ctx.guild.id]["paused"] = True
		await ctx.message.add_reaction("⏸️")
	else:
		info[ctx.guild.id]["voice"].resume()
		info[ctx.guild.id]["paused"] = False
		await ctx.message.add_reaction("▶️")"""

@snoo.command()
async def stop(ctx):
	if (ctx.guild.id in info and len(info[ctx.guild.id]["queue"]) >= 1):
		#info[ctx.guild.id]["queue"].clear()
		info[ctx.guild.id]["voice"].stop()
		info[ctx.guild.id]["task"].cancel()
		await info[ctx.guild.id]["voice"].disconnect()
		info.pop(ctx.guild.id)

		embed=discord.Embed(title = language[lang_set]['ui']['field']['stopped'], description = f"", color=snoo_color)
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['stopped'].upper()}", icon_url=music_icon)
		await ctx.send(embed = embed)

@snoo.command()
async def queue(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		embed=discord.Embed(title = "", description = "", color=snoo_color)
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queue'].upper()}", icon_url=music_icon)
		
		songs = ""
		durations = ""
		early_break = False
		#channels = ""
		total_time = 0
		for video in info[ctx.guild.id]["queue"]:
			total_time += video_info[video]["secs_length"]

		for i in range(len(info[ctx.guild.id]["queue"])):
			if (i == 0):
				embed.add_field(name = f'<a:MusicBars:917119951603646505> {video_info[info[ctx.guild.id]["queue"][i]]["title"]}', value = video_info[info[ctx.guild.id]["queue"][i]]["channel_name"], inline = True)
				embed.add_field(name = '\u200b', value = '\u200b', inline = True)
				embed.add_field(name = format_time(video_info[info[ctx.guild.id]["queue"][i]]["secs_length"]), value = '\u200b', inline = True)
				embed.set_thumbnail(url=video_info[info[ctx.guild.id]["queue"][i]]["thumbnail"])
			else:
				#embed.add_field(name = f'{i} {video_info[info[ctx.guild.id]["queue"][i]]["title"]}', value = video_info[info[ctx.guild.id]["queue"][i]]["channel_name"], inline = True)
				#embed.add_field(name = '\u200b', value = '\u200b', inline = True)
				#embed.add_field(name = format_time(video_info[info[ctx.guild.id]["queue"][i]]["secs_length"]), value = '\u200b', inline = True)

				chr_per_row = 40
				if (len(songs) < 1024 - chr_per_row):
					songs += f"**{i}** " + video_info[info[ctx.guild.id]["queue"][i]]["title"][0 : chr_per_row]
					if (len(video_info[info[ctx.guild.id]["queue"][i]]["title"]) > chr_per_row):
						songs += "...\n"
					else:
						songs += "\n"
				else: 
					early_break = True
					embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["full"].format(len(info[ctx.guild.id]["queue"]) - i, format_time(total_time)))
					break

				#channels += video_info[info["queue"][i]]["channel_name"] + "\n"
				durations += format_time(video_info[info[ctx.guild.id]["queue"][i]]["secs_length"]) + "\n"

		if (songs != ""):
			embed.add_field(name = language[lang_set]["ui"]["field"]["next_up"], value = songs, inline=True)
			embed.add_field(name = language[lang_set]["ui"]["field"]["duration"], value = durations, inline=True)

		if (info[ctx.guild.id]["autoplay"]):
			embed.add_field(name = language[lang_set]["ui"]["field"]["autoplay"], value = video_info[info[ctx.guild.id]["recomended_vid"]]["title"], inline = False)

		if (not early_break):
			embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))
		
		await ctx.send(embed=embed)

@snoo.command()
async def skip(ctx):
	if (len(info[ctx.guild.id]["queue"]) > 1 or info[ctx.guild.id]["autoplay"]):
		await play_next(ctx.guild.id)
	else:
		await ctx.send(language[lang_set]["error"]["can_not_skip"])

@snoo.command()
async def back(ctx):
	if (len(info[ctx.guild.id]["past queue"]) >= 1):
		info[ctx.guild.id]["queue"].insert(1, info[ctx.guild.id]["past queue"][-1])
		await play_next(ctx.guild.id)
		del info[ctx.guild.id]["past queue"][-2:]
	else:
		await ctx.send(language[lang_set]["error"]["can_not_back"])

async def check_if_song_ended(guild):
	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	if (time_since_start.seconds + 1 < video_info[info[guild]["queue"][0]]["secs_length"]):
		return False

	if (len(info[guild]["queue"]) > 1 or info[guild]["looping"] or info[guild]["autoplay"]):
		await play_next(guild)
	else:
		await info[guild]["voice"].disconnect()
		info[guild]["task"].cancel()

		embed=discord.Embed(title = language[lang_set]["ui"]["field"]["queue_end"], description = "", color=snoo_color)
		embed.set_author(name = f'||  {language[lang_set]["ui"]["title"]["queue_end"].upper()}', icon_url=music_icon)
		await info[guild]["channel"].send(embed=embed)

		info[guild]["queue"].clear()
	return True

@snoo.command()
async def loop(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (info[ctx.guild.id]["looping"]):
			info[ctx.guild.id]["looping"] = False
			await ctx.send(language[lang_set]["notifs"]["loop_stop"])
		else:
			info[ctx.guild.id]["looping"] = True
			await ctx.send(language[lang_set]["notifs"]["loop_start"])

@snoo.command()
async def autoplay(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (info[ctx.guild.id]["autoplay"]):
			info[ctx.guild.id]["autoplay"] = False
			await ctx.send(language[lang_set]["notifs"]["autoplay_stop"])
		else:
			info[ctx.guild.id]["autoplay"] = True
			await ctx.send(language[lang_set]["notifs"]["autoplay_start"])

"""@snoo.command()
async def shuffle(ctx):
	if (info["voice"].is_playing()):
		nowplaying = info["queue"][0]
		info["queue"].remove(info["queue"][0])

		random.shuffle(info["queue"])

		info["queue"].insert(0, nowplaying)
		await ctx.send("I have shuffled the current queue!")"""

# _________________________________________________________________ DEBUGING _________________________________________________________________

"""@snoo.command()
async def ping(ctx):
	delay_time = datetime.datetime.now() - ctx.message.created_at
	delay_ms = delay_time.total_seconds() * 1000
	delay_ms = round(delay_ms, 2)
	await ctx.send(str(delay_ms) + "ms")"""

# _________________________________________________________________ SYSTEM _________________________________________________________________

def valid_url(uri: str) -> bool:
    try:
        with requests.get(uri, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                return False
    except requests.exceptions.ConnectionError:
        return False

def verify_yt_id(video_id: str):
    checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
    video_url = checker_url + video_id

    request = requests.get(video_url)

    return request.status_code == 200

def yt_id(url):
	query = urlparse(url)
	if query.hostname == 'youtu.be': return query.path[1:]
	if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
		with suppress(KeyError):
			return parse_qs(query.query)['list'][0]
		if query.path == '/watch': return parse_qs(query.query)['v'][0]
		if query.path[:7] == '/watch/': return query.path.split('/')[1]
		if query.path[:7] == '/embed/': return query.path.split('/')[2]
		if query.path[:3] == '/v/': return query.path.split('/')[2]
	return url

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

def find_url(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)      
    return [x[0] for x in url]

def str_json(string):
	with open("Cache/string.json", "w") as outfile:
		json.dump(string, outfile)

@snoo.command()
async def history(ctx):
	if (ctx.message.author.id == 401442600931950592):
		best_videos = {}
		for day in range(len(song_history[ctx.guild.id][ctx.message.author.id])):
			for video in song_history[ctx.guild.id][ctx.message.author.id][day]:
				for watch_id in range(len(song_history[ctx.guild.id][ctx.message.author.id][day][video])):
					if video in best_videos:
						best_videos[video] += song_history[ctx.guild.id][ctx.message.author.id][day][video][watch_id]["retention"]
						best_videos[video] = round(best_videos[video], 2)
					else:
						best_videos[video] = song_history[ctx.guild.id][ctx.message.author.id][day][video][watch_id]["retention"]
		sorted_videos = dict(sorted(best_videos.items(), key = lambda item: item[1], reverse = True))
		first_ten = list(sorted_videos)[:10]
		shuffle(first_ten)
		await ctx.send(first_ten)
	else:
		await ctx.send(admin_command_message)

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

	channel = snoo.get_channel(977316868253708359)
	with open("Data Files/profile.json", "w") as outfile:
		json.dump(profile_data, outfile)
	await channel.send(file=discord.File("Data Files/profile.json"))

	channel = snoo.get_channel(913524223870398534)
	with open("Data Files/channel_messages.json", "w") as outfile:
		json.dump(channel_messages, outfile)
	await channel.send(file=discord.File("Data Files/channel_messages.json"))

	channel = snoo.get_channel(985597229022724136)
	with open("Data Files/server_config.json", "w") as outfile:
		json.dump(server_config, outfile)
	await channel.send(file=discord.File("Data Files/server_config.json"))

	channel = snoo.get_channel(922592622248341505)
	with open("Data Files/song_history.json", "w") as outfile:
		json.dump(song_history, outfile)
	await channel.send(file=discord.File("Data Files/song_history.json"))

	channel = snoo.get_channel(993332319454760960)
	with open("Data Files/video_info.json", "w") as outfile:
		json.dump(video_info, outfile)
	await channel.send(file=discord.File("Data Files/video_info.json"))

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