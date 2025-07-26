#user_interface.py
# Doitective - Herramienta de gestión de referencias bibliográficas
from colorama import Fore, Back, Style, init
import style as s
init(autoreset=True)
import g_vars as v
# EFFICIENT STYLED PRINTING #
import g_vars
MAIL_TO: None

def styled_print(*segments, sep='', end='\n'):
    """
    Imprime múltiples segmentos con estilo sin errores de concatenación.
    Cada segmento puede ser una string normal o una variable de estilo.
    """
    print(sep.join(str(s) for s in segments), end=end)

def update_UI (key):
    if key == 'w':
        
        print(" " + s.success + f"👣 Welcome to Doitective 🔍👀  {s.version} by {s.author}  \n")
        print(s.info + f"» This project is " + s.success + f"open source " + s.info + f"under the " + s.success
               + f"mit license ") 
        print(s.info + f"» Feel free to contribute " + s.magenta + "joseolezi.github.io/code" + " 🚀 \n")
        print(s.success + f"You can use your e-mail adress to get the best " + s.success + "Doitective and OAPI " + s.dim_white + "performance and support " + s.error + "❤")
        print(s.success + f"  Doitective will take all supported files within the RAW FILES folder and investigate all found DOIs to: 🔍👀\n")
        print(s.success + f"» 1 » " + s.dim_white + f"Merge all records and " + s.subtitle + f"deduplicate " + s.dim_white + "them 🧦")
        print(s.success + f"» 2 » " + s.dim_white + f"Batch call weak records to " + s.subtitle + f"OpenAlex API [OAPI] " + s.dim_white + f"to get the most updated and complete information of each  📚")
        print(s.success + f"» 2 » " + s.subtitle + f"Find the best OA option and URL " + s.dim_white + f"for each publication, scanning all OAPI open access fields and pdf urls by tier")
        print(s.success + f"» 3 » " + s.dim_white + f"Screens " + s.success + f"🧠 Open Access " + s.dim_white + f"from " + s.error + "💸 Restricted access " + s.dim_white + "records and outputs a 3 sheet .xlsx file and 3 .csv files: ↲")
        print("    " + s.success + f"🧠 Unique_Open_Access (Diamond, Gold, Green)")
        print("    " + s.error + f"💸 Unique_Restricted_Access (Hybrid, Bronze, Closed)")
        print("    " + s.info + f"🧦 Duplicated records ") 

        user_input = input("\n" + s.success + ">>>>> " + s.dim_white + "Enter any key to start using Doitective " + s.success + "➤  ")
        if user_input != None:
            return 'i'
        else:
            print("Invalid input. Please try again.")
    elif key == 'i':
        print('\n\n\n\n\n\n\n\n')
        print("\t" + s.highlight + " 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 ")
        print(s.success + f"» 1 » " + s.dim_white + f"Place all the files you want to screen inside the folder: " + s.magenta + f"📂[__RAW_DATA__ ]📂 🔍👀")
        print(s.success + f"     ✓ " + s.dim_white + f"Supported file formats: " + s.success + f".csv .xls .xlxs \n"
              + s.success + f"     ✓ " + s.dim_white + f"Known databases: " + s.success + f"⭐ EBSCO ⭐ PubMed ⭐ Scopus ⭐ World of Sience ⭐ PsyNet ⭐ Cochrane ⭐\n" +
              s.success + f"     ✓ " + s.dim_white + f"Doitective only needs the file to have one header named " + s.warning + "'DOI' with valid field values to work at its best 🎯 ")
        print(s.success + f"» 2 » " + s.success + f"For the best performance, type your email in the .txt file named 'mailto'. You can also create a new one, name it 'mailto' and type your email in")
        print(s.success + f"» 3 » " + s.dim_white + f"Check the " + s.success + f"📂[__SCREENED_DATA__]📂 " + s.dim_white + f"folder to find your screened data once Doitective is done processing 🔍👀\n")
        print(s.warning + f" ! " + s.error + f"WARNING: " + s.warning + f"Make sure all the files with the data you want to merge are " + s.info + "INSIDE THE FOLDER " + s.magenta + f"📂[__ RAW_DATA__]📂")
        print(s.dim_white + f"REMEMBER: You can use your e-mail adress to get the best " + s.success + "Doitective and OAPI performance and support " + s.error + "❤")
        print(s.warning + f"\t>>>> [start] ➤  " + s.dim_white + f"Launch the screener")
        print (s.error + f"\t>>>>  [exit] ➤  " + s.dim_white + f"Quit and close console \n")
        user_input = input(s.success + f">>>>> " + s.dim_white + f"Enter your command here " + s.success + f"➤  ").strip().lower()
        if user_input == 'start':
            print("Processing your files...👀")
            return user_input 
        elif user_input == 'exit':
            print("Exiting Doitective 👣🔍👀💼 Goodbye!")
            return user_input  
        else:
            print(s.error + f"✘ Invalid input. Please type 'start' to begin or 'exit' to quit. ✘")
            return ('i')
    else: 
        print(f"✘ Invalid input. Please try again. ✘")
        return key