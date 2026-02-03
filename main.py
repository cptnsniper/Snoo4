import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord import FFmpegPCMAudio
from discord.ui import Select, Button, View
import os
import json
import datetime
from threading import Thread
import asyncio
from math import fsum, floor, ceil
from pandas import DataFrame
from cryptography.fernet import Fernet
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen, urlretrieve
from contextlib import suppress
from re import findall
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup as bs
from socket import gethostname
from requests import get as r_get
from requests import exceptions
from plotly.express import line as px_line
from difflib import SequenceMatcher 
from copy import deepcopy
from random import shuffle
from pytube import YouTube, Playlist
from validators import url
import queue
from logging import FileHandler
from PIL import Image
from extcolors import extract_from_path
import sys

from System.system import *

import shutil
if shutil.which("ffmpeg") is None:
	print("CRITICAL ERROR: ffmpeg was not found in your system PATH. Music will not work.")
else:
	print(f"FFmpeg found at: {shutil.which('ffmpeg')}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True
intents.voice_states = True

snoo = commands.Bot(command_prefix = prefix, intents = intents)

if (not os.path.isdir('Data Files')):
	os.makedirs("Data Files")
if (not os.path.isdir('Cache')): 
	os.makedirs("Cache")

@snoo.event
async def on_ready():
	print(f'we have logged in as {snoo.user}')
	await snoo.tree.sync()#guild = discord.Object(test_server))
	# snoo.tree.clear_commands(guild=None)
	# await snoo.tree.sync()
	await snoo.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "music (possibly)"))

	await initialize_data()
	verify_lang()
	print("imported data")
	str_json(missing_translations)
	#await channel.send(file=discord.File('Cache/string.json'))
	asyncio.create_task(async_timer(60 * 6, new_save)) #PLEASE FUTURE ME REMMEBER TO UNCOMMENT!!!!!!!!!

	if not daily_entry_check.is_running():
		daily_entry_check.start()

	channel = snoo.get_channel(test_channel)
	await channel.send(f"running version: {version} on {gethostname()}")

async def initialize_data():
	global language
	global video_info
	global playlists

	f = open('System/language.json', encoding='utf8')
	language = json.load(f)

	str_profile = await download_datafile(977316868253708359, "profile")
	str_messages = await download_datafile(913524223870398534, "channel_messages")
	str_history = await download_datafile(922592622248341505, "song_history")
	str_config = await download_datafile(985597229022724136, "server_config")
	str_playlists = await download_datafile(999117002323001354, "playlists")
	video_info = await download_datafile(993332319454760960, "video_info")

	#convert dictionarys to int:
	dict_str_to_int(str_profile, profile_data)
	dict_str_to_int(str_messages, channel_messages)
	dict_str_to_int(str_history, song_history)
	dict_str_to_int(str_config, server_config, True)
	dict_str_to_int(str_playlists, playlists, True)

@snoo.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		print("command not recognized")
		return
	raise error

# _________________________________________________________________ ON MESSAGE _________________________________________________________________

@snoo.event
async def on_message(message: discord.Message):
	# Ignore DMs
	if message.guild is None:
		return

	# Ensure guild + channel dicts exist
	if message.guild.id not in channel_messages:
		channel_messages[message.guild.id] = {}

	if message.channel.id not in channel_messages[message.guild.id]:
		channel_messages[message.guild.id][message.channel.id] = [1]
	else:
		channel_messages[message.guild.id][message.channel.id][-1] += 1

	# Track profile data
	verify_data(message.guild.id, message.author.id)
	profile_data[message.guild.id][message.author.id]["messages"][-1] += 1

	# Ignore self
	if message.author == snoo.user:
		return

	verify_settings(message.guild.id)

	# Voting / image reactions
	if server_config[message.guild.id]["votes"]:
		if message.attachments or len(find_url(message.content)) > 0 or '*image*' in message.content.lower():
			upvote = None
			downvote = None

			for emoji in message.channel.guild.emojis:
				if emoji.name.lower() == "upvote":
					upvote = emoji
					if not server_config[message.guild.id]["downvote"]:
						break
				if emoji.name.lower() == "downvote":
					downvote = emoji
				if upvote is not None and downvote is not None:
					break

			if upvote is None:
				await message.add_reaction(emojis["upvote"])
			else:
				await message.add_reaction(upvote)

			if server_config[message.guild.id]["downvote"]:
				if downvote is None:
					await message.add_reaction(emojis["downvote"])
				else:
					await message.add_reaction(downvote)

	# %%scale reactions
	if message.content.lower().startswith('%'):
		if 'scale' in message.content.lower():
			for num in emojis["numbers"]:
				await message.add_reaction(num)
		else:
			await message.add_reaction(emojis["cross"])
			await message.add_reaction(emojis["check"])

	# Let commands still work
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

def settings_embed(guild):
	embed = discord.Embed(colour=snoo_color)
	embed.set_author(name = title_format.format(language[server_config[guild]['lang_set']]['ui']['title']['settings'].title()), icon_url = settings_icon)

	embed.add_field(name = language[server_config[guild]["lang_set"]]["setting_names"]["language"].title(), value = language[server_config[guild]["lang_set"]]["settings_info"]["language"], inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = f'{language[server_config[guild]["lang_set"]]["flag"]} {server_config[guild]["lang_set"]}', value = "\u200b", inline = True)

	view = View(timeout = None)

	langs = []
	for lang in language:
		langs.append(discord.SelectOption(label = lang, emoji = language[lang]["flag"], default = lang == server_config[guild]["lang_set"]))

	select = Select(placeholder = language[server_config[guild]["lang_set"]]["ui"]["field"]["select_language"], options = langs)
	
	async def change_lang(interaction):
		server_config[guild]["lang_set"] = select.values[0]
		embeds = settings_embed(interaction.guild.id)
		await interaction.message.edit(embed = embeds[0], view = embeds[1])
		await interaction.response.defer()
	
	select.callback = change_lang

	view.add_item(select)

	for config in server_config[guild]:
		if (settings_info[config]["dev"]):
			continue
		embed.add_field(name = language[server_config[guild]["lang_set"]]["setting_names"][config].title(), value = language[server_config[guild]["lang_set"]]["settings_info"][config], inline = True)
		embed.add_field(name = '\u200b', value = '\u200b', inline = True)
		if (server_config[guild][config]):
			embed.add_field(name = emojis["on"], value = "\u200b", inline = True)
		else:
			embed.add_field(name = emojis["off"], value = "\u200b", inline = True)

		button = Button(label = language[server_config[guild]["lang_set"]]["setting_names"][config].title())
		button.custom_id = config
		button.callback = button_config
		view.add_item(button)

	return (embed, view)

@snoo.command()
async def settings(ctx):
	verify_settings(ctx.guild.id)
	embeds = settings_embed(ctx.guild.id)
	await ctx.send(embed = embeds[0], view = embeds[1])

async def button_config(interaction):
	setting = interaction.data["custom_id"]
	if (setting != None):
		setting = setting.lower()
		if (setting in server_config[interaction.guild.id]):
			if (server_config[interaction.guild.id][setting]):
				server_config[interaction.guild.id][setting] = False
			else:
				server_config[interaction.guild.id][setting] = True
			
			embeds = settings_embed(interaction.guild.id)
			await interaction.message.edit(embed = embeds[0], view = embeds[1])
			await interaction.response.defer()
		else:
			await interaction.response.send_message(language[server_config[interaction.guild.id]["lang_set"]]["error"]["setting_not_found"])

@snoo.command()
async def poll(ctx, name, *, opts):
	verify_settings(ctx.guild.id)
	opts_list = opts.split(',')

	embed = discord.Embed(title = name, colour = snoo_color)
	embed.set_author(name = title_format.format(language[server_config[ctx.guild.id]['lang_set']]['ui']['title']['poll'].title()), icon_url = poll_icon)

	for i in range(len(opts_list)):
		embed.add_field(name = f"{language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['option'].title()}  {emojis['poll'][i]}", value = opts_list[i], inline=False)

		if (i >= 6):
			break

	poll = await ctx.send(embed=embed)

	for i in range(len(opts_list)):
		await poll.add_reaction(emojis["poll"][i])

		if (i >= 6):
			break

