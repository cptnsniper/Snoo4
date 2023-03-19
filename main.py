import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord.ui import Button, View
import os
import json
import datetime
from threading import Thread, Timer
import asyncio
from math import fsum, floor
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
from pytube import Playlist
from validators import url
import queue
from logging import FileHandler
from PIL import Image

from System.system import *

intents = discord.Intents.all()
snoo = commands.Bot(command_prefix = prefix, intents = intents)

if (not os.path.isdir('Data Files')):
	os.makedirs("Data Files")
if (not os.path.isdir('Cache')): 
	os.makedirs("Cache")

@snoo.event
async def on_ready():
	print(f'we have logged in as {snoo.user}')
	await snoo.tree.sync()#guild = discord.Object(test_server))
	await snoo.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "music for my friends!"))

	await initialize_data()
	verify_lang()
	print("imported data")
	str_json(missing_translations)
	#await channel.send(file=discord.File('Cache/string.json'))
	asyncio.create_task(async_timer(60 * 6, new_save)) #PLEASE FUTURE ME REMMEBER TO UNCOMMENT!!!!!!!!!

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
		if (message.attachments or len(find_url(message.content)) > 0 or '*image*' in message.content.lower()):
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
				await message.add_reaction(emojis["upvote"])
			else:
				await message.add_reaction(upvote)
			if (server_config[message.guild.id]["downvote"]):
				if (downvote == None):
					await message.add_reaction(emojis["downvote"])
				else:
					await message.add_reaction(downvote)

	if (message.content.lower().startswith('%')):
		if ('scale' in message.content.lower()):
			for num in emojis["numbers"]:
				await message.add_reaction(num)
		else:	
			await message.add_reaction(emojis["cross"])
			await message.add_reaction(emojis["check"])

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
				embed.add_field(name = emojis["on"], value = "\u200b", inline = True)
			else:
				embed.add_field(name = emojis["off"], value = "\u200b", inline = True)
		await ctx.send(embed=embed)

@snoo.command()
async def poll(ctx, name, *, opts):
	opts_list = opts.split(',')

	embed = discord.Embed(title = name, colour = snoo_color)
	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['poll'].upper()}", icon_url = poll_icon)

	for i in range(len(opts_list)):
		embed.add_field(name = f"{language[lang_set]['ui']['field']['option']}  {emojis['poll'][i]}", value = opts_list[i], inline=False)

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
	if (ctx.message.author.id == 401442600931950592):
		await ctx.message.delete()
		await ctx.send(args)

#display information
@snoo.command()
async def profile(ctx, *, user: discord.User = 0):
	if (user == 0):
		user_id = ctx.message.author.id
	else:
		user_id = user.id

	user = await snoo.fetch_user(user_id)
	split_user = str(user).split("#", 1)
	username = split_user[0]

	verify_data(ctx.guild.id, user_id)

	embed = discord.Embed(colour = snoo_color)

	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['profile'].format(username).upper()}", icon_url = profile_icon)

	embed.add_field(name = language[lang_set]['ui']['field']['karma']['title'], value = language[lang_set]['ui']['field']['karma']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['karma'])), inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = language[lang_set]['ui']['field']['friendship']['title'], value = language[lang_set]['ui']['field']['friendship']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['friendship'])), inline = True)
	embed.add_field(name = language[lang_set]['ui']['field']['messages']['title'], value = language[lang_set]['ui']['field']['messages']['desc'].format(sum(profile_data[ctx.guild.id][user_id]['messages'])), inline = True)
	embed.add_field(name = '\u200b', value = '\u200b', inline = True)
	embed.add_field(name = language[lang_set]['ui']['field']['vc_hours']['title'], value = language[lang_set]['ui']['field']['vc_hours']['desc'].format(fsum(profile_data[ctx.guild.id][user_id]['vc_time'])), inline = True)
	
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
	print(playlists[ctx.guild.id])
	if (playlist in playlists[ctx.guild.id]):
		embed = discord.Embed(title = playlists[ctx.guild.id][playlist]["title"], description = playlists[ctx.guild.id][playlist]["desc"], color = snoo_color)
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['playlist'].upper()}", icon_url=music_icon)
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

