from SmartConsole import *
class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("Chemical Manager", "4.0")

        # set-up main memu
        self.sc.main_menu["ADD NEW LOT"] = self.new_lot
        self.sc.main_menu["ADD NEW PART NUMBER"] = self.new_part_number
        self.sc.main_menu["PRINT NEW YELLOW LABEL"] = self.new_yellow_label
        self.sc.main_menu["DO STOCK-COUNT"] = self.stockcount
        self.sc.main_menu["GENERATE HTML REPORTS"] = self.generate_html_report

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
        self.CHEMICALS = self.sc.load_database(self.path_chemicals_csv, ("PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS"))
        self.LOTS = self.sc.load_database(self.path_lots_csv, ("LOT NUMBER","PART NUMBER","EXPIRATION DATE"))
        self.INVENTORY = self.sc.load_database(self.path_inventory, ("BOXID","LOT NUMBER", "INSTOCK"))

    def new_lot(self):
        # get lot number
        lot_number = self.sc.input("Insert new LOT NUMBER")

        # make sure lot is not new
        if not lot_number in self.LOTS:
            # get part number
            part_number = self.sc.input("Insert PART NUMBER")
            # make sure part number exists
            if not part_number in self.CHEMICALS:
                self.sc.error("this PART NUMBER is not in the database")
            else:
                # get exp date
                exp = self.sc.input("Insert EXPIRATION DATE")
                if self.sc.compare_dates(exp, self.sc.today()) <= 0:
                    self.sc.error("This date invalid or expired!")
                else:
                    self.LOTS[lot_number] = [part_number, exp]
                    self.sc.save_database(self.path_lots_csv ,self.LOTS)
                    self.sc.print("Database "+self.path_lots_csv+" Updated successfully!")
        else:
            self.sc.error("LOT NUMBER is not new")
        
        # restart
        self.sc.restart()

    def new_part_number(self):
        # get pn
        part_number = self.sc.input("Insert new PART NUMBER")
        
        # make sure pn is not new
        if part_number in self.CHEMICALS:
            self.sc.error("PART NUMBER is not new")
        else:
            # get description
            description = self.sc.input("Insert DESCRIPTION")
            # storage conditions
            sc = self.sc.input("Insert STORAGE CONDITIONS")
            # get short name
            shortname = self.sc.input("Insert SHORTNAME")
            # get fridge y/n
            if self.sc.question("Needs REFRIGERATION?"):
                fridge = "Y"
            else:
                fridge = "N"
            # get msds number
            msds = self.sc.input("Insert MSDS number")
            # update database "PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS"
            self.CHEMICALS[part_number] = [description, sc, shortname, fridge, msds]
            self.sc.save_database(self.path_chemicals_csv ,self.CHEMICALS)
            self.sc.print("Database "+self.path_chemicals_csv+" Updated successfully!")
        
        # restart
        self.sc.restart()

    def new_yellow_label(self):
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
            self.sc.error("LOT NUMBER is not in the database")
        else:
            # print yellow label
            file = open(self.path_yellow_lbl_csv, 'w')
            file.write("PART NUMBER,LOT NUMBER,STORAGE CONDITIONS,EXPIRATION DATE,NICKNAME,BOXID\n")
            # key PART NUMBER
            # 0 DESCRIPTION
            # 1 STORAGE CONDITIONS
            # 2 NICKNAME
            # 3 FRIDGE
            # 4 MSDS
            part_number = self.LOTS[lot_number][0]
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
        # ready current stock count
        stockcount = []

        # get box id
        box_id = self.sc.input("Scan yellow label [or insert END to finish stock-count]").upper()

        # if box id is END
        if box_id == "END":
            if self.sc.question("Would you like to save the current stock-count?"):
                # update stock
                for key, val in self.INVENTORY.items():
                    if key in stockcount:
                        self.INVENTORY[key][1] = "Y"
                    else:
                        self.INVENTORY[key][1] = "N"
                self.sc.save_database(self.path_inventory, self.INVENTORY)
                self.sc.print("Stock-count was successfully updated!")
            else:
                # abort
                self.sc.print("Stock-count aborted")
        else:
            if box_id in self.INVENTORY:
                # update tmp 
                stockcount.append(box_id)
            else:
                self.sc.error("Invalid BOX ID")

        # restart
        self.sc.restart()

    def generate_html_report(self):
        # generate html report
        # restart
        pass

main()