@snoo.command()
async def user(ctx, *, user: discord.User):
	username = await snoo.fetch_user(user.id)
	await ctx.send(username)

@snoo.command()
async def say(ctx, *, args):
	if (ctx.message.author.id == admin):
		await ctx.message.delete()
		await ctx.send(args)

#display information
@snoo.command()
async def profile(ctx, *, user: discord.User = 0):
	verify_settings(ctx.guild.id)
	if (user == 0):
		user_id = ctx.message.author.id
	else:
		user_id = user.id

	user = await snoo.fetch_user(user_id)
	print(user)
	split_user = str(user).split("#", 1)
	username = split_user[0]

	verify_data(ctx.guild.id, user_id)

	embed = discord.Embed(colour = snoo_color)

	embed.set_author(name = title_format.format(language[server_config[ctx.guild.id]['lang_set']]['ui']['title']['profile'].title().format(username)), icon_url = profile_icon)

	embed.add_field(name = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['karma']['title'].title(), value = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['karma']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['karma'])), inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['friendship']['title'].title(), value = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['friendship']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['friendship'])), inline = True)
	embed.add_field(name = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['messages']['title'].title(), value = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['messages']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['messages'])), inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['vc_hours']['title'].title(), value = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['vc_hours']['desc'].format(fsum(profile_data[ctx.guild.id][user_id]['vc_time'])), inline = True)
	
	await ctx.send(embed = embed)

@snoo.command()
async def graph(ctx, type, *, data: discord.User):
	#if (type(data) == discord.TextChannel):
	#	df = pd.DataFrame(channel_messages[ctx.guild.id][data.id], columns = ['Messages'])
	#else:
	df = DataFrame(profile_data[ctx.guild.id][data.id][type], columns = [type])
	message = await ctx.send(f"Graphing {loading_icon}")

	#layout = Layout(plot_bgcolor='rgb(47,49,54)')

	fig = px_line(df, markers=False, template = "seaborn")
	fig['data'][0]['line']['color']="#FF4400"
	#fig.update_layout(paper_bgcolor="#2f3136")
	fig.write_image("Cache/graph.png")

	#plt.savefig("graph.png")
	await message.delete()
	await ctx.send(file=discord.File('Cache/graph.png'))

	#plt.clf()
	#os.remove("graph.png")

@snoo.command()
async def playlist(ctx, *, playlist = None):
	verify_settings(ctx.guild.id)
	print(playlists[ctx.guild.id])
	if (playlist in playlists[ctx.guild.id]):
		embed = discord.Embed(title = playlists[ctx.guild.id][playlist]["title"], description = playlists[ctx.guild.id][playlist]["desc"], color = snoo_color)
		embed.set_author(name = title_format.format(language[server_config[ctx.guild.id]['lang_set']]['ui']['title']['playlist'].title()), icon_url=music_icon)
		embed.set_thumbnail(url = playlists[ctx.guild.id][playlist]["cover"])
		for song in playlists[ctx.guild.id][playlist]["songs"]:
			embed.add_field(name = video_info[song]["title"], value = video_info[song]["channel_name"], inline = True)
			embed.add_field(name = '\u200b', value = '\u200b', inline = True)
			embed.add_field(name = format_time(video_info[song]["secs_length"]), value = "\u200b", inline = True)
		await ctx.send(embed = embed)

# _________________________________________________________________ MUSIC _________________________________________________________________

async def join_or_move_to_channel(guild, channel):
	if info[guild]["voice"] and info[guild]["voice"].is_connected():
		await info[guild]["voice"].move_to(channel)
	else:
		info[guild]["voice"] = await channel.connect()

@snoo.command()
async def find_playlist(ctx, playlist):
	await ctx.send(find_videos_playlist(playlist))

def find_videos_playlist(playlist_url):
	linklist = []
	playlist = []

	try:
		playlist_info = Playlist(playlist_url)
		linklist = playlist_info.video_urls
	except:
		print("failed to fetch playlist info for: ", playlist_url)

	for link in linklist:
		playlist.append(yt_id(link))
	
	return playlist

def thumbnail_palette(thumbnail, discriminator = ""):
	img_path = os.path.join("Cache", f"img{discriminator}.png")

	urlretrieve(thumbnail, img_path)

	output_width = 300
	img = Image.open(img_path)
	wpercent = (output_width/float(img.size[0]))
	hsize = int((float(img.size[1])*float(wpercent)))
	img = img.resize((output_width, hsize), Image.Resampling.LANCZOS)
	img.save(img_path)

	color_pallet = extract_from_path(img_path, tolerance = 16, limit = 3)
	return (color_pallet[0][0][0], color_pallet[0][1][0], color_pallet[0][2][0])



def find_video_info(id, only_source: bool = False, only_rec: bool = False, refetch: bool = False, discriminator: str = ""):
	"""
	Improved video info fetcher:
	- Uses yt_dlp for metadata + primary audio URL
	- Falls back to pytube for tricky videos whose streams break
	- Avoids slow/blocking HTTP checks
	"""
	# Fast path: reuse cached info when not forcing refresh
	if id in video_info and not (refetch or only_source or only_rec):
		info_block = video_info[id].get("info", {})
		cache_str = info_block.get("cache_date")
		if cache_str and len(cache_str) == 8:
			try:
				cache_date = datetime.datetime(
					int(cache_str[0:4]),
					int(cache_str[4:6]),
					int(cache_str[6:8]),
				)
				time_delta = datetime.datetime.now() - cache_date
				# Convert days to seconds + seconds to check if it's less than 4 hours (14400 seconds)
				if time_delta.total_seconds() < 14400 and not info_block.get("failed_thumbnail") and not info_block.get("failed_palette"):
					return True
			except Exception:
				# If cache parsing fails, just refetch.
				pass

	print(f"finding info for: {id}")

	YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
	vid = None
	try:
		with YoutubeDL(YDL_OPTIONS) as ydl:
			vid = ydl.extract_info(id, download=False)
	except Exception as e:
		print(f"failed to fetch video info via yt_dlp for {id}: {e!r}")

	audio_url = None

	if vid:
		# Primary audio URL from yt_dlp
		audio_url = vid.get("url")
		if not audio_url:
			formats = vid.get("formats") or []
			audio_candidates = [
				f for f in formats
				if f.get("acodec") not in (None, "none") and (f.get("vcodec") in (None, "none"))
			]
			if audio_candidates:
				best = max(audio_candidates, key=lambda f: f.get("abr") or f.get("tbr") or 0)
				audio_url = best.get("url")

	# Fallback to pytube for stubborn videos or when yt_dlp didn't give us a clean URL
	# if not audio_url or not url(str(audio_url)):
	# 	try:
	# 		from pytube import YouTube
	# 		yt = YouTube(f'https://www.youtube.com/watch?v={id}')
	# 		stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
	# 		if stream and stream.url:
	# 			audio_url = stream.url
	# 			print("pytube fallback succeeded for", id)
	# 	except Exception as e:
	# 		print(f"pytube fallback failed for {id}: {e!r}")

	if not audio_url:
		print(f"no usable audio URL for {id}")
		return False

	# If the caller only needs a refreshed source URL, update and return quickly.
	if only_source and id in video_info:
		video_info[id]["source"] = audio_url
		return True

	# If we only care about related videos, we can skip most metadata work
	if only_rec and vid is None:
		# Can't infer recommendations without a base info dict
		return False

	video_info_temp = {}
	video_info_temp["source"] = audio_url

	if vid is None:
		# Minimal metadata if yt_dlp completely failed but pytube succeeded
		video_info_temp["title"] = "Unknown title"
		video_info_temp["views"] = 0
		video_info_temp["secs_length"] = 0
		video_info_temp["publish_date"] = datetime.datetime.now().strftime("%Y%m%d")
		video_info_temp["channel_link"] = "https://www.youtube.com"
		video_info_temp["channel_name"] = "Unknown channel"
		thumb = None
		related_ids = []
	else:
		video_info_temp["title"] = vid.get("title") or "Unknown title"
		video_info_temp["views"] = vid.get("view_count", 0)
		video_info_temp["secs_length"] = int(vid.get("duration") or 0)
		video_info_temp["publish_date"] = vid.get("upload_date") or datetime.datetime.now().strftime("%Y%m%d")
		video_info_temp["channel_link"] = vid.get("uploader_url") or vid.get("channel_url") or "https://www.youtube.com"
		video_info_temp["channel_name"] = vid.get("uploader") or vid.get("channel") or "Unknown channel"
		thumb = vid.get("thumbnail")
		related_ids = vid.get("related_ids") or []

	# Thumbnail & palette (trust yt_dlp / pytube, avoid HTTP probes here)
	failed_thumbnail = False
	failed_palette = False

	if thumb:
		video_info_temp["thumbnail"] = thumb
	else:
		failed_thumbnail = True
		video_info_temp["thumbnail"] = thumbnail_error

	try:
		if failed_thumbnail:
			raise Exception("no thumbnail to build palette from")
		video_info_temp["palette"] = thumbnail_palette(video_info_temp["thumbnail"], discriminator)
	except Exception:
		failed_palette = True
		video_info_temp["palette"] = default_palette

	# Recommended videos / autoplay – best-effort only.
	recomended_vids = []

	for v in related_ids:
		if isinstance(v, str):
			recomended_vids.append(v)

	# Some builds expose related_videos instead/also
	if vid is not None and not recomended_vids and isinstance(vid.get("related_videos"), list):
		for rel in vid["related_videos"]:
			vid_id = rel.get("id") or rel.get("url")
			if isinstance(vid_id, str):
				recomended_vids.append(vid_id[-11:])

	video_info_temp["recomended_vids"] = recomended_vids

	video_info[id] = video_info_temp
	video_info[id]["info"] = {}
	video_info[id]["info"]["cache_date"] = datetime.datetime.now().strftime("%Y%m%d")
	video_info[id]["info"]["failed_thumbnail"] = failed_thumbnail
	video_info[id]["info"]["failed_palette"] = failed_palette
	video_info[id]["info"]["failed_autoplay"] = False if recomended_vids else True

	return True