def find_video_info(id, only_source = False, only_rec = False):
	if (not only_rec):
		YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}
		with YoutubeDL(YDL_OPTIONS) as ydl:
			try:
				vid = ydl.extract_info(id, download=False)
			except:
				print("failed to fetch video info for: ", id)
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
		attempt_i = -1
		while (True):
			video_info[id]["thumbnail"] = vid["thumbnails"][attempt_i]["url"]
			if (valid_url(video_info[id]["thumbnail"])):
				break
			attempt_i -= 1
		str_json(vid["thumbnails"])

	try:
		headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
		resp = r_get('http://www.youtube.com/watch?v=' + id, headers=headers)
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
	except:
		print("failed to find recomended vid for: " + id)

	return True

def search_yt(search):
	query_string = urlencode({'search_query' : search})
	html_content = urlopen('http://www.youtube.com/results?' + query_string)
	search_results = findall(r"watch\?v=(\S{11})", html_content.read().decode())

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
		print("new video: " + result)
		if (not find_video_info(result)):
			return None
	
	return result

def find_playlist_index(queue, thread):
	while True:
		queue_index = queue.get()
		playlist = queue_index[0]
		index = queue_index[1]
		playlist[index] = search_and_find_info(playlist[index])
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
						await channel.send(language[lang_set]["error"]["not_youtube"])
						return
				else:		
					await channel.send(language[lang_set]["error"]["no_content"])
					return
			elif (message_reference.content == ""):
				await channel.send(language[lang_set]["error"]["no_content"])
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
	await play_sys(interaction.guild, interaction.channel, message, interaction.user)
	await interaction.followup.send("interaction successful")

@snoo.command()
async def play(ctx, *, search = None):
	await play_sys(ctx.guild, ctx.channel, ctx.message.reference, ctx.message.author, search)

async def play_sys(guild = None, channel = None, reference = None, user = None, search = None, autoplay = None):
	skip_search = False
	playlist = None
	searching_msg = None
	id = None
	searching = f'{language[lang_set]["notifs"]["searching"]} {loading_icon}'

	if (autoplay == None):
		if (guild.id not in playlists or "liked" not in playlists[guild.id]):
			playlists[guild.id]["liked"] = []

		if (guild.id not in info):
			info[guild.id] = deepcopy(default_info)
			info[guild.id]["channel"] = channel
			info[guild.id]["voice"] = get(snoo.voice_clients, guild = guild)
		
		if (type(user.voice) == type(None)):
			await channel.send(language[lang_set]["error"]["no_vc"])
			return

		filtered_info = await filter_url(reference, channel, search)
		print(filtered_info)
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
					await searching_msg.edit(content = language[lang_set]["error"]["nothing_found"])
					return
	else:
		id = autoplay

	if (not skip_search):
		found_info = True
		if (id not in video_info):
			print("new video")
			found_info = find_video_info(id)

		print(id)
		if (not valid_url(video_info[id]["source"])):
			print("url expired")
			found_info = find_video_info(id, True)

		if (not found_info):
			if (searching_msg != None):
				await searching_msg.edit(content = language[lang_set]["error"]["age_restricted"])
			else:
				await channel.send(language[lang_set]["error"]["age_restricted"])
			return		

		info[guild.id]["queue"].append(id)

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
				info[guild.id]["task"] = asyncio.create_task(async_timer(1, update_nowplaying, guild.id))
			else:
				embed = small_queued_embed(id)

				if (searching_msg != None):
					await searching_msg.edit(content="", embed = embed)
				else:
					print("there was no message to edit and snoo was unable to edit a conformation embed")
					await channel.send(embed = embed)
		else:
			await play_url(guild.id, id)

		find_autoplay(guild.id, id, )

	if (playlist != None and len(playlist) > 0):
		Thread(target = thread_find_playlist, args = (playlist, )).start()
		await queued_embed(channel, playlist)

async def play_url(guild, id):
	if (info[guild]["voice"].is_playing()):
		info[guild]["voice"].stop()

	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	info[guild]["voice"].play(FFmpegPCMAudio(source = video_info[id]["source"], **FFMPEG_OPTIONS))
	info[guild]["voice"].is_playing()
	info[guild]["start_time"] = datetime.datetime.now()

