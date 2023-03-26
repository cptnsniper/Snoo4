from collections import defaultdict

prefix = ['!s ', 'hey snoo, ', 'hey snoo ', 'snoo, ', 'snoo ', 'Hey snoo, ', 'Hey snoo ', 'Snoo, ', 'Snoo ', 'Hey Snoo, ', 'Hey Snoo ', 'hey snoo, ', 'hey snoo ', 'snute ', 'Snute ', "nsnoo "]

profile_data = defaultdict(dict)
channel_messages = defaultdict(dict)
song_history = defaultdict(dict)
server_config = defaultdict(dict)
playlists = defaultdict(dict)
language = defaultdict(dict)
missing_translations = defaultdict(dict)
video_info = defaultdict(dict)
info = {}
default_info = {
	"channel": None,
	"voice": None,
	"paused": False,
	"looping": False,
	"autoplay": True,
	"shuffle": False,
	"queue": [],
	"past queue": [],
	"processing": False,
	"show_queue": False
}

admin_command_message = "you need to be my master to use this command!"
snoo_color = 0xe0917a
version = "0.4.36 (improvements)"
test_server = 905495146890666005
test_channel = 1046466554310701116
lang_set = "English"

default_settings = {"votes": True, "downvote": True, "slim nowplaying": True, "large nowplaying thumbnail": True}
settings_info = {
	"votes": {"dev": False},
	"downvote": {"dev": False},
	# "slim nowplaying": {"dev": False},
	# "large nowplaying thumbnail": {"dev": False}
}

emojis = {
	"upvote": "<:upvote:1076600305149546656>",
	"downvote": "<:downvote:1076600815004958770>",
	"numbers": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"],
	"cross": "<:cross:905498493840400475>",
	"check": "<:check:905498494222098543>",
	"on": "<:on1:985591109998759986><:on2:985591107524104324>",
	"off": "<:off1:985591110799884309><:off2:985591108929208320>",
	"poll": ["<:A_:908477372397920316>", "<:B_:908477372637011968>", "<:C_:908477373090000916>", "<:D_:908477372607639572>", "<:E_:908477372561506324>", "<:F_:908477372511170620>", "<:G_:908477372829949952>"],
	"bar1": "<:bar1:994058965279322144>",
	"bar2": ["<:bar31:994069492026048713>", "<:bar21:994063956178124882>", "<:bar2:994058964918616074>", "<:bar22:994063957117632572>", "<:bar12:994069492953010196>"],
	"bar3": "<:bar3:994058963509334018>",
	"bar1r": "<:bar1R:995467490052280320>",
	"bar2rR": ["<:bar31:994069492026048713>", "<:bar21r:995476810194223135>", "<:bar2r:995476813495152690>", "<:bar22r:995476811637067836>", "<:bar12r:995476812173942816>"],
	"bar2rL": ["<:bar31rr:995479103954239610>", "<:bar21rr:995479102066798612>", "<:bar2rr:995479104453361675>", "<:bar22rr:995479102976962695>", "<:bar12:994069492953010196>"],
	"bar3r": "<:bar3R:995467514144378992>"
}

new_playlist = {"title": "new playlist", "desc": "", "cover": "https://cdn.discordapp.com/attachments/908157040155832350/999112912352333854/snoo_cover.png", "songs": []}

loading_icon = "<a:loading:977336498322030612>"
poll_icon = "https://media.discordapp.net/attachments/908157040155832350/930606118512779364/poll.png"
music_icon = "https://cdn.discordapp.com/attachments/908157040155832350/930609037807087616/snoo_music_icon.png"
profile_icon = "https://media.discordapp.net/attachments/908157040155832350/931732724203520000/profile.png"
award_icon = "https://cdn.discordapp.com/attachments/908157040155832350/958841770765066280/award_icon.png"
settings_icon = "https://cdn.discordapp.com/attachments/908157040155832350/985595253174190080/snoo_icon.png"