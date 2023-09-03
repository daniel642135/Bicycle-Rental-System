#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 02:23:10 2023

@author: Group B - 5

  CoB (NBS) LIM KANG WEN G2301084K
  CoB (NBS) MAK WENG WAI G2300977G
  CoB (NBS) QI RUIJINGLING G2300745D
  CoB (NBS) SONG YUTONG G2300338L
  CoB (NBS) SU RUIYANG G2300471D
  CoB (NBS) LI JIAXUAN G2301249G
"""



import sqlite3
import sys
import datetime
import pandas as pd
import time
import threading

#define the bike class so that there are several types of bikes and the price is modifiable
class Bicycle:
    def __init__(self, bicycleid, name=None, price=None): #initializes the Bicycle class with the attributes bicycleid, name, and price.
        while True:
            try:
                self.bicycleid = int(bicycleid)
                break
            except ValueError: #if it's not a valid integer, prompts the user to input the bicycle ID until a valid integer is provided.
                print("bicycleid should be an integer")
                bicycleid = input("Bicycle ID?")
        
        if name != None:
            allowed_options = ["Adult","Kids","Tandem","Family","Pedal"] #user can only choose these 5 types
            while True:
                if name in allowed_options:
                    self.name = name
                    break
                else: #prompts the user to input a valid name until it matches one of the allowed options.
                    print("Name should be one of the following Adult/Kids/Tandem/Family/Pedal")
                    name = input("Bicycle Name? [Adult/Kids/Tandem/Family/Pedal]")
        
        if price != None:
            while True:
                try:
                    self.price = float(price) #convert it to a float
                    break
                except ValueError: #prompts the user to input the price until a valid numeric value is provided.
                    print("price should be a numeric value")
                    price = input("Price? (numeric)")
        else:
            self.price = price

class Rental:
    def __init__(self):  #create three tables in which the following functions will take place.  
        self.__db = 'bicycle'
        self.__tableName = 'bicycle'
        self.__txtableName = 'txbicycle'
        self.__pricetableName = 'dimBicyclePrice'
        
        con = sqlite3.connect(self.__db) ##connects to the database and creates tables if they don't exist already. It also inserts initial price values if the price table is empty.
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'create table if not exists {self.__tableName}(bicycleid int PRIMARY KEY, \
                            name varchar(25), status varchar(25))')
                cur.execute(f'create table if not exists {self.__txtableName}(transactionid int INTEGER PRIMARY KEY, \
                            bicycleid int, time_in datetime, time_out datetime, \
                            bookinghour int, revenue double,latereturn bool)')
                cur.execute(f'create table if not exists {self.__pricetableName}(name varchar(25) PRIMARY KEY, price float)')
                cur.execute(f'select * from {self.__pricetableName}')
                rows = cur.fetchall()
                if len(rows) ==0:
                    cur.execute(f'insert into {self.__pricetableName}(name, price) values("Adult",8),("Kids",6),("Tandem",16),("Family",35),("Pedal",26)')   #Initial prices are defined for different types of bicycles.
            except sqlite3.Error as e:
                print("Error: ", e)
                
    def displayBicycle(self):     #display the inventory.
        con = sqlite3.connect(self.__db) 
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select a.bicycleid, a.name, b.price, a.status from {self.__tableName} a, {self.__pricetableName} b where a.name = b.name')
                rows = cur.fetchall()
                if len(rows) ==0:  #check if there are any bikes in the inventory. Table is displayed only when at least one bicycle exists.
                    print("There is no bicycle in the Inventory")
                else:
                    headers=["bicycleid", "name", "price", "status"]
                    print(pd.DataFrame(rows, columns=headers))
            except sqlite3.Error as e:
                print("Error: ", e)
                sys.exit(1)
                
    def insertNewBicycle(self,bicycle): #insert new bicycle.
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select bicycleid from {self.__tableName} where bicycleid = {bicycle.bicycleid}')
                bicycleid = cur.fetchone()
                if bicycleid is None:    #check whether the inserted bike is new. The insertion operation can only be successful if the bike is not already in the inventory.    
                    sql = f'insert into {self.__tableName} (bicycleid, name, status) values({bicycle.bicycleid},"{bicycle.name}", "available")'
                    cur.execute(sql)
                    print(f'{bicycle.name} bicycleid:{bicycle.bicycleid} has been added to Inventory')
                else: #the bicycle is already in the inventory
                    print(f'bicycleid:{bicycle.bicycleid} is already available in Inventory')
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)
                
    def removeBicycle(self,bicycle):  #remove bicycle.
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select bicycleid from {self.__tableName} where bicycleid = {bicycle.bicycleid}')
                bicycleid = cur.fetchone()
                if bicycleid is None:  #check if the bicycle you want to remove is in the inventory. The removal operation can only be successful if the bike is already in the inventory.
                    print(f'bicycleid:{bicycle.bicycleid} is not available in Inventory')
                else:
                    sql = f'delete from {self.__tableName} where bicycleid = {bicycle.bicycleid}'
                    cur.execute(sql)
                    print(f'Bicycle with ID {bicycle.bicycleid} has been removed from inventory')
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)

    def updateBicyclePrice(self,bicycle):  #update the price of a type of bicycle.
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select name from {self.__pricetableName} where name = "{bicycle.name}"')
                name = cur.fetchone()
                if name is None:  # Check if the type of bicycle you want to update is in the inventory. The update operation can only be successful at least one bicycle of that type is in the inventory.
                    print(f'name:{bicycle.name} is not available in Inventory')
                else:
                    cur.execute(f'update {self.__pricetableName} set price = {bicycle.price} where name = "{bicycle.name}"')
                    print(f'Price for {bicycle.name} has been updated to ${bicycle.price:.2f}')
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)
    
    def displayBicyclePrice(self):  #display the prices of different types of bicycles. Note that prices have initial values and are categorized by type of bike.
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select * from {self.__pricetableName}')
                rows = cur.fetchall()
                headers=["name", "price"]
                print(pd.DataFrame(rows, columns=headers))
            except sqlite3.Error as e:
                print("Error: ", e)
                sys.exit(1)
    
    def rentOutBicycle(self,bicycle,bookinghour,numbertorent): #rent out bicycles.
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select bicycleid from {self.__tableName} where name = "{bicycle.name}" and status = "available" limit {numbertorent}')
                rows = cur.fetchall()
                if len(rows) < numbertorent:                            # Check if the number of bicycles in stock is sufficient for rental. The rental operation can only be successful if the bicycles are sufficient.
                    print(f'Not enough {bicycle.name} bicyle(s) available for rent. Only {len(rows)} is available')
                else:
                    print("bicycleid rented:")
                    for row in rows:
                        print(row[0])
                        cur.execute(f"update {self.__tableName} set status = 'rental' where bicycleid = {row[0]}")
                        cur.execute(f'Select price from {self.__pricetableName} where name = "{bicycle.name}" ')
                        price = cur.fetchone()    # Calculate the resulting revenue.
                        cur.execute(f"insert into {self.__txtableName} (bicycleid, time_in, bookinghour, revenue) values({row[0]},datetime('now', '+0 hours'),{bookinghour},{price[0]}*{bookinghour})")
                        # Record transaction information.
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)
    
    def returnBicycle(self,bicycle):  #return Bicycles.
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f'Select bicycleid from {self.__tableName} where bicycleid = {bicycle.bicycleid}')
                bicycleid = cur.fetchone()
                cur.execute(f'Select bicycleid from {self.__tableName} where bicycleid = {bicycle.bicycleid} and status = "rental"')
                retbicycleid = cur.fetchone()
                if bicycleid is None:    #check if the bicycle you want to return is in the inventory. 
                    print(f'bicycleid:{bicycle.bicycleid} is not available in Inventory')
                elif retbicycleid is None:                             #check if the status of the bicycle you want to return is "rental". The return operation can only be successful if the bicycle was rented out.
                    print(f'bicycleid:{bicycle.bicycleid} is available for rent and cannot be returned')
                else:
                    cur.execute(f"update {self.__tableName} set status = 'available' where bicycleid = {bicycle.bicycleid}")
                    cur.execute(f'Select price from {self.__pricetableName} where name = (select name from {self.__tableName} where bicycleid = {bicycle.bicycleid})')
                    price = cur.fetchone()      #calculate the actual rental time and possible overtime charges.
                    cur.execute(f"update {self.__txtableName} set time_out = datetime('now', '+0 hours'), \
                                latereturn = case when datetime('time_in', '+' + bookinghour + ' hours') < datetime('now', '+0 hours') then 1 else 0 end, revenue = case when datetime('time_in', '+' + bookinghour + ' hours') < datetime('now', '+0 hours') then {price[0]}*bookinghour + ((strftime('%s', datetime('now', '+0 hours')) - strftime('%s', datetime('time_in', '+' + bookinghour + ' hours')) + 3599) / 3600)*{price[0]} \
                                else {price[0]}*bookinghour end where bicycleid = {bicycle.bicycleid} and time_out is null")
                    cur.execute(f"Select bicycleid, revenue, latereturn from {self.__txtableName} where bicycleid = {bicycle.bicycleid} and time_out = (select max(time_out) from {self.__txtableName} where bicycleid = {bicycle.bicycleid})")
                    row = cur.fetchone()
                    print(f"bicycleid {row[0]} has been returned successfully. Revenue generated is ${row[1]:.2f}. Late return status is {row[2]}")
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)   
                 
                
    def refresh_all_bicycles(self):    #update the status of all bicycles.
        con=sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor()
                cur.execute(f"update {self.__tableName} set status = 'available'")
                print("\nAll bicycles have been refreshed to available")
            except sqlite3.Error as e:
                print("Error refresh :",e)
                #assumue the systhem never close!!!!!!
        
        
         
                           
class DailySalesReport:
    def __init__(self, date): #set up classes (1) database of bicycle, (2) transaction table, (3) bicycle table
        self.date = date
        self.__db = 'bicycle'
        self.__txtableName = 'txbicycle'
        self.__tableName = 'bicycle'
        
    def generate_report(self):
        con = sqlite3.connect(self.__db) #Established the connection to SQLite Database
        with con:
            try: 
                cur = con.cursor()
                cur.execute(f'SELECT a.bicycleid, b.name, a.revenue, a.time_in, a.time_out FROM {self.__txtableName} a, {self.__tableName} b WHERE a.bicycleid = b.bicycleid and date(a.time_in) = "{self.date}"')
                rows = cur.fetchall() 
                #Queries the database to fetch rows containing information (bicycleid, name, revenue, time_in, time_out) from txbicycle and bicycle tables where 'time_in' date matches the provided date
                
                print(f"***** Daily Sales Report - {self.date} *****")
                print("{:<10s} {:<20s} {:>10s} {:>20s} {:>20s}".format("ID", "Bicycle Name", "Revenue", "Time In", "Time Out"))
                #The formatting of report title and formatting of report headers
                
                total_revenue = 0
                
                for row in rows:
                    bicycle_id, bicycle_name, revenue, time_in, time_out = row #The initially obtained details from txbicycle and bicycle tables are printed
                    try: #To look for missing time_out values. If have, then print 'not return'
                        print("{:<10d} {:<20s} ${:>9.2f} {:>20s} {:>20s}".format(bicycle_id, bicycle_name, revenue, time_in, time_out))
                    except:
                        print("{:<10d} {:<20s} ${:>9.2f} {:>20s}{:>20s}".format(bicycle_id, bicycle_name, revenue, time_in, "not return"))
                    total_revenue += revenue #calculation of total revenue of the day
                
                print("\nTotal Revenue: ${:.2f}".format(total_revenue)) #printing of calculated total revenue
                
            except sqlite3.Error:
                print("Error ")
                sys.exit(1)
                
            save_option = input("Do you want to save the report to a file? (y/n): ").strip().lower() #User option to save report into a txt file
        if save_option == 'y':
            
            file_path = f"Sales{self.date[:4]}{self.date[5:7]}{self.date[8:10]}.txt"
            self.save_report_to_file(file_path)
            
    def save_report_to_file(self, file_path):
        try:
            with open(file_path, 'w') as file:
                con = sqlite3.connect(self.__db)  #Established the connection to SQLite Database
                with con:
                    cur = con.cursor()
                    cur.execute(f'SELECT a.bicycleid, b.name, a.revenue, date(a.time_in), date(a.time_out) FROM {self.__txtableName} a, {self.__tableName} b WHERE a.bicycleid = b.bicycleid and date(a.time_in) = "{self.date}"')
                    rows = cur.fetchall()
                    #Queries the database to fetch rows containing information (bicycleid, name, revenue, time_in, time_out)

                    file.write(f"***** Daily Sales Report - {self.date} *****\n")
                    file.write("{:<10s} {:<20s} {:>10s} {:>20s} {:>20s}\n".format("ID", "Bicycle Name", "Revenue", "Time In", "Time Out"))
                    #Open in write mode and format the header of the report

                    total_revenue = 0

                    for row in rows:
                        bicycle_id, bicycle_name, revenue, time_in, time_out = row #The initially obtained details from txbicycle and bicycle tables are printed
                        try: #To look for missing time_out values. If have, then print 'not return'
                            file.write("{:<10d} {:<20s} ${:>9.2f} {:>20s} {:>20s}\n".format(bicycle_id, bicycle_name, revenue, time_in, time_out))
                        except:
                            file.write("{:<10d} {:<20s} ${:>9.2f} {:>20s}{:>20s}".format(bicycle_id, bicycle_name, revenue, time_in, "not return"))
                        total_revenue += revenue #calculation of total revenue of the day

                    file.write("\nTotal Revenue: ${:.2f}\n".format(total_revenue))
                
            print(f"Report saved to {file_path}") 
        except Exception as e:
            print("Error saving report:", str(e))

class Maintenance:
    def __init__(self):
        """
        Initialize the Maintenance class.
        Sets up the database connection and table name for bicycle information.
        """
        self.__db = 'bicycle'
        self.__tableName = 'bicycle'

    def markMaintenance(self, bicycle):
        """
        This method updates the status of the bicycle to 'maintenance' if it is currently 'available'. If the bicycle
        is in 'rental' status, it cannot be placed for maintenance. If the bicycle is not found, a message is displayed.
        """
        con = sqlite3.connect(self.__db) #establishes a connection to the SQLite database
        with con:
            try:
                cur = con.cursor() #creates a cursor to execute SQL statements and manage query results.
                cur.execute(f"select status from {self.__tableName} where bicycleid = {bicycle.bicycleid}")
                row = cur.fetchone() #The fetchone() method retrieves the first row (result) of the query. In this case, it gets the status of the bicycle.
                if row and row[0] == 'available': # checks if the row was retrieved and if the status of the bicycle is 'available'.
                    cur.execute(f"update {self.__tableName} set status = 'maintenance' where bicycleid = {bicycle.bicycleid}") # change the status of the bicycle to 'maintenance'.
                    print(f"Bicycle with ID {bicycle.bicycleid} has been marked for maintenance.")
                elif row and row[0] == 'rental': #checks if the row was retrieved and if the status of the bicycle is 'rental'.
                    print(f"Bicycle with ID {bicycle.bicycleid} cannot be placed for maintenance as it is being rented out.")
                else: #for the situations that the ID is not found
                    print(f"no bicycle with ID {bicycle.bicycleid}")
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)

    def endMaintenance(self, bicycle):
        """
        This method updates the status of the bicycle to 'available' if it is currently under 'maintenance'. If the
        bicycle is not in 'maintenance' status, a message is displayed.
        """
        con = sqlite3.connect(self.__db)
        with con:
            try:
                cur = con.cursor() #creates a cursor to execute SQL statements and manage query results.
                cur.execute(f"select status from {self.__tableName} where bicycleid = {bicycle.bicycleid}")
                row = cur.fetchone() #the fetchone() method retrieves the first row (result) of the query. In this case, it gets the status of the bicycle.
                if row and row[0] == 'maintenance': #checks if the row was retrieved and if the status of the bicycle is 'maintenance'.
                    cur.execute(f"update {self.__tableName} set status = 'available' where bicycleid = {bicycle.bicycleid}") #change the status of the bicycle to 'available'.
                    print(f"Bicycle with ID {bicycle.bicycleid} has completed maintenance and is now available.")
                else: #the bicycleID is not under maintenance
                    print(f"Bicycle with ID {bicycle.bicycleid} is not under maintenance.")
            except sqlite3.Error as e:
                print("Error: ",e)
                sys.exit(1)

class BicycleController:
    def __init__(self): #initializes the BicycleController class with self.__db to the name of the database.
        self.__db="bicycle"
        
    def SalesReportToday(self):
        date = input("Enter the date (YYYY-MM-DD):")
        sales_report = DailySalesReport(date) #creates an instance of the DailySalesReport class, passing the input date as an argument.
        sales_report.generate_report() #invokes the generate_report method on the DailySalesReport instance to generate and display the sales report.
    
    def start(self):
        choice = self.Menu() #invokes the Menu method to display the main menu and store the user's choice
        RentalD = Rental() #creates an instance of the Rental class to manage the rental operations.
        refresh_thread = threading.Thread(target=self._daily_refresh) #ensure to run the _daily_refresh method concurrently with the main program.
        refresh_thread.daemon = True  #when main program ends so does the thread
        refresh_thread.start()
        
        while choice !="X": #starts a loop that continues until the user selects the "X" option to exit the program.
            if choice =="A": #when user choose 'Add New Inventory'
                myid = input("Bicycle ID?") #prompts the user for bicycle ID
                myName = input("Bicycle Name? [Adult/Kids/Tandem/Family/Pedal]") #prompts the user for bicycle name
                bicycle = Bicycle(myid, myName) #creates a new Bicycle instance
                RentalD.insertNewBicycle(bicycle) #inserts it into the inventory using the insertNewBicycle method.
            elif choice =="I": #when user choose 'Inventory'
                subchoice = self.InventoryMenu()
                while subchoice !="R": #starts a loop until the user selects the "R" option to return to the main menu.
                    if subchoice =="1": #user choose to display all inventory
                        RentalD.displayBicycle() #invokes the displayBicycle method to display the current inventory.
                    elif subchoice =="2": #when uer choose 'update bicycle price'
                        myName = input("Bicycle Name? [Adult/Kids/Tandem/Family/Pedal]") #prompts the user for bicycle name
                        myPrice = input("price? (numeric)") #prompts the user for new price
                        myid = -1 #filler id
                        bicycle = Bicycle(myid, myName, myPrice) #creates a new Bicycle instance
                        RentalD.updateBicyclePrice(bicycle) #updates the bicycle price using the updateBicyclePrice method.
                    elif subchoice =="3": #user choose to remove bicycle
                        myid = input("Bicycle ID?") #promptsthe user for bicycle ID
                        bicycle = Bicycle(myid) 
                        RentalD.removeBicycle(bicycle) #removes the bicycle from inventory using the removeBicycle method.
                    elif subchoice =="R": #user choose to return to main menu
                        choice = self.Menu()
                    subchoice = self.InventoryMenu() #prompts the user to select another inventory management option.
            elif choice =="P": #user choose 'Rental and Payment'
                options = """***** Rent Pricing*****
                
                All prices are per hour:
                    """
                print(options) #sisplays a message explaining the rental pricing structure.
                RentalD.displayBicyclePrice() #displays the current bicycle rental prices using the displayBicyclePrice method.
                myName = input("Bicycle Name? [Adult/Kids/Tandem/Family/Pedal]") #prompts the user to enter a bicycle name.
                while True:
                    try:
                        numberRent = int(input("Number to Rent (Integers)")) #prompts the user to enter the number of bicycles to rent.
                        break
                    except ValueError: #handling input validation for integers.
                        print("Number to Rent should be an integer")
                        numberRent = int(input("Number to Rent (Integers)"))
               
                while True:
                    try:
                        bookinghour = int(input("How many hours? (Integers)")) #prompts the user to enter the number of hours for renting.
                        break
                    except ValueError: #handling input validation for integers.
                        print("Booking Hour should be an integer")  
                        bookinghour = int(input("How many hours? (Integers)"))
                myid = -1 #filler id
                bicycle = Bicycle(myid, myName) #creates a new Bicycle instance with ID and name.
                RentalD.rentOutBicycle(bicycle,bookinghour,numberRent) #invokes the rentOutBicycle method to rent out the bicycles.
            elif choice =="R": #user choose to 'Return Rental'
                myid = input("Bicycle ID to return (Integers)")
                bicycle = Bicycle(myid) #prompts the user to enter a bicycle ID for return.
                RentalD.returnBicycle(bicycle) #invokes the returnBicycle method.
            elif choice == "S": #user choose 'Sales Report Today'
                self.SalesReportToday() #Invokes the SalesReportToday method to generate and display the sales report for the current day.
            elif choice == "M": #user choose 'Maintenance'
                subchoice = self.MaintenanceMenu()
                maintenance = Maintenance()
                while subchoice != "R": #Starts a loop until the user selects the "R" option to return to the main menu.
                    if subchoice == "1": #user choose to mark bicycle for maintenance
                        myid = input("Bicycle ID to perform maintenance on (Integers)") #prompts the user to enter a bicycle ID.
                        bicycle = Bicycle(myid)
                        maintenance.markMaintenance(bicycle) #invokes the markMaintenance method to mark the bicycle for maintenance.
                    elif subchoice == "2": #user choose to end maintenance for bicycle
                        myid = input("Bicycle ID to end maintenance for (Integers)") #prompts the user to enter a bicycle ID.
                        bicycle = Bicycle(myid)
                        maintenance.endMaintenance(bicycle) #invokes the endMaintenance method to end the bicycle for maintenance.
                    elif subchoice == "R": #if the user selects option "R" to return to the main menu, exits the maintenance loop.
                        choice = self.Menu() #prompts the user to select another option from the main menu.
                    subchoice = self.MaintenanceMenu()
            elif choice == 'X': #if the user selects the "X" option to exit.
                sys.exit(1)
            choice = self.Menu()

    def Menu(self):
        items = """***** Bicycle Rental System *****

                A. Add New Inventory
                I. Inventory
                P. Rental and Payment
                R: Return Rental
                S: Sales Report Today
                M: Maintenance
                X. Exit
            """
        print(items) #print the menu
        choice = input("Enter your choice").upper().strip() #to ensure not case sensitive
        return choice   
    
    def InventoryMenu(self):
        items = """***** Bicycle Rental System *****
        
                1. Display All Inventory
                2. Update Bicycle Price
                3. Remove Bicycle
                R. Return to main menu
            """
        print(items) #print the menu
        choice = input("Enter your choice").upper().strip()
        return choice  
    
    def MaintenanceMenu(self):
        items = """***** Bicycle Rental System - Maintenance Menu *****
        
                1. Mark Bicycle for Maintenance
                2. End Maintenance for Bicycle
                R. Return to main menu
            """
        print(items) #print the menu
        choice = input("Enter your choice").upper().strip() #to ensure not case sensitive
        return choice
    
    def _daily_refresh(self):
        rental=Rental()
        while True:
            now=datetime.datetime.now()  #checking time whether it is 23:59
            if now.hour==23 and now.minute==59: #this one could change to any time the system owner wants
                rental.refresh_all_bicycles()
                time.sleep(60)  #when finished,sleep for 60 sec, this can make sure no repeat every sec
            time.sleep(1) #check each min

    
if __name__ =="__main__":
    go = BicycleController()
    go.start()
