from collections import defaultdict

prefix = ['!s ', 'hey snoo, ', 'hey snoo ', 'snoo, ', 'snoo ', 'Hey snoo, ', 'Hey snoo ', 'Snoo, ', 'Snoo ', 'Hey Snoo, ', 'Hey Snoo ', 'hey snoo, ', 'hey snoo ', 'snute ', 'Snute ']

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
	"processing": False
}

admin_command_message = "you need to be my master to use this command!"
snoo_color = 0xe0917a
version = "0.4.35 (cleanup)"
test_server = 905495146890666005
test_channel = 1046466554310701116
lang_set = "English"

default_settings = {"votes": True, "downvote": True, "slim nowplaying": True, "large nowplaying thumbnail": True}
settings_info = {
	"votes": {"dev": False},
	"downvote": {"dev": False},
	"slim nowplaying": {"dev": False},
	"large nowplaying thumbnail": {"dev": False}
}

emojis = {
	"upvote": "<:Upvote:919356607563972628>",
	"downvote": "<:Downvote:919357445770473503>",
	"numbers": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"],
	"cross": "<:cross:905498493840400475>",
	"check": "<:check:905498494222098543>",
	"on": "<:on1:985591109998759986><:on2:985591107524104324>",
	"off": "<:off1:985591110799884309><:off2:985591108929208320>",
	"poll": ["<:A_:908477372397920316>", "<:B_:908477372637011968>", "<:C_:908477373090000916>", "<:D_:908477372607639572>", "<:E_:908477372561506324>", "<:F_:908477372511170620>", "<:G_:908477372829949952>"]
}

new_playlist = {"title": "new playlist", "desc": "", "cover": "https://cdn.discordapp.com/attachments/908157040155832350/999112912352333854/snoo_cover.png", "songs": []}

loading_icon = "<a:loading:977336498322030612>"
poll_icon = "https://media.discordapp.net/attachments/908157040155832350/930606118512779364/poll.png"
music_icon = "https://cdn.discordapp.com/attachments/908157040155832350/930609037807087616/snoo_music_icon.png"
profile_icon = "https://media.discordapp.net/attachments/908157040155832350/931732724203520000/profile.png"
award_icon = "https://cdn.discordapp.com/attachments/908157040155832350/958841770765066280/award_icon.png"
settings_icon = "https://cdn.discordapp.com/attachments/908157040155832350/985595253174190080/snoo_icon.png"