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

admin_command_message = "you need to be my master to use this command!"
snoo_color = 0xe0917a
version = "0.4.34 (buttons) BETA"
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