def search_yt(search):
	query_string = urlencode({'search_query' : search})
	html_content = urlopen('http://www.youtube.com/results?' + query_string)
	search_results = findall(r"watch\?v=(\S{11})", html_content.read().decode())

	if (len(search_results) > 0):
		return search_results[0]
	else:
		return True

def search_and_find_info(search, discriminator = ""):
	if (not verify_yt_id(search)):
		result = search_yt(search)
		if (result == None):
			return None
	else:
		result = search
	
		if (not find_video_info(result, discriminator = discriminator)):
			return None
	
	return result

def find_playlist_index(queue, thread):
	while True:
		queue_index = queue.get()
		playlist = queue_index[0]
		index = queue_index[1]
		playlist[index] = search_and_find_info(playlist[index], thread)
		queue.task_done()
		print(f"thread #{thread}: queued index #{index}")

q = queue.Queue()

def thread_find_playlist(playlist):
	for i in range(10):
		Thread(target = find_playlist_index, args = (q, i), daemon = True).start()

	playlist[-1] = yt_id(playlist[-1])
	q.put((playlist, -1))

	for i in range(len(playlist) - 1):
		playlist[i] = yt_id(playlist[i])
		q.put((playlist, i))

	q.join()

async def filter_url(reference, channel, search):
	verify_settings(channel.guild.id)
	if (reference is None):
		if (url(search) and "youtube" in search and "list=" in search):
			return (search, None, find_videos_playlist(search))
		elif (verify_yt_id(yt_id(search))):
			return (search, yt_id(search), None)
	else:
		try:
			message_reference = await channel.fetch_message(reference.message_id)
		except:
			message_reference = reference
		if (len(find_url(message_reference.content)) > 0):
			temp_url = find_url(message_reference.content)[0]
			if ("youtube" in temp_url and "list=" in temp_url):
				return (search, None, find_videos_playlist(temp_url))
			elif (verify_yt_id(yt_id(temp_url))):
				return (search, yt_id(temp_url), None)
			else:
				return (message_reference.content, None, None)
		else:
			if (len(message_reference.embeds) > 0): 
				if (str(message_reference.embeds[0].url) != "Embed.Empty"):
					temp_url = message_reference.embeds[0].url
					if (verify_yt_id(yt_id(temp_url))):
						return (search, yt_id(temp_url), None)
					else:
						await channel.send(language[server_config[channel.guild.id]["lang_set"]]["error"]["not_youtube"])
						return
				else:		
					await channel.send(language[server_config[channel.guild.id]["lang_set"]]["error"]["no_content"])
					return
			elif (message_reference.content == ""):
				await channel.send(language[server_config[channel.guild.id]["lang_set"]]["error"]["no_content"])
				return
			else:
				return (message_reference.content, None, None)

	return (search, None, None)

def search_to_playlist(search):
	if (search[0] == "[" and search[-1] == "]"):
		return search.strip('][').split(', ')
	elif (search in playlists):
		return playlists[search]["songs"]
	return None

@snoo.tree.context_menu(name = "play")#, guild = discord.Object(id = test_server))
async def play_menu(interaction: discord.Interaction, message: discord.Message):
	await interaction.response.defer(ephemeral = True)
	try:
		await play_sys(interaction.guild, interaction.channel, message, interaction.user)
		await interaction.followup.send("interaction successful")
	except Exception as e:
		await interaction.followup.send("sorry, something went wrong")
		raise e

@snoo.command()
async def play(ctx, *, search = None):
	await play_sys(ctx.guild, ctx.channel, ctx.message.reference, ctx.message.author, search)

async def play_sys(guild = None, channel = None, reference = None, user = None, search = None, autoplay = None):
	verify_settings(guild.id)
	skip_search = False
	playlist = None
	searching_msg = None
	id = None
	searching = f'{language[server_config[guild.id]["lang_set"]]["notifs"]["searching"]}   {loading_icon}'

	if (autoplay == None):
		if (guild.id not in playlists or "liked" not in playlists[guild.id]):
			playlists[guild.id]["liked"] = []

		if (guild.id not in info):
			info[guild.id] = deepcopy(default_info)
			info[guild.id]["channel"] = channel
			info[guild.id]["voice"] = get(snoo.voice_clients, guild = guild)
		
		if (type(user.voice) == type(None)):
			await channel.send(language[server_config[guild.id]["lang_set"]]["error"]["no_vc"])
			return

		filtered_info = await filter_url(reference, channel, search)
		search = filtered_info[0]
		id = filtered_info[1]
		playlist = filtered_info[2]

		if (id == None):
			if (playlist == None):
				playlist = search_to_playlist(search)

			if (playlist != None):
				if (len(info[guild.id]["queue"]) < 1):
					search = playlist[0]
					playlist = playlist[1:]
				else:
					skip_search = True

			if (not skip_search):
				searching_msg = await channel.send(searching.format(search))
				id = search_and_find_info(search)
				if (id == None):
					await searching_msg.edit(content = language[server_config[guild.id]["lang_set"]]["error"]["nothing_found"])
					return
	else:
		id = autoplay

	if (not skip_search):
		found_info = find_video_info(id)

		print("playing: " + id)
		if (not valid_url(video_info[id]["source"])):
			print("url expired")
			found_info = find_video_info(id, only_source = True)

		if (not found_info):
			if (searching_msg != None):
				await searching_msg.edit(content = language[server_config[guild.id]["lang_set"]]["error"]["play_error"])
			else:
				await channel.send(language[server_config[guild.id]["lang_set"]]["error"]["play_error"])
			return		

		info[guild.id]["queue"].append(id)
		info[guild.id]["refetch_tried"] = False

		if (autoplay == None):
			if (len(info[guild.id]["queue"]) <= 1):
				await join_or_move_to_channel(guild.id, user.voice.channel)
				await play_url(guild.id, id)

				embeds = nowplaying_embed(guild.id, info[guild.id]["queue"][0])
				# if (server_config[guild.id]["large nowplaying thumbnail"]):
				info[guild.id]["thumbnail"] = await channel.send(embed = embeds[1])
				info[guild.id]["nowplaying"] = await channel.send(embed = embeds[0])#, view = embeds[2])
				info[guild.id]["button_holder"] = await channel.send(embed = embeds[3], view = embeds[2])

				if (searching_msg != None):
					await searching_msg.delete()

				info[guild.id]["nowplaying_edits"] = 0
				info[guild.id]["nowplaying_buffer"] = False
				info[guild.id]["task"] = asyncio.create_task(async_timer(1, update_nowplaying, guild.id))
			else:
				embed = small_queued_embed(guild, id)

				if (searching_msg != None):
					await searching_msg.edit(content="", embed = embed)
				else:
					print("there was no message to edit and snoo was unable to edit a conformation embed")
					await channel.send(embed = embed)
		else:
			await play_url(guild.id, id)

		# Thread(target = find_autoplay, args = (guild.id, id, )).start()
		find_autoplay(guild.id, id)

	if (playlist != None and len(playlist) > 0):
		Thread(target = thread_find_playlist, args = (playlist, )).start()
		await queued_embed(channel, playlist)