def find_autoplay(guild, id):
	if ("recomended_vids" not in video_info[id]):
		find_video_info(id, only_rec = True)

	for vid in video_info[id]["recomended_vids"]:
		if (vid not in info[guild]["past queue"]):
			info[guild]["recomended_vid"] = vid
			if (vid not in video_info):
				if (not find_video_info(vid)):
					continue
			print("autoplay: " + vid)
			break

async def queued_embed(channel, playlist):
	edit_needed = False
	i = 0
	total_time = 0

	embed = discord.Embed(color = snoo_color)
	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()} {0} / {len(playlist)}", icon_url = music_icon)
	embed_msg = await channel.send(embed = embed)

	while (i < len(playlist)):
		if (playlist[i] in video_info):
			info[embed_msg.guild.id]["queue"].append(playlist[i])
			total_time += video_info[playlist[i]]["secs_length"]
			if (i == 0):
				embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
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
		elif (playlist[i] == None):
			i += 1
		else:
			edit_needed = True

	embed.set_thumbnail(url = video_info[playlist[0]]["thumbnail"])
	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()}", icon_url = music_icon)
	if (len(playlist) < 25):
		embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))
	if (embed_msg == None):
		embed_msg = await embed_msg.send(embed = embed)
	else:
		await embed_msg.edit(embed = embed)

	find_autoplay(embed_msg.guild.id, playlist[-1])

def small_queued_embed(id):
	embed = discord.Embed(title = video_info[id]["title"], url = 'http://www.youtube.com/watch?v=' + id, description = f'[{video_info[id]["channel_name"]}]({video_info[id]["channel_link"]})', color = snoo_color)
	embed.set_thumbnail(url = video_info[id]["thumbnail"])
	embed.set_author(name = f"||  {language[lang_set]['ui']['title']['queued'].upper()}", icon_url = music_icon)
	return embed

