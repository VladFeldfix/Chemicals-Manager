from PersonalAssistant import *
import sqlite3
import datetime
class main:
    def __init__(self):
        # create a new PersonalAssistant
        self.pa = PersonalAssistant("Chemicals Manager", "0.1")

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

        # display main menu
        self.pa.main_menu["REGISTER A NEW CHEMICAL AND PRINT A YELLOW LABEL"] = self.add
        self.pa.main_menu["EDIT"] = self.edit_chemical
        self.pa.main_menu["DELETE"] = self.delete_chemical
        self.pa.display_menu()

        # run PersonalAssistant
        self.pa.run()
    
    def display_database(self):
        self.pa.display_database(self.db_location, "dbview", "part_number")

    # ADD
    def add(self):
        # set global variables
        error = False

        # lot number
        lot_number = self.pa.input("Insert LOT NUMBER")
        if lot_number != "":
            self.cur.execute("SELECT * FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
            fetched_values = self.cur.fetchall()
            if len(fetched_values) == 0:
                self.pa.error("Error! LOT NUMBER is not in the database")
                if self.pa.question("Register a new LOT NUMBER?"):
                    if self.add_lot(lot_number):
                        self.print_yellow_label(lot_number)
                    else:
                        self.pa.error("Failed to register new LOT NUMBER")
                else:
                    self.pa.error("Aborting LOT NUMBER registration")
            else:
                self.print_yellow_label(lot_number)
        else:
            self.pa.error("Error! Invalid LOT NUMBER")
        self.pa.restart()
    
    def print_yellow_label(self, lot_number):
        self.pa.update_database()
        self.pa.print("Printing yellow labels")
        qty = self.pa.input("How many YELLOW LABELS do you need to print?")
        file = open(self.pa.get_setting("Yellow labels location")+"/print.csv", 'w')
        file.write("PART NUMBER,LOT NUMBER,SC,EXP,SHORT NAME,QTY\n")
        self.cur.execute("SELECT dbview.part_number, dbview.lot_number, dbview.sc, dbview.exp, dbview.shortname FROM dbview WHERE lot_number = '"+lot_number+"'")
        fetched_values = self.cur.fetchall()
        line_to_print = ""
        if len(fetched_values) > 0:
            for info in fetched_values[0]:
                line_to_print += info+","
        else:
            self.pa.fatal_error("Missing records, cannot print labels")
        line_to_print = line_to_print[:-1]
        file.write(line_to_print+","+qty)
        file.close()
        path = self.pa.get_setting("Yellow labels location")+"/"+self.pa.get_setting("Yellow labels filename")
        if not os.path.isfile(path):
            self.pa.fatal_error("Missing file: "+path)
        else:
            os.popen(path)
    
    def add_lot(self, lot_number):
        # part number
        continue_registration = False
        part_number = self.pa.input("To what PART NUMBER this LOT NUMBER: ["+lot_number+"] belongs?")
        if part_number != "":
            self.cur.execute("SELECT * FROM chemicals WHERE part_number = '"+part_number+"'")
            fetched_values = self.cur.fetchall()
            if len(fetched_values) == 0:
                self.pa.error("Error! PART NUMBER is not in the database")
                if self.pa.question("Register new PART NUMBER?"):
                    if self.add_chemical(part_number):
                        continue_registration = True
                    else:
                        self.pa.error("Failed to register new PART NUMBER")
                        return False
                else:
                    self.pa.error("Aborting PART NUMBER registration")
                    return False
            else:
                continue_registration = True
        else:
            self.pa.error("Error! Invalid PART NUMBER")
            return False
        
        if continue_registration:
            exp = self.date_format(self.pa.input("Insert EXPIRATION DATE in the following format YYYY-MM-DD")) or self.pa.today()
            if self.pa.question("Registering new chemical lot:\nLot Number: "+lot_number+"\nPart Number: "+part_number+"\nExpiration Date: "+exp+"\nApprove registration?"):
                self.cur.execute("INSERT INTO chemical_lots (lot_number, part_number, exp) VALUES ('"+lot_number+"','"+part_number+"','"+exp+"')")
                self.con.commit()
                self.pa.print("LOT NUMBER successfully added to the database!")
                return True
            else:
                self.pa.error("Aborting LOT NUMBER registration")
                return False
    
    def add_chemical(self, part_number):
        error = False
        # description
        desc = self.pa.input("Insert DESCRIPTION") or "Missing description"
        
        # storage conditions
        if not error:
            sc = self.pa.input("Insert STORAGE CONDITIONS (e.g. 20-52C). [Leave empty for Room Temp]") or "Room Temp"
        
        # shortname
        if not error:
            short_name = self.pa.input("Insert SHORT NAME (Optional)")
        
        # fridge
        if not error:
            if self.pa.question("Requires refrigeration?"):
                fridge = "Y"
            else:
                fridge = "N"
        
        # msds
        if not error:
            msds = self.pa.input("Insert MSDS NUMBER (Optional)") or "-N/A-"

        # add new chemical to data
        if not error:
            if self.pa.question("Registering new chemical:\nPart number: "+part_number+"\nDescription: "+desc+"\nStorage conditions: "+sc+"\nShort name: "+short_name+"\nRequires refrigeration: "+fridge+"\nMSDS number: "+msds+"\nApprove registration?"):
                self.cur.execute("INSERT INTO chemicals (part_number, desc, sc, shortname, fridge, msds) VALUES ('"+part_number+"','"+desc+"','"+sc+"','"+short_name+"','"+fridge+"','"+msds+"')")
                self.con.commit()
                self.pa.print("CHEMICAL PART NUMBER successfully added to the database!")
                return True
            else:
                self.pa.error("Aborting PART NUMBER registration")
                return False

        # conclusion
        if error:
            self.pa.error("Failed to add a new chemical!")
            return False

        self.pa.update_database()
        self.pa.restart()

    # EDIT
    def edit_chemical(self):
        # set global variables
        error = False

        # lot or part number
        ans = self.pa.choose("What would you like to edit? [Leave empty to go back to main menu]", ("LOT","PART NUMBER"), "")

        # edit lot
        if ans == "LOT":
            lot_number = self.pa.input("Edit LOT NUMBER: ")
            if lot_number != "":
                self.cur.execute("SELECT * FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    self.pa.error("Error! LOT NUMBER is not in the database")
                else:
                    lot_number = fetched_values[0][0]
                    part_number = fetched_values[0][1]
                    exp = fetched_values[0][2]
                    self.pa.print("Current EXPIRATION DATE: "+exp)
                    exp = self.date_format(self.pa.input("Insert EXPIRATION DATE in the following format YYYY-MM-DD")) or self.pa.today()
                    if self.pa.question("Editing chemical lot:\nLot Number: "+lot_number+"\nPart Number: "+part_number+"\nExpiration Date: "+exp+"\nApprove registration?"):
                        self.cur.execute("UPDATE chemical_lots SET exp = '"+exp+"'")
                        self.con.commit()
                        self.pa.update_database()
                        self.pa.print("LOT NUMBER: "+lot_number+" successfully updated!")
                    else:
                        self.pa.error("Aborting LOT NUMBER update")
            else:
                self.pa.error("Aborting LOT NUMBER update")

        # edit part number
        elif ans == "PART NUMBER":
            part_number = self.pa.input("Edit PART NUMBER: ")
            if part_number != "":
                # part_number VARCHAR(50), desc VARCHAR(100), sc VARCHAR(10), shortname VARCHAR(20), fridge VARCHAR(1), msds VARCHAR(50)
                self.cur.execute("SELECT * FROM chemicals WHERE part_number = '"+part_number+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    pass
                else:
                    self.pa.error("Error! PART NUMBER is not in the database")
            else:
                self.pa.error("Aborting PART NUMBER update")

        # restart
        self.pa.restart()
    
    # DELETE
    def delete_chemical(self):
        # set global variables
        error = False
        self.pa.update_database()
        self.pa.restart()

    # OTHERS
    def date_format(self, text):
        text = text.replace("-", "")
        if len(text) > 7:
            # YYYY-MM-DD
            # 0123-45-67
            yyyy = text[0:4]
            mm = text[4:6]
            dd = text[6:8]
            result = yyyy+"-"+mm+"-"+dd
            try:
                if datetime.datetime(int(yyyy),int(mm),int(dd)) < datetime.datetime.now()+datetime.timedelta(days=5):
                    self.pa.error("NOTICE! This date is already / almost expired!")
            except:
                self.pa.error("Invalid date format: ["+result+"] Was changed to "+self.pa.today())
                result = self.pa.today()
        else:
            self.pa.error("Invalid date format: ["+text+"] Was changed to "+self.pa.today())
            result = self.pa.today()
            
        return result


main()