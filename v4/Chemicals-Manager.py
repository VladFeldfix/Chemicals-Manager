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
        self.path_stockcount = self.path_main+"/Stockcount.txt"
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
        self.BOXES = self.sc.load_database(self.path_stockcount, ("BOXID",))

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
                self.sc.restart()
                return
            else:
                # get exp date
                exp = self.sc.input("Insert EXPIRATION DATE")
                if self.sc.compare_dates(exp, self.sc.today()) <= 0:
                    self.sc.error("This date invalid or expired!")
                    self.sc.restart()
                    return
                else:
                    self.LOTS[lot_number] = [part_number, exp]
                    self.sc.save_database(self.path_lots_csv ,self.LOTS)
                    self.sc.restart()
        else:
            self.sc.error("LOT NUMBER is not new")
            self.sc.restart()
            return
        # validate exp
        # restart

    def new_part_number(self):
        # get pn
        part_number = self.sc.input("Insert new PART NUMBER")
        
        # make sure pn is not new
        if part_number in self.CHEMICALS:
            self.sc.error("PART NUMBER is not new")
            self.sc.restart()
            return
        else:
            # get description
            description = self.sc.input("Insert DESCRIPTION")
            # storage conditions
            sc = self.sc.input("Insert STORAGE CONDITIONS")
            # get short name
            shortname = self.sc.input("Insert SHORTNAME")
            # get fridge y/n
            fridge = self.sc.question("Needs REFRIGERATION?")
            # get msds number
            msds = self.sc.input("Insert MSDS number")
            # update database "PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS"
            self.CHEMICALS[part_number] = [description, sc, shortname, fridge, msds]
            self.sc.save_database(self.path_chemicals_csv ,self.CHEMICALS)
            self.sc.restart()
        # restart
        self.sc.restart()

    def new_yellow_label(self):
        # get lot number
        # make sure lot number exists
        # print yellow label
        # restart
        pass
    
    def stockcount(self):
        # get box number
        # if the input is not == END
        # make sure box number in the database
        # if input is END
        # ask if user wants to save the stockcount
        # restart
        pass

    def generate_html_report(self):
        # generate html report
        # restart
        pass

main()