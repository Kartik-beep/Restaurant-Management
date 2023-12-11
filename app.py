import mysql.connector
import configparser
from base64 import b64decode
from cryptography.fernet import Fernet
import datetime

def decrypt(data, key):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data.decode()

class reception_menu():
    def reception_menu():
        print("\nReception Menu:")
        print("1. Available Rooms")
        print("2. Check In")
        print("3. Check Out")
        print("4. Exit")
    
    def display_available_rooms(cursor):
        try:
            # Execute a query to select available rooms
            cursor.execute("SELECT RoomNumber, Cost FROM Rooms WHERE IS_OCCUPIED = 'N'")
            available_rooms = cursor.fetchall()

            if not available_rooms:
                print("No available rooms.")
            else:
                print("\nAvailable Rooms:")
                header = ["Room Number", "Cost"]
                max_widths = [len(str(column)) for column in header]

                header_format = "{:<15} {:<10}"
                print(header_format.format(*header))
                print("-" * (sum(max_widths) + len(max_widths) - 1))

                for room in available_rooms:
                    formatted_data = [str(field) for field in room]
                    data_format = "{:<15} {:<10}"
                    print(data_format.format(*formatted_data))

        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def check_in(db_connection, cursor, room_number, first_name, last_name, dob, identification_id):
        try:
            while True:
                # Display entered data for confirmation
                print("\nEntered Data for Confirmation:")
                print(f"Room Number: {room_number}")
                print(f"First Name: {first_name}")
                print(f"Last Name: {last_name}")
                print(f"Date of Birth: {dob}")
                print(f"Identification ID: {identification_id}")

                # Ask user to confirm or correct entered data
                confirmation = input("Is the entered data correct? (yes/no): ").lower()

                if confirmation == 'yes':
                    # Data is correct, proceed with check-in
                    current_date = datetime.now().date()
                    current_time = datetime.now().time()

                    # Insert data into the 'CurrentStays' table
                    insert_query = """
                        INSERT INTO CurrentStays (RoomNumber, FirstName, LastName, DateOfBirth, IdentificationID, DateOfCheckIn, TimeOfCheckIn)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (room_number, first_name, last_name, dob, identification_id, current_date, current_time))
                    db_connection.commit()

                    # Set 'IS_OCCUPIED' to 'Y' for the specified room in the 'Rooms' table
                    update_query = "UPDATE Rooms SET IS_OCCUPIED = 'Y' WHERE RoomNumber = %s"
                    cursor.execute(update_query, (room_number,))
                    db_connection.commit()

                    print("Check-in successful!")

                elif confirmation == 'no':
                    pass
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def check_out(db_connection, cursor):
        try:
            # Get room number from user input
            room_number = int(input("Enter Room Number for Check-Out: "))

            # Check if the room is occupied
            check_occupancy_query = "SELECT * FROM CurrentStays WHERE RoomNumber = %s"
            cursor.execute(check_occupancy_query, (room_number,))
            current_stay_data = cursor.fetchone()

            if current_stay_data:
                # Room is occupied, display guest details
                print("\nGuest Details:")
                print(f"Room Number: {current_stay_data[1]}")
                print(f"First Name: {current_stay_data[2]}")
                print(f"Last Name: {current_stay_data[3]}")
                print(f"Date of Birth: {current_stay_data[4]}")
                print(f"Identification ID: {current_stay_data[5]}")
                print(f"Date of Check-In: {current_stay_data[6]} {current_stay_data[7]}")

                # Calculate and display duration of stay
                check_in_date = datetime.strptime(str(current_stay_data[6]), "%Y-%m-%d")
                current_date = datetime.now().date()
                duration_of_stay = (current_date - check_in_date).days
                print(f"Duration of Stay: {duration_of_stay} days")

                # Calculate and display bill amount
                room_cost_query = "SELECT Cost FROM Rooms WHERE RoomNumber = %s"
                cursor.execute(room_cost_query, (room_number,))
                room_cost = cursor.fetchone()[0]
                bill_amount = duration_of_stay * room_cost
                print(f"Bill Amount: {bill_amount} USD")

                # Confirm check-out
                confirm_checkout = input("Confirm Check-Out? (yes/no): ").lower()

                if confirm_checkout == 'yes':
                    # Update IS_OCCUPIED to 'N' in Rooms table
                    update_room_query = "UPDATE Rooms SET IS_OCCUPIED = 'N' WHERE RoomNumber = %s"
                    cursor.execute(update_room_query, (room_number,))
                    db_connection.commit()

                    # Transfer guest details to PastGuests table
                    transfer_query = """
                        INSERT INTO PastGuests (Room_Number, FirstName, LastName, DateOfBirth, IdentificationID, Bill_Amount,
                                            DateOfCheckIN, TimeOfCheckIn, DateOfCheckOut, TimeOfCheckOut)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(transfer_query, (
                        current_stay_data[1], current_stay_data[2], current_stay_data[3], current_stay_data[4],
                        current_stay_data[5], bill_amount, current_stay_data[6], current_stay_data[7],
                        current_date, datetime.now().time()
                    ))
                    db_connection.commit()

                    print("Check-Out successful.")
                else:
                    print("Check-Out canceled.")
            else:
                print("Room is not occupied.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            

class admin_menu():
    def admin_menu():
        print("\nAdmin Menu:")
        print("1. View Employees")
        print("2. View Rooms")
        print("3. View Current Stays")
        print("4. View Past Employees")
        print("5. View Past Guests")
        print("0. Exit")

    def view_employees(db_connection, cursor):
        try:
            cursor.execute("SELECT * FROM Employees")
            employees_data = cursor.fetchall()
            if not employees_data:
                print("No employees found.")
            else:
                print("\nEmployee Data:")
                header = ["ID", "First Name", "Last Name", "DOB", "ID Number", "Date Joined", "Salary", "Designation"]
                for i in employees_data:
                    print(f'{header[0]}: {i[0]}')
                    print(f'Name: {i[1]} {i[2]}')
            while True:
                # Fetch data from the Employees table
                cursor.execute("SELECT * FROM Employees")
                employees_data = cursor.fetchall()
                # Display options
                print("\nOptions:")
                print("1. Show Full Employee Details")
                print("2. Add Employee")
                print("3. Remove Employee")
                print("4. Show All Employees")
                print("5. Previous Menu")

                choice = input("Enter your choice (1-5): ")

                if choice == '1':
                    if not employees_data:
                        print("No Employees found.")
                    else:
                        b = int(input("Enter ID: "))
                        for i in range(len(header)):
                            for a in employees_data:
                                if b in a:
                                    print(f'{header[i]}: {a[i]}')
                elif choice == '2':
                    first_name = input("Enter First Name: ")
                    last_name = input("Enter Last Name: ")
                    dob = input("Enter Date of Birth (YYYY-MM-DD): ")
                    id_number = input("Enter Identification ID: ")
                    date_joined = str(datetime.datetime.now().date())
                    designation = input("Enter Designation (if the employee is reception/admin write same): ")
                    if designation == 'reception':
                        print("Creating Account.......")
                        passw = input("Enter Password for user")
                        print()
                        print(f'Your username is "{first_name}" and password is:', passw)
                        print()
                        create_user_query = f"CREATE USER '{first_name}'@'%' IDENTIFIED BY '{passw}';"
                        grant_a_privileges_query = f"GRANT SELECT, UPDATE ON Restaurant.Rooms TO '{first_name}'@'%';"
                        grant_b_privileges_query = f"GRANT SELECT, INSERT, DELETE, UPDATE ON Restaurant.CurrentStays TO '{first_name}'@'%';"
                        grant_c_privileges_query = f"GRANT INSERT ON Restaurant.PastGuests TO '{first_name}'@'%';"
                        grant_d_privileges_query = f"GRANT SELECT ON Restaurant.Employees TO '{first_name}'@'%';"
                        flush_privileges_query = "FLUSH PRIVILEGES;"
                        cursor.execute(create_user_query)
                        cursor.execute(grant_a_privileges_query)
                        cursor.execute(grant_b_privileges_query)
                        cursor.execute(grant_c_privileges_query)
                        cursor.execute(grant_d_privileges_query)
                        cursor.execute(flush_privileges_query)
                    elif designation == 'admin':
                        print("Creating Admin Account.......")
                        print()
                        print(f'Your username is "{first_name}" and password is:', passw)
                        print()
                        create_user_query = f"CREATE USER '{first_name}'@'%' IDENTIFIED BY '{passw}';"
                        grant_privileges_query = f"GRANT ALL PRIVILEGES ON Restaurant.* TO '{first_name}'@'%' WITH GRANT OPTION;"
                        flush_privileges_query = "FLUSH PRIVILEGES;"
                        cursor.execute(create_user_query)
                        cursor.execute(grant_privileges_query)
                        cursor.execute(flush_privileges_query)
                    else:
                        pass
                    print("Employee added successfully.")
                    salary = int(input("Salary: "))
                    add_employee_query = "INSERT INTO Employees(FirstName, LastName, DateOfBirth, IdentificationID, DateJoined, Salary, Designation) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(add_employee_query, (first_name, last_name, dob, id_number, date_joined, salary, designation))
                    db_connection.commit()
                    employees_data = cursor.fetchall()

                elif choice == '3':
                    # Remove employee logic
                    employee_id_to_remove = int(input("Enter the ID of the employee to remove: "))
                    past_employee_query = "INSERT INTO PastEmployees(First_Name, Last_Name, Date_Of_Birth, Identification_ID, Date_Joined, Date_Left ,Salary, Designation) SELECT FirstName, LastName, DateOfBirth, IdentificationID, DateJoined, %s, Salary, Designation from Employees where Employees.ID = %s"
                    cursor.execute(past_employee_query, (str(datetime.datetime.now().date()), employee_id_to_remove))
                    remove_employee_query = "DELETE FROM Employees WHERE ID = %s"
                    cursor.execute(remove_employee_query, (employee_id_to_remove,))
                    db_connection.commit()
                    print("Employee removed successfully.")
                    employees_data = cursor.fetchall()

                elif choice == '4':
                    print("\nEmployee Data:")
                    for i in employees_data:
                        print(f'{header[0]}: {i[0]}')
                        print(f'Name: {i[1]} {i[2]}')

                elif choice == '5':
                    print("Returning to the previous menu.")
                    break

                else:
                    print("Invalid choice. Please enter a number between 1 and 3.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def view_rooms(db_connection, cursor):
        try:
            while True:
                # Display options for the room menu
                print("\nRoom Menu:")
                print("1. View Rooms")
                print("2. Add Room")
                print("3. Remove Room")
                print("4. Previous Menu")

                room_choice = input("Enter your choice (1-4): ")

                if room_choice == '1':
                    cursor.execute("SELECT * FROM Rooms")
                    rooms_data = cursor.fetchall()
                    if not rooms_data:
                        print("No rooms found.")
                    else:
                        # Display room data
                        print("\nRoom Data:")
                        print("{:<15} {:<10} {:<10}".format("Room Number", "Cost", "Is Occupied"))
                        print("-" * 40)
                        for room in rooms_data:
                            # Check if any field is None before formatting
                            formatted_data = tuple("-" if field is None else field for field in room)
                            print("{:<15} {:<10} {:<10}".format(*formatted_data))

                elif room_choice == '2':
                    # Add room logic
                    room_number = int(input("Enter Room Number: "))
                    cost = int(input("Enter Room Cost: "))
                    add_room_query = "INSERT INTO Rooms(RoomNumber, Cost) VALUES (%s, %s)"
                    cursor.execute(add_room_query, (room_number, cost))
                    db_connection.commit()
                    print("Room added successfully.")

                elif room_choice == '3':
                    # Remove room logic
                    room_number_to_remove = int(input("Enter the Room Number to remove: "))
                    remove_room_query = "DELETE FROM Rooms WHERE RoomNumber = %s"
                    cursor.execute(remove_room_query, (room_number_to_remove,))
                    print("Room removed successfully.")

                elif room_choice == '4':
                    print("Returning to the previous menu.")
                    break

                else:
                    print("Invalid choice. Please enter a number between 1 and 4.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def view_current_stays(cursor):
        try:
            # Fetch data from the CurrentStays table
            cursor.execute("SELECT * FROM CurrentStays")
            current_stays_data = cursor.fetchall()

            if not current_stays_data:
                print("No current stays found.")
            else:
                # Display current stays data
                print("\nCurrent Stays Data:")
                print("{:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format("Stay ID", "Room Number", "First Name", "Last Name", "DOB", "ID Number", "Check-In Date", "Check-In Time"))
                print("-" * 125)
                for stay in current_stays_data:
                    # Check if any field is None before formatting
                    formatted_data = tuple("-" if field is None else field for field in stay)
                    print("{:<10} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}".format(*formatted_data))

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def view_past_employees(cursor):
        try:
            while True:
                # Fetch data from the PastEmployees table
                cursor.execute("SELECT * FROM PastEmployees")
                past_employees_data = cursor.fetchall()
                if not past_employees_data:
                    print("No employees found.")
                else:
                    print("\nEmployee Data:")
                    header = ["First Name", "Last Name", "DOB", "ID Number", "Date Joined", "Date Left", "Designation"]
                    for i in past_employees_data:
                        print(f'{header[0]}: {i[0]}')
                        print(f'Name: {i[1]} {i[2]}')
                print("\nRoom Menu:")
                print("1. View Full Employee Details")
                print("2. Previous Menu")

                choice = input("Enter your choice (1-2): ")

                if choice == '1':
                        if not past_employees_data:
                            print("No Employees found.")
                        else:
                            b = int(input("Enter ID: "))
                            for i in range(len(header)):
                                for a in past_employees_data:
                                    if b in a:
                                        print(f'{header[i]}: {a[i]}')
                elif choice == '2':
                    print("Returning to the previous menu.")
                    break

                else:
                    print("Invalid choice. Please enter a number 1 or 2.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def view_past_guests(db_connection, cursor):
        try:
            # Fetch data from the PastGuests table
            cursor.execute("SELECT * FROM PastGuests")
            past_guests_data = cursor.fetchall()
            headers = ["Bill Number", "Room Number", "First Name", "Last Name", "DOB", "ID Number", "Bill Amount", "Check-In Date", "Check-In Time", "Check-Out Date", "Check-Out Time"]
            if not past_guests_data:
                print("No past guests found.")
            else:
                # Display past guest data
                print("\nPast Guests Data:")
                for i in past_guests_data():
                    print(f'{headers[0]}: {i[0]}')
                    print(f'{headers[5]}: {i[5]}')
            while True:
                print("\nPast Guests Menu")
                print("1. View full details")
                print("2. Previous Menu")

                choice = input("Enter your choice (1-2): ")

                if choice == '1':
                    if not past_guests_data:
                            print("No Guests found.")
                    else:        
                        b = int(input("Enter Bill Number: "))
                        for i in range(len(headers)):
                            for a in past_guests_data:
                                if b in a:
                                    print(f'{headers[i]}: {a[i]}')

                elif choice == '2':
                    print("Returning to the previous menu.")
                    break

                else:
                    print("Invalid choice. Please enter a number 1 or 2.")

        except mysql.connector.Error as err:
                print(f"Error: {err}")

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    key = b64decode(config['Database']['Key'])
    host = decrypt(b64decode(config['Database']['Host']), key)
    database = decrypt(b64decode(config['Database']['Name']), key)

    return host, database

def get_user_designation(cursor, username):
    try:
        query = "SELECT Designation FROM Employees WHERE FirstName = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def main():
    host, database = read_config()

    try:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        
        # username = 'admin'
        # password = 'uqmyhv'

        db_connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        cursor = db_connection.cursor()

        if db_connection.is_connected():
            print("Connected to DB successfully.......")
            # User is not admin, check designation from the Employees table
            designation = get_user_designation(cursor, username)
            if username == 'admin' or designation == 'admin':
                while True:
                    admin_menu.admin_menu()
                    choice = input("Enter your choice (0-5): ")

                    if choice == '0':
                        print("Exiting...")
                        break
                    elif choice == '1':
                        admin_menu.view_employees(db_connection, cursor)
                    elif choice == '2':
                        admin_menu.view_rooms(db_connection, cursor)
                    elif choice == '3':
                        admin_menu.view_current_stays(cursor)
                    elif choice == '4':
                        admin_menu.view_past_employees(cursor)
                    elif choice == '5':
                        admin_menu.view_past_guests(cursor)
                    else:
                        print("Invalid choice. Please enter a number between 0 and 5.")

            elif designation == 'reception':
                while True:
                    reception_menu.reception_menu()
                    choice = input("Enter your choice (1-4): ")

                    if choice == '1':
                        reception_menu.display_available_rooms(cursor)
                        pass
                    elif choice == '2':
                        reception_menu.check_in(db_connection, cursor)
                        pass
                    elif choice == '3':
                        reception_menu.check_out(db_connection, cursor)
                        pass
                    elif choice == '4':
                        print("Exiting...")
                        break
                    else:
                        print("Invalid choice. Please enter a number between 1 and 4.")

            else:
                print("Invalid user designation.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if db_connection.is_connected():
            cursor.close()
            db_connection.close()

if __name__ == "__main__":
    main()