def nowplaying_embed(guild, id):
	verify_settings(guild)

	time_since_start = datetime.datetime.now() - info[guild]["start_time"]
	playing_for = format_time(time_since_start.seconds)
	watch_prsnt = time_since_start.seconds * (100 / video_info[id]["secs_length"])

	playbar = f'{playing_for}   '

	"""playbar_length = 14
	if (server_config[guild]["large nowplaying thumbnail"]):"""
	playbar_length = 18

	segments_prsnt = watch_prsnt * (playbar_length / 100)
	fill_error = 0.5
	empty_error = 0.5

	if (segments_prsnt > 1):
		playbar += emojis["bar1r"]
		fill_error = 1.5
	if (playbar_length - segments_prsnt > 1):
		empty_error = 1.5
	playbar += emojis["bar1"] * round(segments_prsnt - fill_error)
	for i in range(5):
		if (segments_prsnt % 1 < (i + 1) * 0.2):
			if (segments_prsnt > 1 and playbar_length - segments_prsnt > 1):
				playbar += emojis["bar2"][i]
			elif (segments_prsnt < 1):
				playbar += emojis["bar2rR"][i]
			elif (playbar_length - segments_prsnt < 1):
				playbar += emojis["bar2rL"][i]
			break
	playbar += emojis["bar3"] * (playbar_length - round(segments_prsnt + empty_error))
	if (playbar_length - segments_prsnt > 1):
		playbar += emojis["bar3r"]
	playbar += f'   {format_time(video_info[id]["secs_length"])}'

	try:
		urlretrieve(video_info[id]["thumbnail"], "Cache\img.png")
	except:
		find_video_info(id)
		urlretrieve(video_info[id]["thumbnail"], "Cache\img.png")
	img = Image.open("Cache\img.png")
	pix = img.load()
	pixel = [0, 0, 0]
	for i in range(img.size[1]):
		pixel[0] += pix[0, i][0]
		pixel[1] += pix[0, i][1]
		pixel[2] += pix[0, i][2]

	pixel[0] /= img.size[1]
	pixel[1] /= img.size[1]
	pixel[2] /= img.size[1]
	# color = snoo_color
	color = discord.Color.from_rgb(round(pixel[0]), round(pixel[1]), round(pixel[2]))

	publish_date = str(video_info[id]["publish_date"])
	publish_date = datetime.datetime(int(publish_date[0:4]), int(publish_date[4:6]), int(publish_date[6:8]))
	publish_date_delta = datetime.datetime.now() - publish_date
	time_ago = publish_date.strftime("%b %d %Y")
	if (not info[guild]["show_queue"]):
		if (publish_date_delta.days >= 365):
			years = floor(publish_date_delta.days / 365)
			if (years == 1):
				time_ago = language[lang_set]['ui']['field']['time_delta']['year']['singular']
			else:
				time_ago = language[lang_set]['ui']['field']['time_delta']['year']['plural'].format(years)
		elif (publish_date_delta.days >= 30):
			months = floor(publish_date_delta.days / 30)
			if (months == 1):
				time_ago = language[lang_set]['ui']['field']['time_delta']['month']['singular']
			else:
				time_ago = language[lang_set]['ui']['field']['time_delta']['month']['plural'].format(months)
		elif (publish_date_delta.days > 0):
			days = publish_date_delta.days
			if (days == 1):
				time_ago = language[lang_set]['ui']['field']['time_delta']['day']['singular']
			else:
				time_ago = language[lang_set]['ui']['field']['time_delta']['day']['plural'].format(days)
		elif (publish_date_delta.hours > 0):
			hours = publish_date_delta.hours
			if (hours == 1):
				time_ago = language[lang_set]['ui']['field']['time_delta']['hours']['singular']
			else:
				time_ago = language[lang_set]['ui']['field']['time_delta']['hour']['plural'].format(hours)
		else:
			minutes = publish_date_delta.hours
			if (minutes == 1):
				time_ago = language[lang_set]['ui']['field']['time_delta']['minute']['singular']
			elif (minutes < 1):
				time_ago = language[lang_set]['ui']['field']['time_delta']['minute']['less_than']
			else:
				time_ago = language[lang_set]['ui']['field']['time_delta']['minute']['plural'].format(minutes)

	views = '{:,}'.format(video_info[id]['views'])
	if (not info[guild]["show_queue"]):
		if (video_info[id]['views'] > 1000000000):
			views = f"{round(video_info[id]['views'] / 1000000000)}{language[lang_set]['ui']['field']['number_multiplier']['billion']}"
		elif (video_info[id]['views'] > 1000000):
			views = f"{round(video_info[id]['views'] / 1000000)}{language[lang_set]['ui']['field']['number_multiplier']['million']}"
		elif (video_info[id]['views'] > 1000):
			views = f"{round(video_info[id]['views'] / 1000)}{language[lang_set]['ui']['field']['number_multiplier']['thousand']}"

	embed = discord.Embed(title = video_info[id]["title"], url = 'http://www.youtube.com/watch?v=' + id, description = f'[{video_info[id]["channel_name"]}]({video_info[id]["channel_link"]})\n\n{playbar}', color=color)
	thumbnail_embed = discord.Embed(color = color)
	thumbnail_embed.set_image(url=video_info[id]["thumbnail"])
	thumbnail_embed.set_author(name = f"||  {language[lang_set]['ui']['title']['nowplaying'].upper()}", icon_url=music_icon)
	# print(video_info[id]["thumbnail"])
	button_embed = discord.Embed(description = f"{views} {language[lang_set]['ui']['field']['views']} - {time_ago}", color = color)

	if (info[guild]["show_queue"]):
		songs = ""
		durations = ""
		early_break = False
		total_time = 0
		for video in info[guild]["queue"]:
			total_time += video_info[video]["secs_length"]
		total_time += video_info[info[guild]["recomended_vid"]]["secs_length"]

		for i in range(len(info[guild]["queue"])):
			if (i == 0):
				continue

			chr_per_row = 40
			if (len(songs) < 1024 - chr_per_row):
				songs += f"**{i}** " + video_info[info[guild]["queue"][i]]["title"][0 : chr_per_row]
				if (len(video_info[info[guild]["queue"][i]]["title"]) > chr_per_row):
					songs += "...\n"
				else:
					songs += "\n"
			else: 
				early_break = True
				button_embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["full"].format(len(info[guild]["queue"]) - i, format_time(total_time)))
				break

			durations += format_time(video_info[info[guild]["queue"][i]]["secs_length"]) + "\n"

		if (songs != ""):
			button_embed.add_field(name = language[lang_set]["ui"]["field"]["next_up"], value = songs, inline=True)
			button_embed.add_field(name = language[lang_set]["ui"]["field"]["duration"], value = durations, inline=True)

		if (info[guild]["autoplay"]):
			button_embed.add_field(name = language[lang_set]["ui"]["field"]["autoplay"], value = video_info[info[guild]["recomended_vid"]]["title"], inline = False)

		if (not early_break):
			button_embed.set_footer(text = language[lang_set]["ui"]["field"]["queue_footer"]["short"].format(format_time(total_time)))

	view = View(timeout = None)

	emoji = "🤍"
	if (info[guild]["queue"][0] in playlists[guild]["liked"]):
		emoji = "❤️"
	button = Button(emoji = emoji)
	button.callback = like_button
	view.add_item(button)

	button = Button(emoji = "<:back:1035618514800754768>")
	button.callback = back_button
	view.add_item(button)

	emoji = "<:pause:1035617459295764490>"
	if (info[guild]["paused"]):
		emoji = "<:play:1035617460541460520>"
	button = Button(emoji = emoji)
	button.callback = pause_button
	view.add_item(button)

	button = Button(emoji = "<:skip:1035618493376254044>")
	button.callback = skip_button
	view.add_item(button)

	button = Button(emoji = "🛑")
	button.callback = stop_button
	view.add_item(button)

	emoji = "🔽"
	if (info[guild]["show_queue"]):
		emoji = "🔼"
	button = Button(emoji = emoji)
	button.callback = show_queue
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

			if (info[guild]["voice"].is_playing()):
				embeds = nowplaying_embed(guild, info[guild]["queue"][0])
				await info[guild]["nowplaying"].edit(embed = embeds[0])#, view = embeds[2])

			elif (not await check_if_song_ended(guild)):
				print("refetching video info...")
				find_video_info(info[guild]["queue"][0])
				await play_url(guild, info[guild]["queue"][0])

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
		await play_sys(discord.Object(id = guild), info[guild]["channel"], autoplay = info[guild]["recomended_vid"])

	embeds = nowplaying_embed(guild, info[guild]["queue"][0])
	await info[guild]["thumbnail"].edit(embed = embeds[1])
	await info[guild]["button_holder"].edit(embed = embeds[3])
	
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

