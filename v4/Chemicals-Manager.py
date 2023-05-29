from SmartConsole import *
class main:
    # constructor
    def __init__(self):
        # load smart console
        self.sc = SmartConsole("Chemical Manager", "4.0")

        # settings / paths
        self.path_main_folder = self.sc.load_path("Chemicals folder")
        self.path_stockcount = self.sc.load_path(self.path_main_folder+"/Stockcount.txt")
        self.path_yellow_label = self.sc.load_path(self.path_main_folder+"/LBL Chemical Closet AR00162 Yellow Label.btw")
        self.path_yellow_label_csv = self.sc.load_path(self.path_main_folder+"/YellowLabel.csv")

        # main menu
        self.sc.set_main_menu(main_menu)

        # load databases
        self.CHEMICALS = self.sc.load_database()
        self.LOTS = self.sc.load_database()
        self.BOXES = self.sc.load_database()

        # display main menu NEW LOT, NEW PART NUMBER, NEW YELLOW LABEL, STOCK COUNT, GENERATE HTML REPORT
        self.sc.display_main_menu()

    def new_lot(self):
        # get lot number
        # make sure lot is not new
        # get part number
        # make sure part number exists
        # get exp date
        # validate exp
        # restart
        pass

    def new_part_number(self):
        # get pn
        # make sure pn is not new
        # get description
        # storage conditions
        # get short name
        # get msds number
        # get fridge y/n
        # restart
        pass

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