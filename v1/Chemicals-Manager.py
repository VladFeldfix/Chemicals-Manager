from PersonalAssistant import *
import sqlite3

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
        self.con.commit()
        
        # display database
        self.display_database()

        # display main menu
        self.pa.main_menu["ADD CHEMICAL"] = self.add
        self.pa.main_menu["EDIT CHEMICAL"] = self.edit_chemical
        self.pa.main_menu["DELETE CHEMICAL"] = self.delete_chemical
        self.pa.display_menu()

        # run PersonalAssistant
        self.pa.run()
    
    def display_database(self):
        # self.pa.display_database_ext(self.db_location, "")
        self.pa.display_database(self.db_location, "chemicals", "part_number")

    # ADD
    def add(self):
        # set global variables
        error = False

        # lot number
        lot_number = self.pa.input("Chemical lot number")
        self.cur.execute("SELECT * FROM chemical_lots WHERE lot_number = '"+lot_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) == 0:
            if self.pa.question("Lot number is not in the database. Would you like to add a new lot?"):
                self.add_lot(lot_number)
    
    def add_lot(self, lot_number):
        # part number
        part_number = self.pa.input("What is the part number for lot number: "+lot_number+"?")
        self.cur.execute("SELECT * FROM chemicals WHERE part_number = '"+part_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) == 0:
            if self.pa.question("This part number is not in the database. Would you like to add a new chemical?"):
                self.add_chemical(part_number)
    
    def add_chemical(self, part_number):
        error = False
        # description
        desc = self.pa.input("Chemical description")
        if desc == "":
            error = True
        
        # storage conditions
        if not error:
            sc = self.pa.input("Storage conditions (e.g. 20-52C). [Leave empty for Room Temp]") or "Room Temp"


        """

        # part_number VARCHAR(50)
        part_number = self.pa.input("Product part number")
        self.cur.execute("SELECT * FROM products WHERE part_number = '"+part_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) != 0:
            self.pa.error("Product part number is not new")
            error = True
        if part_number == "":
            self.pa.error("Invalid part number")
            error = True
        
        # desc VARCHAR(50)
        if not error:
            desc = self.pa.input("Product description")
            if desc == "":
                self.pa.error("Invalid description")
                error = True

        # parent VARCHAR(50)
        if not error:
            parent = self.pa.input("Parent product (Leave empty for main)")
            if parent == "":
                parent = "MAIN"
            else:
                self.cur.execute("SELECT * FROM products WHERE part_number = '"+parent+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    self.pa.error("Parent don't exist. Register parent before child")
                    error = True

        # order_number VARCHAR(50)
        if not error:
            order_number = self.pa.input("Product order number")
            if order_number == "":
                self.pa.error("Invalid order number")
                error = True

        # wiring_diagram VARCHAR(50)
        if not error:
            wiring_diagram = self.pa.input("Product wiring diagram")
            if wiring_diagram == "":
                self.pa.error("Invalidwiring diagram")
                error = True

        # wiring_diagram_rev VARCHAR(50)
        if not error:
            wiring_diagram_rev = self.pa.input("Product wiring diagram revision")
            if wiring_diagram_rev == "":
                self.pa.error("Invalid revision")
                error = True

        # drawing VARCHAR(50)
        if not error:
            drawing = self.pa.input("Product drawing")
            if drawing == "":
                self.pa.error("Invalid drawing")
                error = True

        # drawing_rev VARCHAR(50)
        if not error:
            drawing_rev = self.pa.input("Product drawing revision")
            if drawing_rev == "":
                self.pa.error("Invalid revision")
                error = True

        # bom_rev VARCHAR(50)
        if not error:
            bom_rev = self.pa.input("Product BOM revision")
            if bom_rev == "":
                self.pa.error("Invalid BOM revision")
                error = True

        # serial_number_format VARCHAR(50)
        if not error:
            serial_number_format = self.pa.choose("Select serial number format:", self.serial_number_formats, self.serial_number_formats[0])
        
        # add new product to data
        if not error:
            if self.pa.question("Registering new product:\nPart number: "+part_number+"\nDescription: "+desc+"\nParent: "+parent+"\nOreder Number: "+order_number+"\nWiring diagram: "+wiring_diagram+" Rev.: "+wiring_diagram_rev+"\nDrawing: "+drawing+" Rev.: "+drawing_rev+"\nBOM Rev.: "+bom_rev+"\nSerial number format: "+serial_number_format+"\nApprove registration?"):
                self.cur.execute("INSERT INTO products (part_number, desc, parent, oreder_number, wiring_diagram, wiring_diagram_rev, drawing, drawing_rev, bom_rev, serial_number_format) VALUES ('"+part_number+"','"+desc+"','"+parent+"','"+order_number+"','"+wiring_diagram+"','"+wiring_diagram_rev+"','"+drawing+"','"+drawing_rev+"','"+bom_rev+"','"+serial_number_format+"')")
                self.con.commit()
                self.pa.print("New product added successfully!")
            else:
                self.pa.error("Product was not added to database")

        # conclusion
        if error:
            self.pa.error("Failed to add a new product!")

        """

        self.pa.update_database()
        self.pa.restart()

    # EDIT
    def edit_chemical(self):
        # set global variables
        error = False

        """
        # part_number VARCHAR(50)
        part_number = self.pa.input("Product part number to edit")
        self.cur.execute("SELECT * FROM products WHERE part_number = '"+part_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) == 0:
            self.pa.error("This part number is not in the database")
            error = True
        else:
            row = fetched_values[0]
            part_number = row[0]
            desc = row[1]
            parent = row[2]
            order_number = row[3]
            wiring_diagram = row[4]
            wiring_diagram_rev = row[5]
            drawing = row[6]
            drawing_rev = row[7]
            bom_rev = row[8]
            serial_number_format = row[9]

        if part_number == "":
            self.pa.error("Invalid part number")
            error = True
        
        # desc VARCHAR(50)
        if not error:
            desc = self.pa.input("Product description: "+desc+"\n[Leave empty to keep original value]") or desc
            if desc == "":
                self.pa.error("Invalid description")
                error = True

        # parent VARCHAR(50)
        if not error:
            parent = self.pa.input("Parent product: "+parent+"\n[Leave empty to keep original value]") or parent
            if parent == "MAIN":
                parent = "MAIN"
            else:
                self.cur.execute("SELECT * FROM products WHERE part_number = '"+parent+"'")
                fetched_values = self.cur.fetchall()
                if len(fetched_values) == 0:
                    self.pa.error("Parent don't exist. Register parent before child")
                    error = True

        # order_number VARCHAR(50)
        if not error:
            order_number = self.pa.input("Product order number: "+order_number+"\n[Leave empty to keep original value]") or order_number
            if order_number == "":
                self.pa.error("Invalid order number")
                error = True

        # wiring_diagram VARCHAR(50)
        if not error:
            wiring_diagram = self.pa.input("Product wiring diagram: "+wiring_diagram+"\n[Leave empty to keep original value]") or wiring_diagram
            if wiring_diagram == "":
                self.pa.error("Invalidwiring diagram")
                error = True

        # wiring_diagram_rev VARCHAR(50)
        if not error:
            wiring_diagram_rev = self.pa.input("Product wiring diagram revision: "+wiring_diagram_rev+"\n[Leave empty to keep original value]") or wiring_diagram_rev
            if wiring_diagram_rev == "":
                self.pa.error("Invalid revision")
                error = True

        # drawing VARCHAR(50)
        if not error:
            drawing = self.pa.input("Product drawing: "+drawing+"\n[Leave empty to keep original value]") or drawing
            if drawing == "":
                self.pa.error("Invalid drawing")
                error = True

        # drawing_rev VARCHAR(50)
        if not error:
            drawing_rev = self.pa.input("Product drawing revision: "+drawing_rev+"\n[Leave empty to keep original value]") or drawing_rev
            if drawing_rev == "":
                self.pa.error("Invalid revision")
                error = True

        # bom_rev VARCHAR(50)
        if not error:
            bom_rev = self.pa.input("Product BOM revision: "+bom_rev+"\n[Leave empty to keep original value]") or bom_rev
            if bom_rev == "":
                self.pa.error("Invalid BOM revision")
                error = True

        # serial_number_format VARCHAR(50)
        if not error:
            serial_number_format = self.pa.choose("Select serial number format: [Leave empty to keep original value]", self.serial_number_formats, serial_number_format)
        
        # EDIT product
        if not error:
            if self.pa.question("Accept changes to product part number: "+part_number+"\nDescription: "+desc+"\nParent: "+parent+"\nOreder Number: "+order_number+"\nWiring diagram: "+wiring_diagram+" Rev.: "+wiring_diagram_rev+"\nDrawing: "+drawing+" Rev.: "+drawing_rev+"\nBOM Rev.: "+bom_rev+"\nSerial number format: "+serial_number_format+"\nApprove registration?"):
                self.cur.execute("UPDATE products SET desc = '"+desc+"', parent = '"+parent+"', oreder_number = '"+order_number+"', wiring_diagram = '"+wiring_diagram+"', wiring_diagram_rev = '"+wiring_diagram_rev+"', drawing = '"+drawing+"', drawing_rev = '"+drawing_rev+"', bom_rev = '"+bom_rev+"', serial_number_format = '"+serial_number_format+"' WHERE part_number = '"+part_number+"'")
                self.con.commit()
                self.pa.print("Product updated successfully!")
            else:
                self.pa.error("Product was not updated")
            
        # conclusion
        if error:
            self.pa.error("Failed to edit the product!")
        """
        self.pa.update_database()
        self.pa.restart()
    
    # DELETE
    def delete_chemical(self):
        # set global variables
        error = False

        """

        # part_number VARCHAR(50)
        part_number = self.pa.input("Product part number to delete")
        self.cur.execute("SELECT * FROM products WHERE part_number = '"+part_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) == 0:
            self.pa.error("This part number is not in the database")
            error = True

        # parents
        self.cur.execute("SELECT * FROM products WHERE parent = '"+part_number+"'")
        fetched_values = self.cur.fetchall()
        if len(fetched_values) != 0:
            row = fetched_values[0]
            child = row[0]
            self.pa.error(part_number+" is a parent of "+child+". Delete child before parent")
            error = True

        # DELETE product
        if not error:
            if self.pa.question("Are you sure you want to delete product: "+part_number+"?"):
                self.cur.execute("DELETE FROM products WHERE part_number = '"+part_number+"'")
                self.con.commit()
                self.pa.print("Product deleted successfully!")
            else:
                self.pa.error("Product was not delete")
        
        # conclusion
        if error:
            self.pa.error("Failed to delete the product!")
        """
        
        self.pa.update_database()
        self.pa.restart()

main()