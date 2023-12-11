import os
import mysql.connector
import random
import string
from hashlib import sha256
import configparser
from cryptography.fernet import Fernet
from base64 import b64encode

def generate_key():
    return Fernet.generate_key()

def encrypt(data, key):
    cipher = Fernet(key)
    return cipher.encrypt(data.encode())

def create_database(host_ip, host_user, host_password):
    print("Creating Database......")
    try:
        db_connection = mysql.connector.connect(
            host=host_ip,
            user=host_user,
            password=host_password
        )
        cursor = db_connection.cursor()
        database_name = 'Restaurant'

        cursor.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if db_connection.is_connected():
            cursor.close()
            db_connection.close()

def create_tables(host_ip, host_user, host_password, host_db):
    print('Connecting to the DB..........')
    try:
        db_connection = mysql.connector.connect(
            host=host_ip,
            user=host_user,
            password=host_password,
            database=host_db
        )
        cursor = db_connection.cursor()

        print("Creating Tables........")
        query = """
            CREATE TABLE IF NOT EXISTS Employees (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                FirstName VARCHAR(255) NOT NULL,
                LastName VARCHAR(255) NOT NULL,
                DateOfBirth DATE,
                IdentificationID VARCHAR(255) NOT NULL,
                DateJoined DATE,
                Salary int,
                Designation VARCHAR(255)
            );

            CREATE TABLE IF NOT EXISTS Rooms (
                RoomNumber INT PRIMARY KEY,
                Cost INT,
                IS_OCCUPIED CHAR(1) DEFAULT 'N'
            );

            CREATE TABLE IF NOT EXISTS CurrentStays (
                StayID INT AUTO_INCREMENT PRIMARY KEY,
                RoomNumber INT,
                FirstName VARCHAR(255) NOT NULL,
                LastName VARCHAR(255) NOT NULL,
                DateOfBirth DATE,
                IdentificationID VARCHAR(255) NOT NULL,
                DateOfCheckIn DATE,
                TimeOfCheckIn TIME,
                FOREIGN KEY (RoomNumber) REFERENCES Rooms(RoomNumber)
            );

            CREATE TABLE IF NOT EXISTS PastEmployees (
                First_Name VARCHAR(255) NOT NULL, 
                Last_Name VARCHAR(255) NOT NULL,
                Date_Of_Birth DATE,
                Identification_ID VARCHAR(20),
                Date_Joined DATE,
                Date_Left DATE,
                Salary int,
                Designation VARCHAR(255)
            );

            CREATE TABLE IF NOT EXISTS PastGuests (
                Bill_Number int AUTO_INCREMENT PRIMARY KEY,
                Room_Number INT,
                FirstName VARCHAR(255) NOT NULL,
                LastName VARCHAR(255) NOT NULL,
                DateOfBirth DATE,
                IdentificationID VARCHAR(255) NOT NULL,
                Bill_Amount int,
                DateOfCheckIN DATE,
                TimeOfCheckIn TIME,
                DateOfCheckOut DATE,
                TimeOfCheckOut TIME
            );

            CREATE TABLE IF NOT EXISTS Menu (
                Extras INT,
                Fines_Charges INT
            );

            CREATE INDEX IF NOT EXISTS idx_FirstName ON Employees(FirstName);
            
            CREATE TABLE IF NOT EXISTS USERS (
            UserID INT AUTO_INCREMENT PRIMARY KEY,
            ID INT,
            username VARCHAR(255),
            password CHAR(64),
            CONSTRAINT FOREIGN KEY (ID) REFERENCES Employees(ID),
            CONSTRAINT FOREIGN KEY (username) REFERENCES Employees(FirstName)
            );
        """

        for statement in query.split(";"):
            if statement.strip():
                cursor.execute(statement)

        print("Creating Default Admin Account.......")
        passw = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        print()
        print('Your username is "admin" and password is:', passw)
        print()
        create_user_query = f"CREATE USER 'admin'@'%' IDENTIFIED BY '{passw}';"
        grant_privileges_query = f"GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;"
        grant_create_user_query = f"GRANT CREATE USER ON *.* TO 'admin'@'%';"
        flush_privileges_query = "FLUSH PRIVILEGES;"
        cursor.execute(create_user_query)
        cursor.execute(grant_privileges_query)
        cursor.execute(grant_create_user_query)
        cursor.execute(flush_privileges_query)
        print("Committing changes.....")
        db_connection.commit()

        print("Making config.ini.....")
        # Generate encryption key
        key = generate_key()
        # Encrypt sensitive information
        encrypted_ip = encrypt(host_ip, key)
        encrypted_user = encrypt(host_user, key)
        encrypted_password = encrypt(host_password, key)
        encrypted_database = encrypt(host_db, key)

        # Store the encryption key and encrypted configuration in config.ini
        config = configparser.ConfigParser()
        config['Database'] = {
            'Key': b64encode(key).decode(),
            'Host': b64encode(encrypted_ip).decode(),
            'Name': b64encode(encrypted_database).decode()
        }

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        # Do not print the key
        print("Configuration file encrypted.")
        print("Keep the config.ini safe. It is needed for app.py to work.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if db_connection.is_connected():
            cursor.close()
            db_connection.close()
        print("Setup completed......")

if __name__ == "__main__":
    ip = input('Enter IP of the Database:')
    user = input('Enter username of root/admin of Database:')
    password = input('Enter Password of user:')
    database = 'Restaurant'

    create_database(ip, user, password)
    create_tables(ip, user, password, database)