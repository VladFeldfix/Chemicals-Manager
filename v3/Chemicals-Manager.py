from SmartConsole import *

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

        # give notices
        notice = False
        i = 0
        for lot, pn_exp in self.Lots.items():
            if i > 0:
                LOT_NUMBER = lot
                PART_NUMBER = pn_exp[0]
                EXPIRATION_DATE = pn_exp[1]
                if not PART_NUMBER in self.Chemicals:
                    self.sc.notice("For LOT NUMBER "+LOT_NUMBER+": PART NUMBER: "+PART_NUMBER+" Is not in the database")
                    notice = True
                if not LOT_NUMBER in self.Stock:
                    self.sc.notice("LOT NUMBER "+LOT_NUMBER+": Is not in stock")
                    notice = True
            i += 1
        if notice:
            self.sc.input("Press ENTER to continue")
        
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
        self.make_html(self.loc_chemicals+"/Chemical-Fridge.html", fridge_report, "תכולת מקרר חומרים")
        self.make_html(self.loc_chemicals+"/Chemical-Closet.html", closet_report, "תכולת ארון חומרים")

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
        file.write(".white{\n")
        file.write("    background-color:#ffffff;\n")
        file.write("}\n")
        file.write(".yellow{\n")
        file.write("    background-color:#e6d063;\n")
        file.write("}\n")
        file.write(".red{\n")
        file.write("    background-color:#d43737;\n")
        file.write("}\n")
        file.write(".black{\n")
        file.write("    background-color:#4a4a4a;\n")
        file.write("}\n")
        file.write("</style>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<h1>"+header+"</h1>\n")
        file.write("<table>\n")
        file.write("<tr>\n")
        file.write("<th>PN</th><th>DESCRIPTION</th><th>SC</th><th>MSDS</th><th>LOT</th><th>EXP</th><th>QTY</th>\n")
        file.write("</tr>\n")
        for line in data:
            PART_NUMBER = line[0]
            DESCRIPTION = line[1]
            STORAGE_CONDITIONS = line[2]
            MSDS = line[3]
            LOT_NUMBER = line[4]
            EXPIRATION_DATE = line[5]
            QTY = line[6]
            line_color = "white"
            if self.sc.test_date(EXPIRATION_DATE):
                compare_dates = self.sc.compare_dates(EXPIRATION_DATE, self.sc.today())
                if compare_dates < 6 and compare_dates > 0:
                    line_color = "yellow"
                if compare_dates <= 0:
                    line_color = "red"
            else:
                line_color = "black"
            file.write("<tr class="+line_color+">\n")
            file.write("<td>"+PART_NUMBER+"</td><td>"+DESCRIPTION+"</td><td>"+STORAGE_CONDITIONS+"</td><td>"+MSDS+"</td><td>"+LOT_NUMBER+"</td><td>"+EXPIRATION_DATE+"</td><td>"+QTY+"</td>\n")
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