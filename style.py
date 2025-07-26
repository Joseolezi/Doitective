# style.py
# Información del proyecto
version = "1.0.0"
author = "jf2"
author_email = "jfan2@hotmail.com"
author_website = "joseolezi.github.io/<>"

from colorama import Fore, Back, Style, init
init(autoreset=True)

# =====================
# Project Metadata
# =====================
version = "1.0.0"
author = "jf2"
author_email = "jfan2@hotmail.com"
author_website = "joseolezi.github.io/<>"
author_patreon = "example_patreon_ex"
# =====================
# Text Styles & Colors
# =====================
title       = Fore.MAGENTA + Style.BRIGHT
subtitle    = Fore.YELLOW + Style.BRIGHT
info        = Fore.CYAN + Style.BRIGHT
success     = Fore.GREEN + Style.BRIGHT
warning     = Fore.YELLOW + Style.BRIGHT
error       = Fore.RED + Style.BRIGHT
prompt      = Fore.WHITE + Style.BRIGHT
highlight   = Back.BLUE + Fore.WHITE + Style.BRIGHT
shadow      = Back.BLACK + Fore.WHITE
negative    = Back.WHITE + Fore.BLACK

# Additional Color Variants
blue        = Fore.BLUE + Style.BRIGHT
dark_blue   = Fore.BLUE + Style.NORMAL
magenta     = Fore.MAGENTA + Style.NORMAL
dark_magenta= Fore.MAGENTA + Style.DIM
green       = Fore.GREEN + Style.NORMAL
dark_green  = Fore.GREEN + Style.DIM
cyan        = Fore.CYAN + Style.NORMAL
dark_cyan   = Fore.CYAN + Style.DIM
red         = Fore.RED + Style.NORMAL
dark_red    = Fore.RED + Style.DIM
yellow      = Fore.YELLOW + Style.NORMAL
dark_yellow = Fore.YELLOW + Style.DIM
white       = Fore.WHITE + Style.NORMAL
dim_white   = Fore.WHITE + Style.DIM
grey        = Fore.BLACK + Style.BRIGHT

# =====================
# Icons & Symbols
# =====================
i_success    = "✓"
i_warning    = "!"
i_error      = "✗"
i_info       = "»"
i_prompt     = ">"
i_enter      = "↲"
i_arrow      = "➤"
i_check      = "✔"
i_cross      = "❌"
i_question   = "❓"
i_exclam     = "❗"
i_hourglass  = "⏳"
i_time       = "⏱"
i_star       = "⭐"
i_folder     = "📂"
i_file       = "📄"
i_fire       = "🔥"
i_bolt       = "⚡"
i_lock       = "🔒"
i_unlock     = "🔓"
i_gear       = "⚙"
i_bug        = "🐞"
i_rocket     = "🚀"
i_clip       = "📎"
i_link       = "🔗"
i_books      = "📚"
i_eyes       = "👀"
i_thumbs_up  = "👍"
i_thumbs_down= "👎"
i_heart      = "❤"
i_pray       = "🙏"
i_brain      = "🧠"
i_mic        = "🎙"
i_speaker    = "🔈"
i_music      = "🎵"
i_flag       = "🚩"
i_keyboard   = "⌨"
i_terminal   = "🖥"
i_checklist  = "📋"
i_calendar   = "📅"
i_pen        = "🖊"
i_warning_sign = "🚫"
i_attention  = "⚠"
i_lightbulb  = "💡"
i_smile      = "😊"
i_sad        = "😢"
i_robot      = "🤖"
i_think      = "💭"
i_right      = "➡"
i_left       = "⬅"
i_up         = "⬆"
i_down       = "⬇"
i_thanks     = "🙌"

# =====================
# Misc
# =====================
reset = Style.RESET_ALL
key   = magenta
data  = cyan