async def play_url(guild, id):
    # 1. Check if the voice client exists and is actually connected
    if guild not in info or "voice" not in info[guild]:
        print("Play URL failed: No voice client in info dict.")
        return

    vc = info[guild]["voice"]

    # 2. If we are not connected, try to reconnect to the last known channel
    if not vc.is_connected():
        print("Voice client is disconnected. Attempting to reconnect...")
        try:
            # Try to grab the channel the bot *was* in
            channel = vc.channel
            # If the bot object doesn't know its channel, we can't rejoin
            if channel:
                # Cleanup the dead connection
                try:
                    await vc.disconnect(force=True)
                except Exception:
                    pass
                
                # Reconnect and update the info dict
                new_vc = await channel.connect()
                info[guild]["voice"] = new_vc
                vc = new_vc
                print("Reconnection successful.")
            else:
                print("Could not reconnect: Last channel is unknown.")
                return
        except Exception as e:
            print(f"Failed to reconnect: {e}")
            return

    # 3. Stop any currently playing audio
    if vc.is_playing():
        vc.stop()

    # 4. Define FFMPEG options (Updated to be more robust)
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
        'options': '-vn'
    }

    # 5. Play the audio with error logging
    # Set the start time BEFORE trying to play. 
    # This ensures the key exists even if FFMPEG crashes.
    info[guild]["start_time"] = datetime.datetime.now() 

    print(f"Attempting to play Source URL: {video_info[id]['source']}")
    try:
        source = FFmpegPCMAudio(
            source=video_info[id]["source"], 
            stderr=sys.stderr, 
            **FFMPEG_OPTIONS
        )
        vc.play(source)
        # info[guild]["start_time"] = datetime.datetime.now()  <-- REMOVE THIS LINE from here
    except Exception as e:
        print(f"CRITICAL FFMPEG ERROR: {e}")
        import traceback
        traceback.print_exc()

    # 6. Pre-fetch recommendations (Background Task)
    if "recomended_vids" not in video_info[id]:
        # Using a thread/task here avoids blocking the play function
        asyncio.create_task(async_find_rec(id, guild))
    else:
        # If we already have recs, verify the next one works
        verify_autoplay(guild, id)

# Helper wrapper to avoid async errors in the main flow
async def async_find_rec(id, guild):
    find_video_info(id, only_rec=True)
    verify_autoplay(guild, id)

def verify_autoplay(guild, id):
    for vid in video_info[id].get("recomended_vids", []):
        if vid not in info[guild]["past queue"]:
            if not find_video_info(vid):
                continue
            info[guild]["recomended_vid"] = vid
            print("autoplay set to: " + vid)
            break

async def queued_embed(channel, playlist):
	verify_settings(channel.guild.id)
	edit_needed = False
	i = 0
	total_time = 0

	embed = discord.Embed(color = snoo_color)
	embed.set_author(name = title_format.format(f"{language[server_config[channel.guild.id]['lang_set']]['ui']['title']['queued'].title()} {0} / {len(playlist)}"), icon_url = music_icon)
	embed_msg = await channel.send(embed = embed)

	while (i < len(playlist)):
		if (playlist[i] in video_info):
			info[embed_msg.guild.id]["queue"].append(playlist[i])
			total_time += video_info[playlist[i]]["secs_length"]
			if (i == 0):
				color0 = discord.Color.from_rgb(video_info[playlist[0]]["palette"][0][0], video_info[playlist[0]]["palette"][0][1], video_info[playlist[0]]["palette"][0][2])
				embed = discord.Embed(color = color0)
				embed.set_author(name = title_format.format(f"{language[server_config[channel.guild.id]['lang_set']]['ui']['title']['queued'].title()} {0} / {len(playlist)}"), icon_url = music_icon)
				embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
			if (i < 25):
				embed.add_field(name = f'**{i + 1}** {video_info[playlist[i]]["title"]}', value = video_info[playlist[i]]["channel_name"], inline = False)
			else:
				embed.set_footer(text = language[server_config[channel.guild.id]['lang_set']]["ui"]["field"]["queue_footer"]["full"].format(i - 24, format_time(total_time)))

			if (edit_needed):
				if (i == 0):
					embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
				embed.set_author(name = title_format.format(f"{language[server_config[channel.guild.id]['lang_set']]['ui']['title']['queued'].title()} {0} / {len(playlist)} {i + 1} / {len(playlist)}"), icon_url = music_icon)
				
				await embed_msg.edit(embed = embed)
				edit_needed = False
			
			i += 1
		elif (playlist[i] == None):
			i += 1
		else:
			edit_needed = True

	embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
	embed.set_author(name = title_format.format(language[server_config[channel.guild.id]['lang_set']]['ui']['title']['queued'].upper()), icon_url = music_icon)
	if (len(playlist) < 25):
		embed.set_footer(text = language[server_config[channel.guild.id]['lang_set']]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))
	if (embed_msg == None):
		embed_msg = await embed_msg.send(embed = embed)
	else:
		await embed_msg.edit(embed = embed)

	find_autoplay(embed_msg.guild.id, playlist[-1])

def find_autoplay(guild, id):
	if ("recomended_vids" not in video_info[id]):
		find_video_info(id, only_rec = True)

	for vid in video_info[id]["recomended_vids"]:
		if (vid not in info[guild]["past queue"]):
			if (not find_video_info(vid)):
				continue
			info[guild]["recomended_vid"] = vid
			print("autoplay: " + vid)
			break

def small_queued_embed(guild, id):
	verify_settings(guild)
	color0 = discord.Color.from_rgb(video_info[id]["palette"][0][0], video_info[id]["palette"][0][1], video_info[id]["palette"][0][2])
	embed = discord.Embed(title = video_info[id]["title"], url = 'http://www.youtube.com/watch?v=' + id, description = f'[{video_info[id]["channel_name"]}]({video_info[id]["channel_link"]})', color = color0)
	embed.set_thumbnail(url = video_info[id]["thumbnail"])
	embed.set_author(name = title_format.format(language[server_config[guild]['lang_set']]['ui']['title']['queued'].title()), icon_url = music_icon)
	return embed

@snoo.command()
async def nowplaying_bar_test(ctx):
	playbar_length = 18
	for i in range(10):
		playbar = ""
		for j in range(3):
			percent = (i * 3 + j) / 29
			playbar += nowplaying_bar(playbar_length, percent)
			playbar += f" {round(percent * playbar_length, 2)} \n"
		await ctx.send(playbar)

