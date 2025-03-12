# Download SmartConsole.py from: https://github.com/VladFeldfix/Smart-Console/blob/main/SmartConsole.py
from SmartConsole import *
from termcolor import colored
class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("Chemical Manager", "5.1")

        # set-up main memu
        self.sc.add_main_menu_item("DO STOCK-COUNT", self.stockcount)
        self.sc.add_main_menu_item("PRINT NEW YELLOW LABEL", self.new_yellow_label)
        self.sc.add_main_menu_item("GENERATE HTML REPORTS", self.generate_html_report)
        self.sc.add_main_menu_item("ADD NEW PART NUMBER", self.new_part_number)
        self.sc.add_main_menu_item("ADD NEW LOT", self.new_lot)

        # get settings
        self.path_main = self.sc.get_setting("Chemicals folder")
        self.path_inventory = self.path_main+"/Inventory.csv"
        self.path_yellow_lbl = self.path_main+"/LBL Chemical Closet AR00162 Yellow Label.btw"
        self.path_yellow_lbl_csv = self.path_main+"/YellowLabel.csv"
        self.path_lots_csv = self.path_main+"/Lots.csv"
        self.path_chemicals_csv = self.path_main+"/Chemicals.csv"

        # test all paths
        self.sc.test_path(self.path_main)
        self.sc.test_path(self.path_yellow_lbl)
        self.sc.test_path(self.path_yellow_lbl_csv)

        # load databases
        self.load_databases()

        # display main menu NEW LOT, NEW PART NUMBER, NEW YELLOW LABEL, STOCK COUNT, GENERATE HTML REPORT
        self.sc.start()
    
    def load_databases(self):
        # load databases
        self.CHEMICALS = self.sc.load_database(self.path_chemicals_csv, ("PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS","HARDNESS TEST"))
        self.LOTS = self.sc.load_database(self.path_lots_csv, ("LOT NUMBER","PART NUMBER","EXPIRATION DATE"))
        self.INVENTORY = self.sc.load_database(self.path_inventory, ("BOXID","LOT NUMBER", "INSTOCK"))

    def new_lot(self):
        self.load_databases()
        # get lot number
        lot_number = self.sc.input("Insert new LOT NUMBER").upper()

        if lot_number != "":
            # make sure lot is not new
            if not lot_number in self.LOTS:
                # get part number
                part_number = self.sc.input("Insert PART NUMBER").upper()
                # make sure part number exists
                if not part_number in self.CHEMICALS:
                    self.sc.error("this PART NUMBER is not in the database")
                else:
                    # get exp date
                    exp = self.sc.input("Insert EXPIRATION DATE [YYYY-MM-DD]")
                    if self.sc.compare_dates(exp, self.sc.today()) <= 0:
                        self.sc.error("This date invalid or expired!")
                    else:
                        self.sc.hr()
                        if self.sc.question("LOT NUMBER: "+lot_number+"\nPART NUMBER: "+part_number+"\nEXPIRATION DATE: "+exp+"\nWould you like to update the database?"):
                            self.LOTS[lot_number] = [part_number, exp]
                            self.sc.save_database(self.path_lots_csv ,self.LOTS)
                            self.sc.good("Database "+self.path_lots_csv+" Updated successfully!")
            else:
                self.sc.error("LOT NUMBER is not new")
        else:
            self.sc.error("Invalid LOT NUMBER")
        # restart
        self.sc.restart()

    def new_part_number(self):
        self.load_databases()
        # get pn
        part_number = self.sc.input("Insert new PART NUMBER").upper()
        
        if part_number != "":
            # make sure pn is not new
            if part_number in self.CHEMICALS:
                self.sc.error("PART NUMBER is not new")
            else:
                # get description
                description = self.sc.input("Insert DESCRIPTION")
                # storage conditions
                sc = self.sc.input("Insert STORAGE CONDITIONS [Or leave empty for ROOM TEMP]") or "ROOM TEMP"
                # get short name
                shortname = self.sc.input("Insert SHORTNAME")
                # get fridge y/n
                if self.sc.question("Needs REFRIGERATION?"):
                    fridge = "Y"
                else:
                    fridge = "N"
                # get msds number
                msds = self.sc.input("Insert MSDS number [Or leave empty for -N/A-]") or "-N/A-"
                # get hardness testing information
                hardness = self.sc.input("Insert hardness testing information [Or leave empty for -N/A-]") or "-N/A-"
                self.sc.hr()
                if self.sc.question("PART NUMBER: "+part_number+"\nDESCRIPTION: "+description+"\nSTORAGE CONDITIONS: "+sc+"\nREFRIGERATION: "+fridge+"\nMSDS: "+msds+"\nHARDNESS TESTING: "+hardness+"\nWould you like to update the database?"):
                    # update database "PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS"
                    self.CHEMICALS[part_number] = [description, sc, shortname, fridge, msds, hardness]
                    self.sc.save_database(self.path_chemicals_csv ,self.CHEMICALS)
                    self.sc.good("Database "+self.path_chemicals_csv+" Updated successfully!")
        else:
            self.sc.error("Invalid PART NUMBER")

        # restart
        self.sc.restart()

    def new_yellow_label(self):
        self.load_databases()
        # calculate last id
        box_id = 0
        ln = 0
        for key, val in self.INVENTORY.items():
            ln += 1
            if not key == "BOXID":
                try:
                    box_id = int(key)
                except:
                    self.sc.fatal_error("in file: "+self.path_inventory+"\nLine #"+str(ln)+"\nInvalid BOX ID: '"+str(key)+"' Numerical value expected")
        box_id += 1
        
        # get lot number
        lot_number = self.sc.input("Insert LOT NUMBER")

        # make sure lot number exists
        if not lot_number in self.LOTS:
            self.sc.error("LOT NUMBER: "+lot_number+" is not in the database")
            self.sc.restart()
            return
        
        # make sure there is a part number for this lot
        part_number = self.LOTS[lot_number][0]
        if not part_number in self.CHEMICALS:
            self.sc.error("PART NUMBER: "+part_number+" is not in the database")
            self.sc.restart()
            return

        # print yellow label
        file = open(self.path_yellow_lbl_csv, 'w')
        file.write("PART NUMBER,LOT NUMBER,STORAGE CONDITIONS,EXPIRATION DATE,NICKNAME,BOXID\n")
        # key PART NUMBER
        # 0 DESCRIPTION
        # 1 STORAGE CONDITIONS
        # 2 NICKNAME
        # 3 FRIDGE
        # 4 MSDS
        sc = self.CHEMICALS[part_number][1]
        exp = self.LOTS[lot_number][1]
        shortname = self.CHEMICALS[part_number][2]
        file.write(part_number+","+lot_number+","+sc+","+exp+","+shortname+","+str(box_id)+"\n")
        file.close()
        self.INVENTORY[str(box_id)] = [lot_number, "Y"]
        self.sc.save_database(self.path_inventory, self.INVENTORY)
        os.popen(self.path_yellow_lbl)
        
        # restart
        self.sc.restart()
    
    def stockcount(self):
        self.load_databases()
        # ready current stock count
        stockcount = []
        box_id = ""
        selected = ""
        # if box id is END
        while box_id != "END":
            # get box id
            box_id = self.sc.input("Scan yellow label [or insert END to finish stock-count]").upper()
            if box_id in self.INVENTORY:
                # update tmp 
                error = False
                # gather data
                
                # self.CHEMICALS
                # KEY PART NUMBER
                # 0 DESCRIPTION
                # 1 STORAGE CONDITIONS
                # 2 NICKNAME
                # 3 FRIDGE
                # 4 MSDS
                
                # self.LOTS
                # KEY LOT NUMBER
                # 0 PART NUMBER
                # 1 EXPIRATION DATE
                
                # self.INVENTORY
                # KEY BOXID
                # 0 LOT NUMBER
                # 1 INSTOCK
                lot_number = self.INVENTORY[box_id][0]
                part_number = "Not in database!"
                exp = "---"
                description = "---"
                sc = "---"
                fridge = "---"
                msds = "---"
                comment = ""
                
                if lot_number in self.LOTS:
                    part_number = self.LOTS[lot_number][0]
                    exp = self.LOTS[lot_number][1]
                else:
                    error = True
                
                if part_number in self.CHEMICALS:
                    description = self.CHEMICALS[part_number][0]
                    sc = self.CHEMICALS[part_number][1]
                    fridge = self.CHEMICALS[part_number][3]
                    if fridge == 'Y':
                        fridge = colored(" [*] FRIDGE", 'blue')
                    else:
                        fridge = ""
                    msds = self.CHEMICALS[part_number][4]
                else:
                    error = True
                
                if self.sc.test_date(exp):
                    compare_dates = self.sc.compare_dates(exp, self.sc.today())
                    if compare_dates < 6 and compare_dates > 0:
                        comment = colored("[!] About to expire", 'yellow')
                        error = True
                    if compare_dates <= 0:
                        comment = colored("[!] Expired", 'red')
                        error = True
                else:
                    error = True
                
                if part_number != selected:
                    if comment == "":
                        comment = colored("[!] Not the same as previous",'yellow')
                    else:
                        comment += colored("\n[!] Not the same as previous",'yellow')
                    selected = part_number
                #tmp = "***** Not added to inventory! *****"
                #Not_added_to_inventory = "*"*len(tmp)+"\n"+tmp+"\n"+"*"*len(tmp)
                Not_added_to_inventory = colored("[X] Not added to inventory",'red')
                if not error:
                    if comment == "":
                        comment = colored("[+] Added to inventory", 'green')
                    else:
                        comment += colored("\n[+] Added to inventory", 'green')
                else:
                    if comment == "":
                        comment = Not_added_to_inventory
                    else:
                        comment += "\n"+Not_added_to_inventory
                # display data
                #self.sc.print("BOXID: "+box_id+"\nPART NUMBER: "+part_number+"\nDESCRIPTION: "+description+"\nSTORAGE CONDITIONS: "+sc+"\nFRIDGE: "+fridge+"\nMSDS: "+msds+"\nLOT NUMBER: "+lot_number+"\nEXPIRATION DATE: "+exp+"\n"+comment)
                self.sc.print("#"+box_id+" "+part_number+" "+exp+fridge+"\n"+comment)
                if not error:
                    stockcount.append(box_id)
            else:
                if box_id != "END":
                    self.sc.error("Invalid BOX ID")
            self.sc.hr()
        if self.sc.question("Would you like to save the current stock-count?"):
            # update stock
            skip = True
            for key, val in self.INVENTORY.items():
                if not skip:
                    if key in stockcount:
                        self.INVENTORY[key][1] = "Y"
                    else:
                        self.INVENTORY[key][1] = "N"
                else:
                    skip = False
            self.sc.save_database(self.path_inventory, self.INVENTORY)
            self.sc.good("Stock-count was successfully updated!")
        else:
            # abort
            self.sc.warning("Stock-count aborted")
        # restart
        self.sc.restart()

    def generate_html_report(self):
        self.load_databases()
        # stock count
        stockcount = {}
        for box_id, arguments in self.INVENTORY.items():
            lot_number = arguments[0]
            in_stock = arguments[1]
            if not lot_number in stockcount:
                if in_stock == "Y":
                    stockcount[lot_number] = 1
                else:
                    stockcount[lot_number] = 0
            else:
                if in_stock == "Y":
                    stockcount[lot_number] += 1

        # generate report data
        fridge_report = []
        closet_report = []
        not_empty_part_numbers_fridge = []
        not_empty_part_numbers_no_fridge = []

        # get data for existing items
        for lot_number, arguments in self.LOTS.items():
            part_number = arguments[0]
            if part_number in self.CHEMICALS:
                description = self.CHEMICALS[part_number][0]
                sc = self.CHEMICALS[part_number][1]
                nickname = self.CHEMICALS[part_number][2]
                fridge = self.CHEMICALS[part_number][3]
                msds = self.CHEMICALS[part_number][4]
                hardness = self.CHEMICALS[part_number][5]
                exp = arguments[1]
                if lot_number in stockcount:
                    qty = str(stockcount[lot_number])
                else:
                    qty = "0"
                if qty != "0":
                    if fridge == "Y":
                        fridge_report.append((part_number, description, sc, msds, lot_number, hardness, exp, qty))
                        if not part_number in not_empty_part_numbers_fridge:
                            not_empty_part_numbers_fridge.append(part_number)
                    elif fridge == "N":
                        closet_report.append((part_number, description, sc, msds, lot_number, hardness, exp, qty))
                        if not part_number in not_empty_part_numbers_no_fridge:
                            not_empty_part_numbers_no_fridge.append(part_number)

        # get data for part numbers that have qty of zero
        for part_number, data in self.CHEMICALS.items():
            if part_number != "PART NUMBER":
                if not part_number in not_empty_part_numbers_fridge and not part_number in not_empty_part_numbers_no_fridge:
                    description = data[0]
                    sc = data[1]
                    fridge = data[3]
                    msds = data[4]
                    hardness = data[5]
                    if fridge == "Y":
                        fridge_report.append((part_number, description, sc, msds, "-N/A-", hardness, "-N/A-", "0"))
                    else:
                        closet_report.append((part_number, description, sc, msds, "-N/A-", hardness, "-N/A-", "0"))

        # make html
        self.make_html(self.path_main+"/Chemical-Fridge.html", fridge_report, "תכולת מקרר חומרים")
        self.make_html(self.path_main+"/Chemical-Closet.html", closet_report, "תכולת ארון חומרים")

        # restart
        self.sc.restart()
    
    def make_html(self, location, data, header):
        file = open(location, 'w', encoding = "utf-8")
        file.write("<html>\n")
        file.write("<head>\n")
        file.write("<style>\n")
        file.write("body{\n")
        file.write("    font-family:Arial;\n")
        file.write("}\n")
        file.write("table{\n")
        file.write("    border:black solid 1px;\n")
        file.write("    text-align:left;\n")
        file.write("    border-collapse:collapse;\n")
        file.write("    margin:auto;\n")
        file.write("}\n")
        file.write("table td{\n")
        file.write("    border:black solid 1px;\n")
        file.write("    padding:5;\n")
        file.write("    font-size:10pt;\n")
        file.write("}\n")
        file.write("table th{\n")
        file.write("    border:black solid 1px;\n")
        file.write("    padding:5;\n")
        file.write("    background-color:black;\n")
        file.write("    color:white;\n")
        file.write("}\n")
        file.write("h1{\n")
        file.write("    text-align:center;\n")
        file.write("}\n")
        file.write("</style>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<h1>"+header+"</h1>\n")
        file.write("<table>\n")
        file.write("<tr>\n")
        file.write("<th>PN</th><th>DESCRIPTION</th><th>SC</th><th>MSDS</th><th>HARDNESS TEST</th><th>LOT</th><th>EXP</th><th>QTY</th>\n")
        file.write("</tr>\n")
        for line in data:
            PART_NUMBER = line[0]
            DESCRIPTION = line[1]
            STORAGE_CONDITIONS = line[2]
            MSDS = line[3]
            LOT_NUMBER = line[4]
            HARDNESS_TEST = line[5]
            EXPIRATION_DATE = line[6]
            QTY = line[7]
            comment = ""
            if EXPIRATION_DATE != "-N/A-":
                if self.sc.test_date(EXPIRATION_DATE):
                    compare_dates = self.sc.compare_dates(EXPIRATION_DATE, self.sc.today())
                    if compare_dates < 6 and compare_dates > 0:
                        comment = "About to expire"
                    if compare_dates <= 0:
                        comment = "Expired"
                else:
                    comment = "Invalid expiration date"
            file.write("<tr>\n")
            file.write("<td>"+PART_NUMBER+"</td><td>"+DESCRIPTION+"</td><td>"+STORAGE_CONDITIONS+"</td><td>"+MSDS+"</td><td>"+HARDNESS_TEST+"</td><td>"+LOT_NUMBER+"</td><td>"+EXPIRATION_DATE+"  "+comment+"</td><td>"+QTY+"</td>\n")
            file.write("</tr>\n")
        file.write("</table>\n")
        file.write("</body>\n")
        file.write("</footer>\n")
        file.write("<br><br><br><p style='direction:rtl;'>בודק:___________</p>\n")
        file.write("<p style='direction:rtl;'>תאריך:"+self.sc.today()+"</p>\n")
        file.write("</footer>\n")
        file.write("</html>\n")
        file.close()
        os.popen(location)

main()