async def show_queue(interaction):
	if (info[interaction.guild.id]["show_queue"]):
		info[interaction.guild.id]["show_queue"] = False
	else:
		info[interaction.guild.id]["show_queue"] = True

	embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
	await interaction.response.edit_message(embed = embeds[3], view = embeds[2])

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

async def stop_button(interaction):
	if (interaction.guild.id in info):
		#info[ctx.guild.id]["queue"].clear()
		info[interaction.guild.id]["voice"].stop()
		info[interaction.guild.id]["task"].cancel()
		await info[interaction.guild.id]["voice"].disconnect()
		info.pop(interaction.guild.id)

		embed=discord.Embed(title = language[lang_set]['ui']['field']['stopped'], description = f"", color=snoo_color)
		embed.set_author(name = f"||  {language[lang_set]['ui']['title']['stopped'].upper()}", icon_url=music_icon)
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
	if (len(info[ctx.guild.id]["queue"]) > 1 or info[ctx.guild.id]["autoplay"]):
		if (info[ctx.guild.id]["paused"]):
			info[ctx.guild.id]["paused"] = False
			embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
			await ctx.edit(view = embeds[2])

		await play_next(ctx.guild.id)
	else:
		await ctx.send(language[lang_set]["error"]["can_not_skip"])

async def skip_button(interaction):
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
		await interaction.response.send_message(language[lang_set]["error"]["can_not_skip"])