def nowplaying_bar(playbar_length, percent):
	playbar = ""
	taken_up_fills = 1
	taken_up_empty = 2

	segments_present = percent * playbar_length
	focus_snap_points = len(emojis["playbar"]["focus_bars"]["body"])
	focus_bar_percent = floor((segments_present % 1) * 0.999 * focus_snap_points)

	if (segments_present > 1 + 1 / focus_snap_points):
		playbar += emojis["playbar"]["fills_and_caps"][0]
		taken_up_fills += 1
	
	if (1 - 1 / focus_snap_points < segments_present < 1 + 1 / focus_snap_points):
		if (segments_present < 1):
			taken_up_empty += 1
		else:
			taken_up_fills += 1

	if (1 - 1 / focus_snap_points < playbar_length - segments_present < 1 + 1 / focus_snap_points and playbar_length - segments_present < 1):
		taken_up_fills += 1
			

	if (segments_present > 1 and playbar_length - segments_present > 1):
		if (focus_bar_percent == 0):
			taken_up_fills += 1
		if (focus_bar_percent == focus_snap_points - 1):
			taken_up_empty += 1

	playbar += emojis["playbar"]["fills_and_caps"][2] * ceil(segments_present - taken_up_fills)

	if (segments_present < 1):
		playbar += emojis["playbar"]["focus_bars"]["cap_r"][focus_bar_percent]
	elif (segments_present < 1 + 1 / focus_snap_points):
		playbar += emojis["playbar"]["focus_bars"]["cap_r"][-1]

	elif (percent >= 1):
		playbar += emojis["playbar"]["focus_bars"]["cap_l"][-1]
	elif (playbar_length - segments_present < 1):
		playbar += emojis["playbar"]["focus_bars"]["cap_l"][focus_bar_percent]
	elif (playbar_length - segments_present < 1 + 1 / focus_snap_points):
		playbar += emojis["playbar"]["focus_bars"]["cap_l"][0]

	else:
		playbar += emojis["playbar"]["focus_bars"]["body"][focus_bar_percent]

	playbar += emojis["playbar"]["fills_and_caps"][3] * ceil(playbar_length - segments_present - taken_up_empty)

	if (playbar_length - segments_present > 1 + 1 / focus_snap_points):
		playbar += emojis["playbar"]["fills_and_caps"][1]

	return playbar

def nowplaying_embed(guild, id):
	verify_settings(guild)

	# Safety check: Get start_time, default to NOW if missing
	start_ts = info[guild].get("start_time", datetime.datetime.now())
	time_since_start = datetime.datetime.now() - start_ts
	playing_for = format_time(time_since_start.seconds)
	watch_percent = time_since_start.seconds / video_info[id]["secs_length"]

	playbar = f'{playing_for}   {nowplaying_bar(18, watch_percent)}   {format_time(video_info[id]["secs_length"])}'

	publish_date = str(video_info[id]["publish_date"])
	publish_date = datetime.datetime(int(publish_date[0:4]), int(publish_date[4:6]), int(publish_date[6:8]))
	publish_date_delta = datetime.datetime.now() - publish_date
	time_ago = publish_date.strftime("%b %d %Y")
	if (not info[guild]["show_queue"]):
		if (publish_date_delta.days >= 365):
			years = floor(publish_date_delta.days / 365)
			if (years == 1):
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['year']['singular']
			else:
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['year']['plural'].format(years)
		elif (publish_date_delta.days >= 30):
			months = floor(publish_date_delta.days / 30)
			if (months == 1):
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['month']['singular']
			else:
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['month']['plural'].format(months)
		elif (publish_date_delta.days > 0):
			days = publish_date_delta.days
			if (days == 1):
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['day']['singular']
			else:
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['day']['plural'].format(days)
		elif (floor(publish_date_delta / datetime.timedelta(hours = 1)) > 0):
			hours = floor(publish_date_delta / datetime.timedelta(hours = 1))
			if (hours == 1):
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['hours']['singular']
			else:
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['hour']['plural'].format(hours)
		else:
			minutes = floor(publish_date_delta / datetime.timedelta(minutes = 1))
			if (minutes == 1):
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['minute']['singular']
			elif (minutes < 1):
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['minute']['less_than']
			else:
				time_ago = language[server_config[guild]["lang_set"]]['ui']['field']['time_delta']['minute']['plural'].format(minutes)

	views = '{:,}'.format(video_info[id]['views'])
	if (not info[guild]["show_queue"]):
		if (video_info[id]['views'] > 1000000000):
			views = f"{round(video_info[id]['views'] / 1000000000)}{language[server_config[guild]['lang_set']]['ui']['field']['number_multiplier']['billion']}"
		elif (video_info[id]['views'] > 1000000):
			views = f"{round(video_info[id]['views'] / 1000000)}{language[server_config[guild]['lang_set']]['ui']['field']['number_multiplier']['million']}"
		elif (video_info[id]['views'] > 1000):
			views = f"{round(video_info[id]['views'] / 1000)}{language[server_config[guild]['lang_set']]['ui']['field']['number_multiplier']['thousand']}"

	color0 = discord.Color.from_rgb(video_info[id]["palette"][0][0], video_info[id]["palette"][0][1], video_info[id]["palette"][0][2])
	color1 = discord.Color.from_rgb(video_info[id]["palette"][1][0], video_info[id]["palette"][1][1], video_info[id]["palette"][1][2])
	color2 = discord.Color.from_rgb(video_info[id]["palette"][2][0], video_info[id]["palette"][2][1], video_info[id]["palette"][2][2])

	thumbnail_embed = discord.Embed(color = color0)
	thumbnail_embed.set_image(url=video_info[id]["thumbnail"])
	thumbnail_embed.set_author(name = title_format.format(language[server_config[guild]['lang_set']]['ui']['title']['nowplaying'].title()), icon_url=music_icon)
	embed = discord.Embed(title = video_info[id]["title"], url = 'http://www.youtube.com/watch?v=' + id, description = f'[{video_info[id]["channel_name"]}]({video_info[id]["channel_link"]})\n\n{playbar}', color=color1)
	button_embed = discord.Embed(description = f"{views} {language[server_config[guild]['lang_set']]['ui']['field']['views']} - {time_ago}", color = color2)

	if (info[guild]["show_queue"]):
		songs = ""
		durations = ""
		early_break = False
		total_time = 0
        
        # Safely get the recommended video (defaults to None if missing)
		rec_vid = info[guild].get("recomended_vid")

		for video in info[guild]["queue"]:
			total_time += video_info[video]["secs_length"]
        
        # Use the safe variable we created above
		if (rec_vid != None):
			total_time += video_info[rec_vid]["secs_length"]

		for i in range(len(info[guild]["queue"])):
			if (i == 0):
				continue
            
            # ... [keep your existing loop code for songs/durations] ...
            # (Just copy/paste your existing formatting loop here if you are replacing the whole block)
            # Shortened here for clarity:
			chr_per_row = 40
			if (len(songs) < 1024 - chr_per_row):
				songs += f"**{i}** " + video_info[info[guild]["queue"][i]]["title"][0 : chr_per_row]
				if (len(video_info[info[guild]["queue"][i]]["title"]) > chr_per_row):
					songs += "...\n"
				else:
					songs += "\n"
			else: 
				early_break = True
				button_embed.set_footer(text = language[server_config[guild]["lang_set"]]["ui"]["field"]["queue_footer"]["full"].format(len(info[guild]["queue"]) - i, format_time(total_time)))
				break

			durations += format_time(video_info[info[guild]["queue"][i]]["secs_length"]) + "\n"

		if (songs != ""):
			button_embed.add_field(name = language[server_config[guild]["lang_set"]]["ui"]["field"]["next_up"].title(), value = songs, inline=True)
			button_embed.add_field(name = language[server_config[guild]["lang_set"]]["ui"]["field"]["duration"].title(), value = durations, inline=True)

        # Update this check to use 'rec_vid' as well
		if (info[guild]["autoplay"] and rec_vid != None):
			button_embed.add_field(name = language[server_config[guild]["lang_set"]]["ui"]["field"]["autoplay"].title(), value = video_info[rec_vid]["title"], inline = False)

		if (not early_break):
			button_embed.set_footer(text = language[server_config[guild]["lang_set"]]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))

	view = View(timeout = None)

	emoji = emojis["not_like"]
	if (info[guild]["queue"][0] in playlists[guild]["liked"]):
		emoji = emojis["like"]
	button = Button(emoji = emoji)
	button.callback = like_button
	view.add_item(button)

	button = Button(emoji = emojis["back"])
	button.callback = back_button
	view.add_item(button)

	emoji = emojis["pause"]
	if (info[guild]["paused"]):
		emoji = emojis["play"]
	button = Button(emoji = emoji)
	button.callback = pause_button
	view.add_item(button)

	button = Button(emoji = emojis["skip"])
	button.callback = skip_button
	view.add_item(button)

	emoji = emojis["extend"]
	if (info[guild]["show_queue"]):
		emoji = emojis["collapse"]
	button = Button(emoji = emoji)
	button.callback = show_queue
	view.add_item(button)

	if (info[guild]["show_queue"]):
		button = Button(emoji = emojis["delete"])
		button.callback = stop_button
		view.add_item(button)

	return [embed, thumbnail_embed, view, button_embed]

