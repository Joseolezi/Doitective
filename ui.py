#user_interface.py
# OpenPrisma - Herramienta de gestión de referencias bibliográficas
from colorama import Fore, Back, Style, init
import style as s
init(autoreset=True)
# EFFICIENT STYLED PRINTING #

MAIL_TO: None

def styled_print(*segments, sep='', end='\n'):
    """
    Imprime múltiples segmentos con estilo sin errores de concatenación.
    Cada segmento puede ser una string normal o una variable de estilo.
    """
    print(sep.join(str(s) for s in segments), end=end)

def update_UI (key):
    if key == 'w':

        print("💠  " + s.info + f"Welcome to OpenPrisma {s.version} by {s.author} 💠\n")
        print(s.info + f"» This project is " + s.success + f"open source " + s.info + f"under the " + s.success
               + f"mit license " + s.info + f"with " + s.error + f"❤") 
        print(s.info + f"» Feel free to contribute " + s.magenta + "joseolezi.github.io/code" + " 🚀 \n")
        print(s.success + f" 🤖 OpenPrisma takes all supported files within the RAW FILES folder and: \n")
        print("\t " + s.success + f"» 1 » " + s.dim_white + f"Merges all records and " + s.subtitle + f"deduplicates " + s.dim_white + "them 🧦")
        print("\t " + s.success + f"» 2 » " + s.dim_white + f"With the unique list, batch calls by DOI groups to " + s.subtitle + f"OpenAlex API [OAPI] works endpoint " + s.dim_white + f"to get the most updated and complete information of each record 📚")
        print("\t " + s.success + f"» 2 » " + s.subtitle + f"Enriches all entries " + s.dim_white + f"by updating imprecise and empty fields. OpenPrisma only needs files with valid DOI fields to enrich the record")
        print("\t " + s.success + f"» 3 » " + s.dim_white + f"Screens " + s.success + f"🔓 Open Access " + s.dim_white + f"from " + s.error + "🚩 Paywall " + s.dim_white + "records and outputs a 3 sheet .xlsx file and 3 .csv files: ↲")
        print("\t    " + s.success + f"🧠 Unique_Open_Access ")
        print("\t    " + s.warning + f"🚩 Unique_Pay_Wall ")
        print("\t    " + s.error + f"🧦 Duplicates ") 

        user_input = input("\n\n" + s.success + ">>>>> " + s.dim_white + "Enter any key to start using OpenPrisma " + s.success + "➤  ")
        if user_input != None:
            return 'i'
        else:
            print("Invalid input. Please try again.")
    elif key == 'i':
        print('\n\n\n\n\n\n\n\n')
        print("\t" + s.highlight + " 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 INSTRUCTIONS 📄 \n")
        print(s.magenta + f"» 1 » " + s.dim_white + f"Place all the files you want to screen inside the folder: " + s.magenta + f"📂[__RAW_DATA__ ]📂")
        print(s.success + f"     ✓ " + s.info + f"Supported file formats: " + s.success + f".csv .xls .xlxs \n" 
              + s.success + f"     ✓ " + s.info + f"Known databases: " + s.success + f"⭐ EBSCO ⭐ PubMed ⭐ Scopus ⭐ World of Sience ⭐\n" + 
              s.success + f"     ✓ " + s.dim_white + f"OpenPrisma only needs the file to have one header named " + s.warning + "'DOI' with valid field values to work at its best 🔥")
        print(s.magenta + f"» 2 » " + s.dim_white + f"Run the script to process your files.")
        print(s.magenta + f"» 3 » " + s.dim_white + f"Check the " + s.success + f"📂[__SCREENED_DATA__]📂 " + s.dim_white + f"folder to find your screened data once OpenPrisma is done processing ⚙\n")
        print(s.warning + f" ! " + s.error + f"WARNING: " + s.warning + f"Make sure all the files with the data you want to merge are " + s.info + "INSIDE THE FOLDER " + s.magenta + f"📂[__ RAW_DATA__]📂\n")
        print(s.magenta + f"» 4 » " + s.dim_white + f"Available actions: ⌨")
        print(s.success + f" >>>>> [your e-mail] ➤  " + s.dim_white + f"Launch the screener with the best " + s.success + "OAPI " + s.dim_white + "performance and " + s.error + "❤")
        print(s.warning + f" >>>>> [launch] ➤  " + s.dim_white + f"Launch the screener with shame")
        print (s.info + f" >>>>> [es] ➤  " + s.dim_white + f"Change language to spanish")
        print (s.error + f" >>>>> [exit] ➤  " + s.dim_white + f"Quit and close console \n\n")
        user_input = input(s.success + f">>>>> " + s.dim_white + f"Enter your command here " + s.success + f"➤  ").strip().lower()
        if user_input == 'start':
            print("Processing your files...")
            return user_input 
        elif user_input == 'exit':
            print("Exiting OpenPrisma. Goodbye!")
            return user_input  
        else:
            print(s.error + f"✘ Invalid input. Please type 'start' to begin or 'exit' to quit. ✘")
            return ('i')
    else: 
        print(f"✘ Invalid input. Please try again. ✘")
        return key