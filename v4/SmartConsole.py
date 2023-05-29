import os
import sys

class SmartConsole:
    def __init__(self, name, version):
        # display title
        title = name+" v"+version
        print("---"+"-"*len(title)+"---")
        print("-- "+title+" --")
        print("---"+"-"*len(title)+"---")

        # load settings.txt
        if not os.path.isfile("settings.txt"):
            self.fatal_error("Missing file settings.txt")
        else:
            self.__loaded_settings = {}
            file = open("settings.txt")
            lines = file.readlines()
            file.close()
            for line in lines:
                line = line.replace("\n", "")
                if ">" in line:
                    line = line.split(">")
                    if len(line) == 2:
                        self.__loaded_settings[line[0]] = line[1]
    
    def load_path(self, pathname):
        if pathname in self.__loaded_settings:
            path = self.__loaded_settings[pathname]
            if not os.path.isdir(path) and not os.path.isfile(path):
                self.fatal_error("Missing path: "+path)
            else:
                return path
        else:
            self.fatal_error("Missing settings: "+pathname)
    
    def fatal_error(self, text):
        print("ERROR! "+text)
        self.exit()
    
    def exit(self):
        sys.exit()