@snoo.command()
async def nowplaying(ctx):
	embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
	# if (server_config[ctx.guild.id]["large nowplaying thumbnail"]):
	await info[ctx.guild.id]["thumbnail"].delete()
	info[ctx.guild.id]["thumbnail"] = await ctx.send(embed = embeds[1])
	await info[ctx.guild.id]["nowplaying"].delete()
	info[ctx.guild.id]["nowplaying"] = await ctx.send(embed = embeds[0])#, view = embeds[2])
	await info[ctx.guild.id]["button_holder"].delete()
	info[ctx.guild.id]["button_holder"] = await ctx.send(embed = embeds[3], view = embeds[2])
	info[ctx.guild.id]["channel"] = ctx.channel

async def update_nowplaying(guild):
	try:
		if (info[guild]["paused"] or info[guild]["processing"]):
			return

		if (len(info[guild]["queue"]) > 0 and info[guild]["nowplaying_edits"] >= 0):

			voice_client = info[guild]["voice"]
			if (voice_client and voice_client.is_playing()):
				embeds = nowplaying_embed(guild, info[guild]["queue"][0])
				await info[guild]["nowplaying"].edit(embed = embeds[0])

				# if (info[guild]["recomended_vid"] != None and info[guild]["nowplaying_buffer"] == True):
				# 	info[guild]["nowplaying_buffer"] = False
				# 	await info[guild]["thumbnail"].edit(embed = embeds[1])
				# 	await info[guild]["button_holder"].edit(embed = embeds[3], view = embeds[2])

			else:
				ended = await check_if_song_ended(guild)
				if (not ended) and (not info[guild].get("refetch_tried", False)):
					print("refetching video info...")
					try:
						if find_video_info(info[guild]["queue"][0], only_source = True, refetch = True):
							await play_url(guild, info[guild]["queue"][0])
							print("refetching was successful")
					except Exception as e:
						print(repr(e))
					finally:
						info[guild]["refetch_tried"] = True

		info[guild]["nowplaying_edits"] += 1
		if (info[guild]["nowplaying_edits"] > 300):
			info[guild]["nowplaying_edits"] = 0

			embeds = nowplaying_embed(guild, info[guild]["queue"][0])

			# if (server_config[guild]["large nowplaying thumbnail"]):
			await info[guild]["thumbnail"].delete()
			info[guild]["thumbnail"] = await info[guild]["channel"].send(embed = embeds[1])
			await info[guild]["nowplaying"].delete()
			info[guild]["nowplaying"] = await info[guild]["channel"].send(embed = embeds[0])#, view = embeds[2])
			await info[guild]["button_holder"].delete()
			info[guild]["button_holder"] = await info[guild]["channel"].send(embed = embeds[3], view = embeds[2])

	except Exception as e:
		print("--- UPDATE LOOP CRASHED ---")
		import traceback
		traceback.print_exc() # Prints the specific line number and error

async def play_next(guild):
    current_url = info[guild]["queue"][0]
    info[guild]["past queue"].append(current_url)
    if (not info[guild]["looping"]):
        del info[guild]["queue"][0]

    if (len(info[guild]["queue"]) > 0):
        await play_url(guild, info[guild]["queue"][0])
    elif (info[guild]["autoplay"]):
        # Safe get
        vid = info[guild].get("recomended_vid")
        
        # --- FIX: EXACT COPY OF QUEUE END LOGIC ---
        if vid is None:
            if info[guild]["voice"].is_connected():
                await info[guild]["voice"].disconnect()
            
            info[guild]["task"].cancel()

            # EXACT same embed structure as check_if_song_ended
            embed = discord.Embed(
                title = language[server_config[guild]["lang_set"]]["embed field"]["queue_end"].title(),
                description = "", 
                color = snoo_color,
            )
            embed.set_author(
                name = title_format.format(
                    language[server_config[guild]["lang_set"]]["ui"]["title"]["queue_end"].title()
                ),
                icon_url = music_icon,
            )
            await info[guild]["channel"].send(embed = embed)

            info[guild]["queue"].clear()
            return
        # --- END FIX ---

        info[guild]["recomended_vid"] = None
        info[guild]["nowplaying_buffer"] = True
        await play_sys(discord.Object(id = guild), info[guild]["channel"], autoplay = vid)

    # Everything below here runs only if music is still playing
    embeds = nowplaying_embed(guild, info[guild]["queue"][0])
    await info[guild]["thumbnail"].edit(embed = embeds[1])
    await info[guild]["button_holder"].edit(embed = embeds[3])
    
    time_since_start = datetime.datetime.now() - info[guild]["start_time"]
    length = video_info[current_url].get("secs_length", 0)
    
    if length > 0:
        watch_prsnt = round(time_since_start.seconds * (1 / length), 2)
    else:
        watch_prsnt = 0.0

    for user in get_users_in_vc(True)[guild]:
        if (guild not in song_history or user not in song_history[guild]):
            song_history[guild][user] = [{current_url: [{"retention": watch_prsnt, "listen_time": time_since_start.seconds}]}]
        elif (current_url not in song_history[guild][user][-1]):
            song_history[guild][user][-1][current_url] = [{"retention": watch_prsnt, "listen_time": time_since_start.seconds}]
        else:
            song_history[guild][user][-1][current_url].append({"retention": watch_prsnt, "listen_time": time_since_start.seconds})

# @snoo.command()
# async def queue(ctx):
# 	verify_settings(ctx.guild.id)
# 	if (info[ctx.guild.id]["voice"].is_playing()):
# 		embed=discord.Embed(title = "", description = "", color=snoo_color)
# 		embed.set_author(name = title_format.format(language[server_config[ctx.guild.id]['lang_set']]['ui']['title']['queue'].upper()), icon_url=music_icon)
		
# 		songs = ""
# 		durations = ""
# 		early_break = False
# 		#channels = ""
# 		total_time = 0
# 		for video in info[ctx.guild.id]["queue"]:
# 			total_time += video_info[video]["secs_length"]

# 		for i in range(len(info[ctx.guild.id]["queue"])):
# 			if (i == 0):
# 				embed.add_field(name = f'<a:MusicBars:917119951603646505> {video_info[info[ctx.guild.id]["queue"][i]]["title"]}', value = video_info[info[ctx.guild.id]["queue"][i]]["channel_name"], inline = True)
# 				embed.add_field(name = '\u200b', value = '\u200b', inline = True)
# 				embed.add_field(name = format_time(video_info[info[ctx.guild.id]["queue"][i]]["secs_length"]), value = '\u200b', inline = True)
# 				embed.set_thumbnail(url=video_info[info[ctx.guild.id]["queue"][i]]["thumbnail"])
# 			else:
# 				#embed.add_field(name = f'{i} {video_info[info[ctx.guild.id]["queue"][i]]["title"]}', value = video_info[info[ctx.guild.id]["queue"][i]]["channel_name"], inline = True)
# 				#embed.add_field(name = '\u200b', value = '\u200b', inline = True)
# 				#embed.add_field(name = format_time(video_info[info[ctx.guild.id]["queue"][i]]["secs_length"]), value = '\u200b', inline = True)

# 				chr_per_row = 40
# 				if (len(songs) < 1024 - chr_per_row):
# 					songs += f"**{i}** " + video_info[info[ctx.guild.id]["queue"][i]]["title"][0 : chr_per_row]
# 					if (len(video_info[info[ctx.guild.id]["queue"][i]]["title"]) > chr_per_row):
# 						songs += "...\n"
# 					else:
# 						songs += "\n"
# 				else: 
# 					early_break = True
# 					embed.set_footer(text = language[server_config[ctx.guild.id]["lang_set"]]["ui"]["field"]["queue_footer"]["full"].format(len(info[ctx.guild.id]["queue"]) - i, format_time(total_time)))
# 					break

