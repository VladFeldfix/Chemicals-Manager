import os
import sys
import datetime
from datetime import date as date_n
import re
class SmartConsole:
    # CONSTRUCTOR
    def __init__(self, name, version):
        self.title = name+" v"+version
        self.main_menu = {}
        self.__load_settings()

    # FLOW
    def start(self):
        # clear console
        os.system('cls')

        # display title
        self.print("---"+"-"*len(self.title)+"---")
        self.print("-- "+self.title+" --")
        self.print("---"+"-"*len(self.title)+"---")

        # display main menu
        self.main_menu["SETTINGS"] = self.open_settings
        self.main_menu["HELP"] = self.help
        self.main_menu["EXIT"] = self.exit
        self.print("MAIN MENU:")
        item = 0
        options = {}
        for key, value in self.main_menu.items():
            item += 1
            self.print(str(item)+". "+key)
            options[str(item)] = value
        
        # get input
        ans = self.input("Insert your choice")
        if ans in options:
            options[ans]()
        else:
            self.error("Invalid selection")
            self.restart()
            return
    
    def restart(self):
        self.input("Press ENTER to restart")
        self.start()
    
    def exit(self):
        self.input("Press ENTER to exit")
        os._exit(1)
        sys.exit()
    
    # INPUT
    def input(self, text):
        return input(text+" >")
    
    def question(self, text):
        ans = self.input(text+" [Y/N]").upper()
        if not ans in ("Y", "N"):
            self.error("Invalid answer!")
            self.question(text)
        else:
            return ans == "Y"

    # OUTPUT
    def print(self, text):
        print(text)

    def error(self, text):
        self.print("ERROR "+text)
    
    def fatal_error(self, text):
        self.print("ERROR! "+text)
        self.exit()
    
    # SETTINGS
    def __load_settings(self):
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
                        self.__loaded_settings[line[0].strip()] = line[1].strip()
    
    def open_settings(self):
        os.popen("settings.txt")

    def get_setting(self, var):
        if var in self.__loaded_settings:
            return self.__loaded_settings[var]
        else:
            self.fatal_error("Missing setting: "+var)

    # HELP
    def help(self):
        os.popen("help.pdf")
    
    # FILE HANDLER
    def test_path(self, path):
        if not os.path.isdir(path) and not os.path.isfile(path):
            self.fatal_error("Missing path: "+path)

    # DATABASES
    def save_database(self, path, data):
        self.test_path(path)
        file = open(path, 'w')
        for key, values in data.items():
            valstowrite = ""
            for val in values:
                valstowrite += val+","
            valstowrite = valstowrite[:-1]
            file.write(key+","+valstowrite+"\n")
        file.close()

    def load_database(self, path, headers):
        return_value = {}
        self.test_path(path)
        file = open(path, 'r')
        lines = file.readlines()
        file.close()
        ln = 0
        if len(lines) > 0:
            for line in lines:
                ln += 1
                line = line.replace("\n", "")
                line = line.split(",")
                if len(line) != len(headers):
                    self.fatal_error("in file: "+path+"\nIn line #"+str(ln)+"\nIncorrect number of values\nMake the file according to the following format:\n"+str(headers))
                else:
                    if ln == 1:
                        i = 0
                        for h in line:
                            if h != headers[i]:
                                self.fatal_error("in file: "+path+"\nIn line #"+str(ln)+"\nInvalid header\nGiven: '"+h+"' Expected: '"+headers[i]+"'")
                            i += 1
                    key = line[0]
                    values = line[1:]
                    if not key in return_value:
                        return_value[key] = values
                    else:
                        self.fatal_error("in file: "+path+"\nIn line #"+str(ln)+"\nPrimary key: "+key+" is not unique")
        else:
            ln += 1
            self.fatal_error("in file: "+path+"\nIn line #"+str(ln)+"\nFile is empty")
        return return_value

    # DATE
    def today(self):
        # get today
        now = datetime.datetime.now()
        yyyy = str(now.year)
        mm = str(now.month).zfill(2)
        dd = str(now.day).zfill(2)
        return yyyy+"-"+mm+"-"+dd
    
    def test_date(self, givenDate):
        # make sure the format is correct
        tmp = givenDate.replace("-","")
        tmp = re.sub('[^0-9]','', tmp)
        if len(tmp) < 8:
            self.error("Invalid date format: "+givenDate)
            return False
        
        # test year format
        YYYY = int(tmp[0:4])
        if not YYYY in range(0,10000):
            self.error("Invalid year format: "+str(YYYY)+" acceptable range 0-9999")
            return False
        YYYY = str(YYYY)
        YYYY = YYYY.zfill(4)

        # test month format
        MM = int(tmp[4:6])
        if not MM in range(1,13):
            self.error("Invalid month format: "+str(MM)+" acceptable range 1-12")
            return False
        MM = str(MM)
        MM = MM.zfill(2)

        # test day format
        DD = int(tmp[6:8])
        if not DD in range(1,32):
            self.error("Invalid day format: "+str(DD)+" acceptable range 1-31")
            return False
        DD = str(DD)
        DD = DD.zfill(2)
        
        # return true if date is good
        return True

    def compare_dates(self, firstDate, secondDate):
        if self.test_date(firstDate) and self.test_date(secondDate):
            firstDate = firstDate.replace("-","")
            secondDate = secondDate.replace("-","")
            date1 = date_n(int(firstDate[0:4]), int(firstDate[4:6]), int(firstDate[6:8]))
            date2 = date_n(int(secondDate[0:4]), int(secondDate[4:6]), int(secondDate[6:8]))
            return (date1 - date2).days
        else:
            return 0