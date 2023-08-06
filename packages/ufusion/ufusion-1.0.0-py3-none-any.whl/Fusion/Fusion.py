from Fusion.ui.menu import Menu
from Fusion.download.downloader import Downloader
from Fusion.Packages.packager import Packager
import json
class Fusion:
    def __init__(self):
        version = self.get_version()
        logo = f"""
       ______           _                
      / ____/_  _______(_)___  ____      
     / /_  / / / / ___/ / __ \/ __ \     
    / __/ / /_/ (__  ) / /_/ / / / /     
   /_/    \__,_/____/_/\____/_/ /_/      
        powered by f09l
        version {version}                               
        """                        
            
        main_menu = Menu([
            ["Downloader", lambda: Downloader(main_menu=main_menu)],
            ["Packages", lambda: Packager(main_menu=main_menu)],
            ["Exit", lambda:exit()]
        ],logo=logo)

        # Start the main menu
        main_menu.start()
    def get_version(self):
        try:
            with open("version.json") as f:
                    return json.load(f)["version"]
        except:
             return ""
Fusion()