@snoo.command()
async def back(ctx):
	if (len(info[ctx.guild.id]["past queue"]) >= 1):
		if (info[ctx.guild.id]["paused"]):
			info[ctx.guild.id]["paused"] = False
			embeds = nowplaying_embed(ctx.guild.id, info[ctx.guild.id]["queue"][0])
			await ctx.edit(view = embeds[2])

		info[ctx.guild.id]["queue"].insert(1, info[ctx.guild.id]["past queue"][-1])
		await play_next(ctx.guild.id)
		del info[ctx.guild.id]["past queue"][-2:]
	else:
		await ctx.send(language[lang_set]["error"]["can_not_back"])

async def back_button(interaction):
	if (len(info[interaction.guild.id]["past queue"]) >= 1):
		if (info[interaction.guild.id]["paused"]):
			info[interaction.guild.id]["paused"] = False
			embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
			await interaction.message.edit(view = embeds[2])
		
		info[interaction.guild.id]["queue"].insert(1, info[interaction.guild.id]["past queue"][-1])
		await play_next(interaction.guild.id)
		del info[interaction.guild.id]["past queue"][-2:]

		#member = await interaction.guild.fetch_member(interaction.user.id)
		await interaction.response.defer()
		#await interaction.response.send_message(language[lang_set]["notifs"]["back"].format(member.nick))
	else:
		await interaction.response.send_message(language[lang_set]["error"]["can_not_back"])

async def like_button(interaction):
	if (info[interaction.guild.id]["queue"][0] in playlists[interaction.guild.id]["liked"]):
		playlists[interaction.guild.id]["liked"].remove(info[interaction.guild.id]["queue"][0])
	else:
		playlists[interaction.guild.id]["liked"].append(info[interaction.guild.id]["queue"][0])

	embeds = nowplaying_embed(interaction.guild.id, info[interaction.guild.id]["queue"][0])
	await interaction.response.edit_message(embed = embeds[3], view = embeds[2])

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

@snoo.command()
async def shuffle(ctx):
	if (info[ctx.guild.id]["voice"].is_playing()):
		if (not info[ctx.guild.id]["shuffle"]):
			nowplaying = info[ctx.guild.id]["queue"][0]
			info[ctx.guild.id]["original queue"] = info[ctx.guild.id]["queue"]

			info[ctx.guild.id]["queue"].remove(info[ctx.guild.id]["queue"][0])
			shuffle(info[ctx.guild.id]["queue"])

			info[ctx.guild.id]["queue"].insert(0, nowplaying)
			await ctx.send("I have shuffled the current queue!")
		else:
			info[ctx.guild.id]["queue"] = info[ctx.guild.id]["original queue"]
			await ctx.send("I have unshuffled the current queue!")

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
		#shuffle(first_ten)
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
	Timer(60, check_time).start()

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

async def upload_file(channel_id, name, file):
	channel = snoo.get_channel(channel_id)
	json_object = json.dumps(file, indent=4)
	with open(f"Data Files/{name}.json", "w") as outfile:
		outfile.write(json_object)
	await channel.send(file=discord.File(f"Data Files/{name}.json"))

async def new_save():
	time = datetime.datetime.now()

	users_in_vc = get_users_in_vc()
	for server in users_in_vc:
		for user in users_in_vc[server]:
			verify_data(server, user)
			profile_data[server][user]["vc_time"][-1] = round(profile_data[server][user]["vc_time"][-1] + 0.1, 1)

	await upload_file(977316868253708359, "profile", profile_data)
	await upload_file(913524223870398534, "channel_messages", channel_messages)
	await upload_file(985597229022724136, "server_config", server_config)
	await upload_file(922592622248341505, "song_history", song_history)
	await upload_file(993332319454760960, "video_info", video_info)
	await upload_file(999117002323001354, "playlists", playlists)

	print("saved in " + str(round((datetime.datetime.now() - time).total_seconds() * 1000)) + "ms")

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

check_time()

with open('Token/filekey.key', 'rb') as filekey:
	key = filekey.read()

fernet = Fernet(key)

with open('Token/token.txt', 'rb') as enc_file:
    encrypted = enc_file.read()

handler = FileHandler(filename='Cache/discord.log', encoding='utf-8', mode='w')
snoo.run(fernet.decrypt(encrypted).decode('UTF-8'), log_handler = handler)