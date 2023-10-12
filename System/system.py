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
# sources = {}
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

admin_command_message = "you are not allowed to use this command!"
snoo_color = 0xfab384
default_palette = ((255, 218, 174), (250, 179, 132), (207, 112, 91))
version = "0.4.38 (music stability)"
test_server = 905495146890666005
test_channel = 1046466554310701116
admin = 401442600931950592
# lang_set = "English"
lang_completion = {"English": 100}
title_format = "{}"

default_settings = {"lang_set": "English", "votes": True, "downvote": False}
settings_info = {
	"votes": {"dev": False},
	"downvote": {"dev": False},
    "lang_set": {"dev": True},
	# "slim nowplaying": {"dev": False},
	# "large nowplaying thumbnail": {"dev": False}
}

emojis = {
	"upvote": "<:Upvote:1124508818924118016>",
	"downvote": "<:Downvote:1124508816692756661>",
	"numbers": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"],
	"cross": "<:cross:905498493840400475>",
	"check": "<:check:905498494222098543>",
	"on": "<:on1:1124488396337860638><:on2:1124488399005433886>",
	"off": "<:off1:1124489547150000241><:off2:1124489549586903060>",
	"poll": ["<:A_:908477372397920316>", "<:B_:908477372637011968>", "<:C_:908477373090000916>", "<:D_:908477372607639572>", "<:E_:908477372561506324>", "<:F_:908477372511170620>", "<:G_:908477372829949952>"],
    "playbar": {
		"fills_and_caps": ["<:CapR:1124495141927911494>", "<:CapL:1124495139864334377>", "<:BodyR:1124498384619843615>", "<:BodyL:1124498381474107442>"],
		"focus_bars": {
			"cap_r": ["<:CapR1:1124498394614878330>", "<:CapR1:1124498394614878330>", "<:CapR2:1124498395575369728>", "<:CapR3:1124498687708631060>", "<:CapR4:1124731484947882026><:Center0:1124731486025814136>"],
			"body": ["<:Center4:1124731487086981252><:Center0:1124731486025814136>", "<:Center1:1124498784605458463>", "<:Center2:1124498786115387512>", "<:Center3:1124498787893780582>", "<:Center4:1124731487086981252><:Center0:1124731486025814136>"],
			"cap_l": ["<:Center4:1124731487086981252><:CapL0:1124731482947203154>", "<:CapL1:1124498388503777360>", "<:CapL2:1124498389887881216>", "<:CapL3:1124498390982594650>", "<:CapL3:1124498390982594650>"]
		},
	},
    "not_like": "<:NotLike:1125142767459389440>",
    "like": "<:Upvote:1124508818924118016>",
    "delete": "<:Trash:1125151486062628894>",
    "extend": "<:MenuUp:1125147518087483392>",
    "collapse": "<:MenuDown:1125147515835142215>",
    "back": "<:Back:1125143134976880740>",
    "skip": "<:Skip:1125143137355051068>",
    "pause": "<:Pause:1125136351063453756>",
    "play": "<:Play:1125136354028814366>"
}

new_playlist = {"title": "new playlist", "desc": "", "cover": "https://cdn.discordapp.com/attachments/908157040155832350/999112912352333854/snoo_cover.png", "songs": []}

loading_icon = "<a:Loading2:1124429339778351155>"
poll_icon = "https://cdn.discordapp.com/attachments/908157040155832350/1124407360471961700/Poll.png"
music_icon = "https://cdn.discordapp.com/attachments/908157040155832350/1124407819916025947/Music.png"
profile_icon = "https://cdn.discordapp.com/attachments/908157040155832350/1124408205032833034/Profile.png"
settings_icon = "https://cdn.discordapp.com/attachments/908157040155832350/1124406499230367914/Settings.png"
thumbnail_error = "https://cdn.discordapp.com/attachments/908157040155832350/1137151667826073731/Snoo_Thumbnail_Error.png"