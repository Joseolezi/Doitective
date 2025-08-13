# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
#ui.py
# Doitective - Herramienta de gestión de referencias bibliográficas
from colorama import Fore, Back, Style, init
import utils.style.styles as s
init(autoreset=True)
import modules.memory as m
# EFFICIENT STYLED PRINTING #
import modules.memory as memory


MAIL_TO: None

input_command = (s.success + f">>>>> " + s.dim_white + f"Enter your command here " + s.success + f"➤  ")

def not_valid_input (users_prompt, valid_ins):
    print(s.error + f"✘ Invalid input. Please input a valid commnad ✘")
    user_input = input(users_prompt)
    x = valid_ins.keys()
    if user_input in (x):
        returns = valid_ins.get(user_input)
        return returns
    else: not_valid_input(users_prompt, valid_ins)


separator = '\n↓-↓-↓-↓-↓--↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓-↓\n'

def styled_print(*segments, sep='', end='\n'):
    """
    Imprime múltiples segmentos con estilo sin errores de concatenación.
    Cada segmento puede ser una string normal o una variable de estilo.
    """
    print(sep.join(str(s) for s in segments), end=end)

def update_UI (key):
    if key == 'w':
        mailto = m.get('mailto')
      # welcome menu   
        print("\t" + s.warning + f" Welcome to " + s.success + "👣 Doitective 🔍👀 " + s.dim_white + f"{s.version} by {s.author}  \n")
        print(s.info + f"» This project is " + s.success + f"open source " + s.info + f"under the " + s.success
               + f"mit license ") 
        print(s.info + f"» Feel free to contribute " + s.magenta + "joseolezi.github.io/code" + " 🚀 \n")
        print(s.dim_white + f"You can use your e-mail 📧 adress to get the best " + s.success + "👣 Doitective 🔍👀 and OAPI " + s.dim_white + "performance and support 💚")
        if mailto != None:
            print(f"Doitective has detected a .txt file with a valid e-mail and will use it for future searches as ID for OAPI calls") 
            print(f"Mailto: " + s.success + f"{mailto}" + s.dim_white + " If this is wrong or not you, please note that 👣 Doitective 🔍👀 feelings could get hurt\n")
            print(s.info + f"Willing to support and keep track of updates or new open projects? " + s.dim_white + "type " + s.success + "'support' " + s.dim_white + "to apply to Olezi early access comunity\n")
        user_input = input("\n" + s.success + ">>>>> " + s.dim_white + "Enter any key " + s.success + "➤  ")
        if user_input != None:
            return 'i'
        else:
            print("Invalid input. Please try again.")

       # What does doitective do menu
    elif key == 'i':
        v_inputs = {}
        print(separator)
        print(s.success + f" Doitective " + s.dim_white + "will examine all supported files within the "  + s.magenta + f"📂[__RAW_DATA__ ]📂 folder 🔍👀\n")
        print(s.success + f"» 1 » " + s.dim_white + f"Merge all records and " + s.subtitle + f"deduplicate " + s.dim_white + "them 🧦")
        print(s.success + f"» 2 » " + s.dim_white + f"Batch call weak records to " + s.subtitle + f"OpenAlex API [OAPI] " + s.dim_white + f"to get the most updated and complete information of each  📚")
        print(s.success + f"» 2 » " + s.subtitle + f"Find the best OA option and URL " + s.dim_white + f"for each publication, scanning all OAPI open access fields and pdf urls by tier")
        print(s.success + f"» 3 » " + s.dim_white + f"Screens " + s.success + f"🧠 Open Access " + s.dim_white + f"from " + s.error + "💸 Restricted access " + s.dim_white + "records and outputs a 3 sheet .xlsx file and 3 .csv files: ↲")
        print('')
        print("    " + s.success + f"🧠 Unique_Open_Access (Diamond, Gold, Hybrid gold, Green and Bronze)")
        print("    " + s.error + f"🚧 Unique_Restricted_Access (Restricted or Closed)")
        print("    " + s.info + f"🧦 Duplicated records ") 
        print("    " + s.dim_white + f"⁉ Not Articles and Ineligible Records")
        print('')
        print(s.warning + f"\t>>>> [con] ➤  " + s.dim_white + f"Continue")
        print (s.error + f"\t>>>>[exit] ➤  " + s.dim_white + f"Quit and close console \n")
        user_input = input(input_command).strip().lower()
        if user_input == 'con':
            return 'l' 
        elif user_input == 'exit':
            print("Exiting Doitective 👣🔍👀💼 Goodbye!")
            return user_input  
        else:
            v_inputs = {'con':'l', 'exit':'exit'}
            returns = not_valid_input (input_command, v_inputs)
            return returns  
        
    # Launching menu
    elif key == 'l':
        
        print(separator)
        print("\t" + s.highlight + "\t\t 📄 INSTRUCTIONS 📄 \t\t\n")
        print(s.success + f"» 1 » " + s.dim_white + f"Place all the files you want to screen inside the folder: " + s.magenta + f"📂[__RAW_DATA__ ]📂 🔍👀")
        print(s.success + f"     ✓ " + s.dim_white + f"Supported file formats: " + s.success + f".csv .xls .xlxs \n"
            + s.success + f"     ✓ " + s.dim_white + f"Known databases: " + s.success + f"⭐ EBSCO ⭐ PubMed ⭐ Scopus ⭐ World of Sience ⭐ PsyNet ⭐ Cochrane ⭐\n" +
              s.success + f"     ✓ " + s.dim_white + f"Doitective tracks DOI (preferred), PMID or TITLE if previous is missing." + s.warning + "If none of these is valid, the record will be tagged as 'Unknown' 🤔")
        print(s.success + f"» 2 » " + s.success + f"For the best performance: " + s.dim_white + "make sure there is a .txt file with only your e-mail in the app folder. Name the txt file 'mailto' 📧")
        print(s.success + f"» 3 » " + s.dim_white + f"Check the " + s.success + f"📂[__SCREENED_DATA__]📂 " + s.dim_white + f"folder to find your screened data once Doitective is done processing 🔍👀\n")
        print(s.warning + f" ⚠ " + f" WARNING: " + s.dim_white + f"Make sure all the files with the data you want to merge are " + s.info + "INSIDE THE FOLDER " + s.magenta + f"📂[__ RAW_DATA__]📂")
        print(s.info + f" ✓ " + f"REMEMBER: " + s.dim_white + f"You may use your e-mail adress to get the best " + s.success + f"Doitective and OAPI performance and show support 💚\n" + 
              s.magenta + "If you forgot settiong your e-mail for better performance and avoid throttling, you can enter it now to launch the screener")
        print('')
        print(s.warning + f"\t>>>> [start] ➤  " + s.dim_white + f"Launch the screener")
        print (s.error + f"\t>>>> [exit]  ➤  " + s.dim_white + f"Quit and close console \n")
        user_input = input(s.success + f">>>>> " + s.dim_white + f"Enter your command here " + s.success + f"➤  ").strip().lower()
        if user_input == 'start':
            print("Processing your files...👀")
            return 'launch' 
        elif user_input == 'exit':
            
            return user_input  
        else:
            print(s.error + f"✘ Invalid input. Please type 'start' to begin or 'exit' to quit. ✘")
            return ('l')
    else: 
        print(f"✘ Invalid input. Please try again. ✘")
        return key