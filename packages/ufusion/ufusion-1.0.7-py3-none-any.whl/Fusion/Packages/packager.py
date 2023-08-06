import os
import json
import time
from ui.menu import Menu

class Packager:
    def __init__(self, main_menu):
        self.main_menu = main_menu
        self.menu = Menu([], parent_menu=self.main_menu)
        self.run()

    def get_folders(self):
        current_path = os.path.join(os.getcwd(), "Packages")
        if not os.path.exists(current_path):
            return []
        folders = [name for name in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, name))]
        return folders

    def select_folder(self, folder):
        folder_path = os.path.join(os.getcwd(), "Packages", folder)
        json_file_path = os.path.join(folder_path, "Fusion.json")

        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                try:
                    data = json.load(file)
                    main_file = data.get("main")
                    if main_file:
                        main_file_path = os.path.join(folder_path, main_file)
                        if os.path.exists(main_file_path):
                            # Run the main Python file
                            os.system(f"python {main_file_path}")
                        else:
                            print("Main Python file not found.")
                    else:
                        print("No 'main' key found in Fusion.json.")
                except json.JSONDecodeError:
                    print("Error parsing Fusion.json.")
        else:
            print("Fusion.json file not found.\nmake sure you have Fusion.json file in your folder with the main file path ")

        time.sleep(2)
        self.menu.start()

    def run(self):
        folders = self.get_folders()
        options = [[folder, lambda folder=folder: self.select_folder(folder)] for folder in folders]
        options.append(["Back", self.menu.start])
        self.menu.options = options
        self.menu.start()