# 				#channels += video_info[info["queue"][i]]["channel_name"] + "\n"
# 				durations += format_time(video_info[info[ctx.guild.id]["queue"][i]]["secs_length"]) + "\n"

# 		if (songs != ""):
# 			embed.add_field(name = language[server_config[ctx.guild.id]["lang_set"]]["ui"]["field"]["next_up"], value = songs, inline=True)
# 			embed.add_field(name = language[server_config[ctx.guild.id]["lang_set"]]["ui"]["field"]["duration"], value = durations, inline=True)

# 		if (info[ctx.guild.id]["autoplay"]):
# 			embed.add_field(name = language[server_config[ctx.guild.id]["lang_set"]]["ui"]["field"]["autoplay"], value = video_info[info[ctx.guild.id]["recomended_vid"]]["title"], inline = False)

# 		if (not early_break):
# 			embed.set_footer(text = language[server_config[ctx.guild.id]["lang_set"]]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))
		
# 		await ctx.send(embed=embed)

async def show_queue(interaction):
	if (info[interaction.guild.id]["show_queue"]):
		info[interaction.guild.id]["show_queue"] = False
	else:
		info[interaction.guild.id]["show_queue"] = True

	embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
	await interaction.response.edit_message(embed = embeds[3], view = embeds[2])

@snoo.command()
async def stop(ctx):
	verify_settings(ctx.guild.id)
	if (ctx.guild.id in info and len(info[ctx.guild.id]["queue"]) >= 1):
		#info[ctx.guild.id]["queue"].clear()
		info[ctx.guild.id]["voice"].stop()
		info[ctx.guild.id]["task"].cancel()
		await info[ctx.guild.id]["voice"].disconnect()
		info.pop(ctx.guild.id)

		embed=discord.Embed(title = language[server_config[ctx.guild.id]['lang_set']]['ui']['field']['stopped'].title(), description = f"", color=snoo_color)
		embed.set_author(name = title_format.format(language[server_config[ctx.guild.id]['lang_set']]['ui']['title']['stopped'].title()), icon_url=music_icon)
		await ctx.send(embed = embed)

async def stop_button(interaction):
	verify_settings(interaction.guild.id)
	if (interaction.guild.id in info):
		#info[ctx.guild.id]["queue"].clear()
		info[interaction.guild.id]["voice"].stop()
		info[interaction.guild.id]["task"].cancel()
		await info[interaction.guild.id]["voice"].disconnect()
		info.pop(interaction.guild.id)

		embed=discord.Embed(title = language[server_config[interaction.guild.id]['lang_set']]['ui']['field']['stopped'].title(), description = f"", color=snoo_color)
		embed.set_author(name = title_format.format(language[server_config[interaction.guild.id]['lang_set']]['ui']['title']['stopped'].title()), icon_url=music_icon)
		await interaction.response.send_message(embed = embed)

@snoo.command()
async def pause(ctx):
	if (not info[ctx.guild.id]["paused"]):
		info[ctx.guild.id]["voice"].pause()
		info[ctx.guild.id]["paused"] = True
		info[ctx.guild.id]["pause_time"] = datetime.datetime.now()
		await ctx.message.add_reaction("⏸️")
	else:
		info[ctx.guild.id]["voice"].resume()
		info[ctx.guild.id]["paused"] = False
		info[ctx.guild.id]["start_time"] += datetime.datetime.now() - info[ctx.guild.id]["pause_time"]
		await ctx.message.add_reaction("▶️")

async def pause_button(interaction):
	if (not info[interaction.guild.id]["paused"]):
		info[interaction.guild.id]["voice"].pause()
		info[interaction.guild.id]["paused"] = True
		info[interaction.guild.id]["pause_time"] = datetime.datetime.now()
	else:
		info[interaction.guild.id]["voice"].resume()
		info[interaction.guild.id]["paused"] = False
		info[interaction.guild.id]["start_time"] += datetime.datetime.now() - info[interaction.guild.id]["pause_time"]

	embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
	await interaction.response.edit_message(embed = embeds[3], view = embeds[2])

@snoo.command()
async def skip(ctx):
	verify_settings(ctx.guild.id)
	if (len(info[ctx.guild.id]["queue"]) > 1 or info[ctx.guild.id]["autoplay"]):
		if (info[ctx.guild.id]["paused"]):
			info[ctx.guild.id]["paused"] = False
			embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
			await ctx.edit(view = embeds[2])

		await play_next(ctx.guild.id)
	else:
		await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["error"]["can_not_skip"])

async def skip_button(interaction):
	verify_settings(interaction.guild.id)
	if (len(info[interaction.guild.id]["queue"]) > 1 or info[interaction.guild.id]["autoplay"]):
		if (info[interaction.guild.id]["paused"]):
			info[interaction.guild.id]["paused"] = False
			embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
			await interaction.message.edit(view = embeds[2])

		await play_next(interaction.guild.id)

		#member = await interaction.guild.fetch_member(interaction.user.id)
		await interaction.response.defer()
		#await interaction.response.send_message(language[lang_set]["notifs"]["skip"].format(member.nick))
	else:
		await interaction.response.send_message(language[server_config[interaction.guild.id]['lang_set']]["error"]["can_not_skip"])

@snoo.command()
async def back(ctx):
	verify_settings(ctx.guild.id)
	if (len(info[ctx.guild.id]["past queue"]) >= 1):
		if (info[ctx.guild.id]["paused"]):
			info[ctx.guild.id]["paused"] = False
			embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
			await ctx.edit(view = embeds[2])

		cur_track = info[ctx.guild.id]["queue"][0]
		info[ctx.guild.id]["queue"].insert(1, info[ctx.guild.id]["past queue"][-1])
		await play_next(ctx.guild.id)
		info[ctx.guild.id]["queue"].insert(1, cur_track)
		del info[ctx.guild.id]["past queue"][-2:]
	else:
		await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["error"]["can_not_back"])

async def back_button(interaction):
	verify_settings(interaction.guild.id)
	if (len(info[interaction.guild.id]["past queue"]) >= 1):
		if (info[interaction.guild.id]["paused"]):
			info[interaction.guild.id]["paused"] = False
			embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
			await interaction.message.edit(view = embeds[2])

		cur_track = info[interaction.guild.id]["queue"][0]
		info[interaction.guild.id]["queue"].insert(1, info[interaction.guild.id]["past queue"][-1])
		await play_next(interaction.guild.id)
		info[interaction.guild.id]["queue"].insert(1, cur_track)
		del info[interaction.guild.id]["past queue"][-2:]
		

		#member = await interaction.guild.fetch_member(interaction.user.id)
		await interaction.response.defer()
		#await interaction.response.send_message(language[lang_set]["notifs"]["back"].format(member.nick))
	else:
		await interaction.response.send_message(language[server_config[interaction.guild.id]['lang_set']]["error"]["can_not_back"])

async def like_button(interaction):
	if (info[interaction.guild.id]["queue"][0] in playlists[interaction.guild.id]["liked"]):
		playlists[interaction.guild.id]["liked"].remove(info[interaction.guild.id]["queue"][0])
	else:
		playlists[interaction.guild.id]["liked"].append(info[interaction.guild.id]["queue"][0])

	embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
	await interaction.response.edit_message(embed = embeds[3], view = embeds[2])

async def check_if_song_ended(guild):
	"""Return True if we consider the current song finished, False otherwise.
	We are defensive about missing/zero duration so we don't spam join/leave.
	"""
	verify_settings(guild)
	# If for some reason there's no queue, treat as ended.
	if guild not in info or len(info[guild]["queue"]) == 0:
		return True

	current_id = info[guild]["queue"][0]
	length = video_info.get(current_id, {}).get("secs_length", 0)
	time_since_start = datetime.datetime.now() - info[guild]["start_time"]

	# If we don't know the length (<= 0), don't auto-disconnect immediately.
	# Give it at least 5 seconds before we treat it as ended to avoid join/leave loops.
	if length <= 0:
		if time_since_start.total_seconds() < 5:
			return False
	else:
		# Normal case: if we've not yet reached the end, it's not finished.
		if (time_since_start.total_seconds() + 1) < length:
			return False

	# At this point we consider the track finished.
	if (len(info[guild]["queue"]) > 1 or info[guild]["looping"] or info[guild]["autoplay"]):
		await play_next(guild)
	else:
		await info[guild]["voice"].disconnect()
		info[guild]["task"].cancel()

		embed = discord.Embed(
			title = language[server_config[guild]["lang_set"]]["embed field"]["queue_end"].title(),
			description = "",
			color = snoo_color,
		)
		embed.set_author(
			name = title_format.format(
				language[server_config[guild]["lang_set"]]["ui"]["title"]["queue_end"].title()
			),
			icon_url = music_icon,
		)
		await info[guild]["channel"].send(embed = embed)

		info[guild]["queue"].clear()
	return True

