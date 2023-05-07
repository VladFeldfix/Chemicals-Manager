# GENERAL INFORMATION
## Chemical Manager is a database management application designed to ADD, EDIT, DELETE, and COUNT STOCK for the chemical fridge and chemical closet.
## The application will allow you to manage the database, print yellow labels and stock reports

# HOW TO USE
## Download the application
## Set all the settings according to PART V
## Run Chemicals-Manager.exe file

from PersonalAssistant import *
from PersonalAssistant import FIELD
import os
import sqlite3

class main:
    def __init__(self):
        # set up Personal Assistant
        self.pa = PersonalAssistant(__file__, "Chemicals Manager", "2.0")
        
        # connect to database
        self.db_location = self.pa.get_setting("Database location")
        self.con = sqlite3.connect(self.db_location)
        self.cur = self.con.cursor()

        # create database tables
        self.cur.execute("CREATE TABLE IF NOT EXISTS chemicals (part_number VARCHAR(50), desc VARCHAR(100), sc VARCHAR(10), shortname VARCHAR(20), fridge VARCHAR(1), msds VARCHAR(50))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS chemical_lots (lot_number VARCHAR(50), part_number VARCHAR(50), exp VARCHAR(10))")
        self.cur.execute("CREATE VIEW IF NOT EXISTS dbview AS SELECT chemicals.part_number, chemicals.desc, chemical_lots.exp, chemical_lots.lot_number, chemicals.sc, chemicals.msds, chemicals.fridge, chemicals.shortname FROM chemicals, chemical_lots WHERE chemicals.part_number = chemical_lots.part_number")
        self.con.commit()

        # display database
        self.display_database()

        # MAIN MENU
        self.pa.main_menu["PRINT YELLOW LABEL"] = self.add
        self.pa.main_menu["EDIT"] = self.edit
        self.pa.main_menu["DELETE"] = self.delete
        self.pa.main_menu["STOCK COUNT"] = self.stock
        self.pa.display_menu()

        # run GUI
        self.pa.run()

    def display_database(self):
        self.pa.display_database(self.db_location, "dbview", "part_number")

    def add(self):
        ## PRINT YELLOW LABEL
        #- This will allow you to add a new LOT NUMBER to the database by filling a form
        #- At the end of the form press Y to submit the form and the new LOT NUMBER will be added to the database
        #- When form is successfully submitted the application will open bar tender to print a yellow label
        
        # get lot:
        lot_number = self.pa.input("Insert LOT NUMBER").upper() or "EMPTY LOT"
        self.cur.execute("SELECT * FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
        fetched_values = self.cur.fetchall()
        print_yellow_lbl = False
        add_lot = False
        if len(fetched_values) == 0:
            self.pa.error("LOT NUMBER is not in the database")
            if self.pa.question("Would you like to add a new LOT NUMBER?"):
                # see if part number exists
                part_number = self.pa.input("Insert PART NUMBER").upper() or "EMPTY PART NUMBER"
                self.cur.execute("SELECT * FROM chemicals WHERE part_number = '"+part_number+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    # add a new part number
                    if self.pa.question("PART NUMBER: "+part_number+" is not in the database, would you like to add it?"):
                        # create form add chemical
                        fields = {}
                        fields["PART NUMBER"] = FIELD("PART NUMBER", TEXT, part_number)
                        fields["PART NUMBER"].disabled = True
                        fields["DESCRIPTION"] = FIELD("DESCRIPTION", TEXT, "No Description")
                        fields["STORAGE CONDITIONS"] = FIELD("STORAGE CONDITIONS", TEXT, "Room Temp")
                        fields["SHORT NAME"] = FIELD("SHORT NAME", TEXT, "N/A")
                        fields["FRIDGE"] = FIELD("FRIDGE", CHOOSE, "N")
                        fields["FRIDGE"].options = ("Y", "N")
                        fields["MSDS"] = FIELD("MSDS", TEXT, "N/A")

                        # submit form
                        submit = self.pa.form(fields)

                        # proccess given information
                        if submit:
                            self.cur.execute("INSERT INTO chemicals (part_number, desc, sc, shortname, fridge, msds) VALUES ('"+str(submit["PART NUMBER"])+"','"+str(submit["DESCRIPTION"])+"','"+str(submit["STORAGE CONDITIONS"])+"','"+str(submit["SHORT NAME"])+"','"+str(submit["FRIDGE"])+"','"+str(submit["MSDS"])+"')")
                            self.con.commit()
                            self.pa.print("New PART NUMBER added successfully!")
                            add_lot = True
                        else:
                            self.pa.error("PART NUMBER adding aborted!")
                    else:
                        self.pa.error("PART NUMBER adding aborted!")
                else:
                    add_lot = True

            if add_lot:
                # create form add lot
                fields = {}
                fields["LOT NUMBER"] = FIELD("LOT NUMBER", TEXT, lot_number)
                fields["LOT NUMBER"].disabled = True
                fields["PART NUMBER"] = FIELD("PART NUMBER", TEXT, part_number)
                fields["PART NUMBER"].disabled = True
                fields["EXPIRATION DATE"] = FIELD("EXPIRATION DATE", DATE, self.pa.today())
            
                # submit form
                submit = self.pa.form(fields)
                
                # proccess given information
                if submit:
                    self.cur.execute("INSERT INTO chemical_lots (lot_number, part_number, exp) VALUES ('"+str(submit["LOT NUMBER"])+"','"+submit["PART NUMBER"]+"','"+str(submit["EXPIRATION DATE"])+"')")
                    self.con.commit()
                    self.pa.print("New LOT NUMBER added successfully!")
                    print_yellow_lbl = True
                else:
                    self.pa.error("LOT NUMBER adding aborted!")
            else:
                self.pa.error("LOT NUMBER adding aborted!")
        else:
            print_yellow_lbl = True
        
        # print yellow lbl
        if print_yellow_lbl:
            csv = self.pa.get_setting("Yellow Label CSV")
            path = self.pa.get_setting("Yellow Label filename")
            if os.path.isfile(path) and os.path.isfile(csv):
                file = open(csv, 'w')
                file.write("PART NUMBER,LOT,STORAGE CONDITIONS,EXPIRATION DATE,SHORT NAME\n")
                self.cur.execute("SELECT * FROM dbview WHERE lot_number = '"+lot_number+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    self.pa.fatal_error("Unexpected error!")
                else:
                    # 0 chemicals.part_number
                    # 1 chemicals.desc
                    # 2 chemical_lots.exp
                    # 3 chemical_lots.lot_number
                    # 4 chemicals.sc
                    # 5 chemicals.msds
                    # 6 chemicals.fridge
                    # 7 chemicals.shortname
                    data = fetched_values[0]
                    part_number = data[0]
                    lot_number = data[3]
                    sc = data[4]
                    exp = data[2]
                    short_name = data[7]
                    file.write(part_number+","+lot_number+","+sc+","+exp+","+short_name)
                file.close()
                os.popen(path)
            else:
                self.pa.fatal_error("Missing files: "+path+" or "+csv)

        # resptart
        if not self.pa.database_is_displayed():
            self.display_database()
        else:
            self.pa.update_database()
        self.pa.restart()
    
    def edit(self):
        ## EDIT
        #- This will allow you to edit an existing PART NUMBER by filling a form
        #- At the end of the form press Y to submit the form and the user information will be edited
        # get user id to edit
        part_number = self.pa.input("Insert PART NUMBER to edit").upper()
        self.cur.execute("SELECT * FROM chemicals WHERE part_number = '"+part_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) == 0:
            self.pa.error("PART NUMBER is not in the database!")
        else:
            # get default values
            # part_number VARCHAR(50), desc VARCHAR(100), sc VARCHAR(10), shortname VARCHAR(20), fridge VARCHAR(1), msds VARCHAR(50)
            data = fetched_values[0]
            part_number = data[0]
            desc = data[1]
            sc = data[2]
            shortname = data[3]
            fridge = data[4]
            msds = data[5]

            # setup a form to fill
            fields = {}
            fields["PART NUMBER"] = FIELD("PART NUMBER", TEXT, part_number)
            fields["PART NUMBER"].disabled = True
            fields["DESCRIPTION"] = FIELD("DESCRIPTION", TEXT, desc)
            fields["STORAGE CONDITIONS"] = FIELD("STORAGE CONDITIONS", TEXT, sc)
            fields["SHORT NAME"] = FIELD("SHORT NAME", TEXT, shortname)
            fields["FRIDGE"] = FIELD("FRIDGE", CHOOSE, fridge)
            fields["FRIDGE"].options = ("Y", "N")
            fields["MSDS"] = FIELD("MSDS", TEXT, msds)
            form = self.pa.form(fields)

            if form:
                self.cur.execute("UPDATE chemicals SET msds = '"+str(form["MSDS"])+"', desc = '"+str(form["DESCRIPTION"])+"', sc = '"+str(form["STORAGE CONDITIONS"])+"', shortname = '"+str(form["SHORT NAME"])+"', fridge = '"+str(form["FRIDGE"])+"' WHERE part_number = '"+str(form["PART NUMBER"])+"'")
                self.con.commit()
                self.pa.print("PART NUMBER "+str(form["PART NUMBER"])+" - Changes have been saved")
            else:
                self.pa.error("PART NUMBER "+part_number+" - Changes have NOT been saved")

        if not self.pa.database_is_displayed():
            self.display_database()
        else:
            self.pa.update_database()
        self.pa.restart()
    
    def delete(self):
        ## DELETE
        #- This will allow you to delete an existing LOT or PART NUMBER
        #- Insert a valid LOT or PART NUMBER to delete
        # get user id to edit
        ans = self.pa.choose("What would you like to delete?", ("LOT NUMBER", "PART NUMBER"), "")
        if ans == "PART NUMBER":
            part_number = self.pa.input("Insert PART NUMBER to delete").upper()
            self.cur.execute("SELECT * FROM chemicals WHERE part_number = '"+part_number+"'")
            fetched_values = self.cur.fetchall()
            if len(fetched_values) == 0:
                self.pa.error("PART NUMBER is not in the database!")
            else:
                if self.pa.question("Are you sure you want to delete PART NUMBER: "+part_number+" and all open lots for this part number?"):
                    self.cur.execute("DELETE FROM chemicals WHERE part_number = '"+part_number+"'")
                    self.cur.execute("DELETE FROM chemical_lots WHERE part_number = '"+part_number+"'")
                    self.con.commit()
                    self.pa.print("PART NUMBER "+part_number+" and all open lots [if any exited] for this part number - were deleted")
                else:
                    self.pa.error("PART NUMBER "+part_number+" - was NOT deleted")
        
        elif ans == "LOT NUMBER":
            lot_number = self.pa.input("Insert LOT NUMBER to delete").upper()
            self.cur.execute("SELECT * FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
            fetched_values = self.cur.fetchall()
            if len(fetched_values) == 0:
                self.pa.error("LOT NUMBER is not in the database!")
            else:
                if self.pa.question("Are you sure you want to delete LOT NUMBER: "+lot_number):
                    self.cur.execute("DELETE FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
                    self.con.commit()
                    self.pa.print("LOT NUMBER "+lot_number+" - was deleted")
                else:
                    self.pa.error("LOT NUMBER "+lot_number+" - was NOT deleted")

        if not self.pa.database_is_displayed():
            self.display_database()
        else:
            self.pa.update_database()
        self.pa.restart()

    def stock(self):
        ## STOCK-COUNT
        #- Will allow you to count the current stock
        stock_list = []
        current_part_number = ""
        self.pa.print("Scan all yellow labels one by one. Insert the word END to finish the stock-count")
        lot_number = ""
        while lot_number != "END":
            lot_number = self.pa.input("Insert LOT NUMBER or the word END to finish the stock-count").upper()
            if lot_number != "END":
                self.cur.execute("SELECT * FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    self.pa.error("LOT NUMBER: "+lot_number+" is not in the database")
                else:
                    dont_add = False
                    data = fetched_values[0]
                    lot_number = data[0]
                    part_number = data[1]
                    exp = data[2]
                    self.pa.print("LOT NUMBER: "+lot_number+", PART NUMBER: "+part_number+", EXPIRATION DATE: "+exp)
                    if current_part_number != part_number:
                        current_part_number = part_number
                        self.pa.notice("Notice! This part number is not same same as the previous one")
                    dt = exp
                    dt = dt.split("-")
                    y = int(dt[0])
                    m = int(dt[1])
                    d = int(dt[2])
                    if datetime.datetime(y,m,d) < datetime.datetime.now()+datetime.timedelta(days=5):
                        self.pa.error("Notice! this lot is expired!")
                        if self.pa.question("Would you like to delete it from the database?"):
                            self.cur.execute("DELETE FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
                            self.con.commit()
                            self.pa.print("LOT NUMBER "+lot_number+" - was deleted")
                            dont_add = True
                        else:
                            self.pa.error("LOT NUMBER "+lot_number+" - was NOT deleted")
                    if not dont_add:
                        stock_list.append(lot_number)
            else:
                self.pa.print("Stock-Count complete!")
                file = open("Stockcount.txt", "w")
                for line in stock_list:
                    file.write(line+"\n")
                file.close()
        self.pa.restart()

main()

# SCRIPT FUNCTIONS
# SETTINGS
# Database location --> The location of the database. For example: database.db
# Yellow Label filename --> yellow lbl.btw
# Yellow Label CSV --> yellow lbl.csv

# RELATED FILES
## Yellow Label.btw a bartender file
## CSV file for the Yellow label to print from
## Database file to keep all the relevant data