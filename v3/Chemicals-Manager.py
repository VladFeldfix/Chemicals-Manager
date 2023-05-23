from SmartConsole import *
from tkinter import *

class main:
    def __init__(self):
        # setup smart console
        self.sc = SmartConsole("Chemicals-Manager", "3.0")
        
        # create main menu
        self.sc.main_menu["PRINT YELLOW LABEL"] = self.yellow_lbl
        self.sc.main_menu["STOCKCOUNT"] = self.stock_count

        # setup a directoy and make sure all paths exist
        self.loc_chemicals = self.sc.get_setting("Chemicals location")
        self.sc.test_path(self.loc_chemicals)

        # setup databases
        self.Chemicals = self.sc.csv_to_dict(self.loc_chemicals+"/Chemicals.csv", ("PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS"))
        self.Lots = self.sc.csv_to_dict(self.loc_chemicals+"/Lots.csv", ("LOT NUMBER","PART NUMBER","EXPIRATION DATE"))
        
        # related_files
        self.yellow_lbl = self.loc_chemicals+"/LBL Chemical Closet AR00162 Yellow Label.btw"
        self.yellow_lbl_csv = self.loc_chemicals+"/YellowLabel.csv"
        self.stock_count = self.loc_chemicals+"/Stockcount.txt"

        self.sc.test_path(self.yellow_lbl)
        self.sc.test_path(self.yellow_lbl_csv)
        self.sc.test_path(self.stock_count)

        # run main menu
        self.sc.start()

        # run gui
        self.sc.gui()

    def yellow_lbl(self):
        # get lot number
        lot = self.sc.input("Insert LOT NUMBER")
        if not lot in self.Lots:
            self.sc.error("LOT NUMBER is not in the database")
            self.sc.abort()
            return
    
        # get part number
        pn = self.Lots[lot][0]
        if not pn in self.Chemicals:
            self.sc.error("PART NUMBER "+pn+" is not in the database")
            self.sc.abort()
            return
        
        # get sc exp and nickname
        # get sc
        sc = self.Chemicals[pn][1]
        # get exp
        exp = self.Lots[lot][1]
        # get nickname
        nickname = self.Chemicals[pn][2]

        # update yellow label csv
        file = open(self.yellow_lbl_csv, 'w')
        file.write("PART NUMBER,LOT NUMBER,STORAGE CONDITIONS,EXPIRATION DATE,NICKNAME\n")
        file.write(pn+","+lot+","+sc+","+exp+","+nickname)
        file.close()
        os.popen(self.yellow_lbl)
        
        # restart
        self.sc.restart()

    def stock_count(self):
        # start
        self.sc.print("Scan all chemicals using the yellow label barcode\nTo finish stock-count and save progress enter the word: END")
        lot = ""
        current_pn = "INITIAL_VALUE"
        stock = {}
        while lot != "END":
            # get lot
            lot = self.sc.input("Insert LOT NUMBER").upper()
            if lot != "END":
                if not lot in self.Lots:
                    self.sc.error("This LOT NUMBER is not in the database")
                else:
                    pn = self.Lots[lot][0]
                    if not pn in self.Chemicals:
                        self.sc.error("PART NUMBER "+pn+" is not in the database")
                    else:
                        DESCRIPTION = self.Chemicals[pn][0]
                        STORAGE_CONDITIONS = self.Chemicals[pn][1]
                        NICKNAME = self.Chemicals[pn][2]
                        FRIDGE = self.Chemicals[pn][3]
                        MSDS = self.Chemicals[pn][4]
                        EXPIRATION_DATE = self.Lots[lot][1]
                        QTY = 0
                        if not lot in stock:
                            stock[lot] = (1, FRIDGE)
                        else:
                            stock[lot][0] += 1
                        QTY = stock[lot][0]
                        self.sc.print(pn+"  |  "+lot+"  |  "+sc+"  |  "+exp+"  |  "+nickname+"  |  "+str(qty))
                        if pn != current_pn:
                            if current_pn != "INITIAL_VALUE":
                                self.sc.notice("Not the same chemical!")
                            current_pn = pn
        if self.sc.question("Would you like to save the current stock count?"):
            file = open(self.stock_count, 'w')
            for key, val in stock.items():
                file.write(key+" > "+str(val)+"\n")
            file.close()
            self.sc.print("Stock-count was successfully updated!")

            # generate html
        # restart
        self.sc.restart()
main()