from SmartConsole import *
from tkinter import *

class main:
    def __init__(self):
        # setup smart console
        self.sc = SmartConsole("Chemicals-Manager", "3.0")
        
        # create main menu
        self.sc.main_menu["PRINT YELLOW LABEL"] = self.yellow_lbl
        self.sc.main_menu["STOCKCOUNT"] = self.stock_count
        self.sc.main_menu["GENERATE REPORTS"] = self.generate_html_reports

        # setup a directoy and make sure all paths exist
        self.loc_chemicals = self.sc.get_setting("Chemicals location")
        self.sc.test_path(self.loc_chemicals)

        # setup databases
        self.Chemicals = self.sc.csv_to_dict(self.loc_chemicals+"/Chemicals.csv", ("PART NUMBER","DESCRIPTION","STORAGE CONDITIONS","NICKNAME","FRIDGE","MSDS"))
        self.Lots = self.sc.csv_to_dict(self.loc_chemicals+"/Lots.csv", ("LOT NUMBER","PART NUMBER","EXPIRATION DATE"))
        self.Stock = self.sc.csv_to_dict(self.loc_chemicals+"/Stockcount.txt", ("LOT", "QTY"))
        
        # related_files
        self.file_yellow_lbl = self.loc_chemicals+"/LBL Chemical Closet AR00162 Yellow Label.btw"
        self.file_yellow_lbl_csv = self.loc_chemicals+"/YellowLabel.csv"
        self.file_stock_count = self.loc_chemicals+"/Stockcount.txt"

        self.sc.test_path(self.file_yellow_lbl)
        self.sc.test_path(self.file_yellow_lbl_csv)
        self.sc.test_path(self.file_stock_count)

        # run main menu
        self.sc.start()

        # run gui
        self.sc.gui()

    def yellow_lbl(self):
        # get lot number
        lot = self.sc.input("Insert LOT NUMBER").upper()
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
        file = open(self.file_yellow_lbl_csv, 'w')
        file.write("PART NUMBER,LOT NUMBER,STORAGE CONDITIONS,EXPIRATION DATE,NICKNAME\n")
        file.write(pn+","+lot+","+sc+","+exp+","+nickname)
        file.close()
        os.popen(self.file_yellow_lbl)

        # update stock-count
        if lot in self.Stock:
            self.Stock[lot] = int(self.Stock[lot][0])
            self.Stock[lot] += 1
        else:
            self.Stock[lot] = 1
        file = open(self.file_stock_count, 'w')
        for key, val in self.Stock.items():
            try:
                file.write(key+","+str(val[0])+"\n")
            except:
                file.write(key+","+str(val)+"\n")
        file.close()
        self.sc.print("Stock-count was successfully updated!")
        
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
                    self.sc.error("LOT NUMBER: "+lot+" is not in the database")
                else:
                    pn = self.Lots[lot][0]
                    if not pn in self.Chemicals:
                        self.sc.error("PART NUMBER: "+pn+" is not in the database")
                    else:
                        PART_NUMBER = pn
                        STORAGE_CONDITIONS = self.Chemicals[pn][1]
                        NICKNAME = self.Chemicals[pn][2]
                        FRIDGE = self.Chemicals[pn][3]
                        LOT_NUMBER = lot
                        EXPIRATION_DATE = self.Lots[lot][1]
                        if self.sc.test_date(EXPIRATION_DATE):
                            compare_dates = self.sc.compare_dates(EXPIRATION_DATE, self.sc.today())
                            if compare_dates < 6 and compare_dates > 0:
                                self.sc.error("LOT NUMBER: "+lot+" will expire in: "+str(compare_dates)+" days")
                            if compare_dates <= 0:
                                self.sc.error("LOT NUMBER: "+lot+" IS expired!")
                        QTY = 0
                        if not lot in stock:
                            stock[lot] = 1
                        else:
                            stock[lot] += 1
                        QTY = stock[lot]
                        self.sc.print(PART_NUMBER+"  |  "+LOT_NUMBER+"  |  "+STORAGE_CONDITIONS+"  |  "+EXPIRATION_DATE+"  |  "+NICKNAME+"  |  "+str(QTY))
                        if pn != current_pn:
                            if current_pn != "INITIAL_VALUE":
                                self.sc.notice("Not the same chemical!")
                            current_pn = pn
        if self.sc.question("Would you like to save the current stock count?"):
            file = open(self.file_stock_count, 'w')
            for key, val in stock.items():
                file.write(key+","+str(val)+"\n")
            file.close()
            self.sc.print("Stock-count was successfully updated!")
            self.Stock = self.sc.csv_to_dict(self.loc_chemicals+"/Stockcount.txt", ("LOT", "QTY"))
            self.generate_html_reports()
    
    def generate_html_reports(self):
        # generate html
        fridge_report = []
        closet_report = []
        for LOT_NUMBER, QTY in self.Stock.items():
            QTY = QTY[0]
            PART_NUMBER = self.Lots[LOT_NUMBER][0]
            DESCRIPTION = self.Chemicals[PART_NUMBER][0]
            STORAGE_CONDITIONS = self.Chemicals[PART_NUMBER][1]
            FRIDGE = self.Chemicals[PART_NUMBER][3]
            MSDS = self.Chemicals[PART_NUMBER][4]
            EXPIRATION_DATE = self.Lots[LOT_NUMBER][1]
            report_string = [PART_NUMBER,DESCRIPTION,STORAGE_CONDITIONS,MSDS,LOT_NUMBER,EXPIRATION_DATE,QTY]
            if FRIDGE == "Y":
                fridge_report.append(report_string)
            if FRIDGE == "N":
                closet_report.append(report_string)
        
        # make html
        self.make_html(self.loc_chemicals+"/Chemical-Fridge.html", fridge_report)
        self.make_html(self.loc_chemicals+"/Chemical-Closet.html", closet_report)

        # restart
        self.sc.restart()
    
    def make_html(self, location, data):
        file = open(location, 'w')
        for line in data:
            PART_NUMBER = line[0]
            DESCRIPTION = line[1]
            STORAGE_CONDITIONS = line[2]
            MSDS = line[3]
            LOT_NUMBER = line[4]
            EXPIRATION_DATE = line[5]
            QTY = line[6]
            print(PART_NUMBER,DESCRIPTION,STORAGE_CONDITIONS,MSDS,LOT_NUMBER,EXPIRATION_DATE,QTY)
            file.write(PART_NUMBER+" "+DESCRIPTION+" "+STORAGE_CONDITIONS+" "+MSDS+" "+LOT_NUMBER+" "+EXPIRATION_DATE+" "+QTY)
        file.close()
        os.popen(location)
main()