@snoo.command()
async def loop(ctx):
	verify_settings(ctx.guild.id)
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (info[ctx.guild.id]["looping"]):
			info[ctx.guild.id]["looping"] = False
			await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["notifs"]["loop_stop"])
		else:
			info[ctx.guild.id]["looping"] = True
			await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["notifs"]["loop_start"])

@snoo.command()
async def autoplay(ctx):
	verify_settings(ctx.guild.id)
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (info[ctx.guild.id]["autoplay"]):
			info[ctx.guild.id]["autoplay"] = False
			await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["notifs"]["autoplay_stop"])
		else:
			info[ctx.guild.id]["autoplay"] = True
			await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["notifs"]["autoplay_start"])

@snoo.command()
async def shuffle(ctx):
	verify_settings(ctx.guild.id)
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (not info[ctx.guild.id]["shuffle"]):
			nowplaying = info[ctx.guild.id]["queue"][0]
			info[ctx.guild.id]["original queue"] = info[ctx.guild.id]["queue"]

			info[ctx.guild.id]["queue"].remove(info[ctx.guild.id]["queue"][0])
			shuffle(info[ctx.guild.id]["queue"])

			info[ctx.guild.id]["queue"].insert(0, nowplaying)
			await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["notifs"]["shuffle"])
		else:
			info[ctx.guild.id]["queue"] = info[ctx.guild.id]["original queue"]
			await ctx.send(language[server_config[ctx.guild.id]['lang_set']]["notifs"]["unshuffle"])

# _________________________________________________________________ DEBUGING _________________________________________________________________

@snoo.command()
async def hi(ctx):
	view = View()
	button = Button(style = discord.ButtonStyle.primary, label = "hi", emoji = "😊")
	button.callback = button_callback
	view.add_item(button)
	await ctx.send("hi", view = view)

async def button_callback(interaction):
	await interaction.response.send_message("hi " + str(interaction.user) + "!")

# _________________________________________________________________ SYSTEM _________________________________________________________________

@snoo.command()
async def quit(ctx):
	if (ctx.message.author.id == admin):
		await ctx.send("stopping the program...")
		sys.exit("stopped the program")
	else:
		await ctx.send(admin_command_message)

@snoo.command()
async def restart(ctx):
	if (ctx.message.author.id == admin):
		await ctx.send("restarting the program...")
		print("restarting the program...")
		os.system("python main.py")
		asyncio.sleep(0.2)
		quit()
	else:
		await ctx.send(admin_command_message)

async def download_datafile(channel_id, name):
	channel = snoo.get_channel(channel_id)
	async for message in channel.history (limit = 1):
		await message.attachments[0].save(f"Data Files/{name}.json")
	f = open(f"Data Files/{name}.json")
	return json.load(f)

def dict_str_to_int(str_dict, _dict, single = False):
	if (not single):
		for key in str_dict:
			for new_key in str_dict[key]:
				_dict[int(key)][int(new_key)] = str_dict[key][new_key]
	else:
		for key in str_dict:
			_dict[int(key)] = str_dict[key]

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

def valid_url(uri: str) -> bool:
    try:
        with r_get(uri, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except exceptions.HTTPError:
                return False
    except exceptions.ConnectionError:
        return False

def verify_yt_id(video_id: str):
    checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
    video_url = checker_url + video_id

    request = r_get(video_url)

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
    url = findall(regex, string)      
    return [x[0] for x in url]

def str_json(string):
	with open("Cache/string.json", "w") as outfile:
		json.dump(string, outfile)

@snoo.command()
async def history(ctx):
	if (ctx.message.author.id == admin):
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
		#shuffle(first_ten)
		await ctx.send(first_ten)
	else:
		await ctx.send(admin_command_message)

def get_users_in_vc(exclude_snoo: bool = False):
	users_in_vc = {}

	for guild in snoo.guilds:
		for vc in guild.voice_channels:
			if len(vc.members) > 0:
				if guild.id not in users_in_vc:
					users_in_vc[guild.id] = []
				for member in vc.members:
					if exclude_snoo and snoo.user is not None and member.id == snoo.user.id:
						continue
					users_in_vc[guild.id].append(member.id)

	return users_in_vc

def verify_settings(guild):
	if (guild not in server_config):
		server_config[guild] = deepcopy(default_settings)

def verify_data(guild, user):
	if guild not in profile_data:
		profile_data[guild] = {}
	if user not in profile_data[guild]:
		profile_data[guild][user] = {
			"messages": [0],
			"vc_time": [0],
			"friendship": [0],
			"karma": [0],
		}

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

@snoo.command()
async def add(ctx):
	if (ctx.message.author.id == admin):
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

@snoo.command()
async def save(ctx):
	if ctx.message.author.id == admin:
		await new_save()
		await ctx.message.add_reaction("✅")
	else:
		await ctx.send(admin_command_message)

async def upload_file(channel_id, name, file):
	channel = snoo.get_channel(channel_id)
	json_object = json.dumps(file)
	os.makedirs("Data Files", exist_ok=True)
	with open(f"Data Files/{name}.json", "w", encoding="utf-8") as outfile:
		outfile.write(json_object)
	await channel.send(file=discord.File(f"Data Files/{name}.json"))

async def new_save():
	start_time = datetime.datetime.now()

	users_in_vc = get_users_in_vc()
	for server in users_in_vc:
		for user in users_in_vc[server]:
			verify_data(server, user)
			profile_data[server][user]["vc_time"][-1] = round(
				profile_data[server][user]["vc_time"][-1] + 0.1, 1
			)

	await upload_file(977316868253708359, "profile", profile_data)
	await upload_file(913524223870398534, "channel_messages", channel_messages)
	await upload_file(985597229022724136, "server_config", server_config)
	await upload_file(922592622248341505, "song_history", song_history)

	save_info = deepcopy(video_info)
	for vid_id, info_dict in list(save_info.items()):
		if isinstance(info_dict, dict) and "source" in info_dict:
			info_dict.pop("source")

	await upload_file(993332319454760960, "video_info", save_info)
	await upload_file(999117002323001354, "playlists", playlists)

	print("saved in " + str(round((datetime.datetime.now() - start_time).total_seconds() * 1000)) + "ms")

@tasks.loop(minutes=1)
async def daily_entry_check():
	now = datetime.datetime.now().strftime("%H:%M")
	if now == "05:00":
		add_entry()

@daily_entry_check.before_loop
async def before_daily_entry_check():
	await snoo.wait_until_ready()

async def async_timer(interval, func, arg1 = None, arg2 = None, arg3 = None):
	while True:
		if (arg1 == None):
			await asyncio.gather(asyncio.sleep(interval), func(),)
		elif (arg2 == None):
			await asyncio.gather(asyncio.sleep(interval), func(arg1),)
		elif (arg3 == None):
			await asyncio.gather(asyncio.sleep(interval), func(arg1, arg2),)
		else:
			await asyncio.gather(asyncio.sleep(interval), func(arg1, arg2, arg3),)

# _________________________________________________________________ RUN _________________________________________________________________


with open('Token/filekey.key', 'rb') as filekey:
	key = filekey.read()

fernet = Fernet(key)

with open('Token/token.txt', 'rb') as enc_file:
    encrypted = enc_file.read()

handler = FileHandler(filename='Cache/discord.log', encoding='utf-8', mode='w')
snoo.run(fernet.decrypt(encrypted).decode('UTF-8'), log_handler = handler)