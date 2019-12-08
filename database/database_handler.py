import sqlite3
import threading
import socket

import json

# class FetchThread(threading.Thread):
class FetchThread():
    # def __init__(self, db):
    def __init__(self):
        # threading.Thread.__init__(self)
        self.database = Database("Main")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Starting FetchThread with db: {self.database.name}")
            s.bind(("127.0.0.1", 50007)) # TODO: Resolve via DNS
            s.listen(1) # Only listen to one Connection at a time.

            # Listen forever
            while True:

                client_connection, client_address = s.accept()
                with client_connection:
                    print(f"New connection by {client_address}")
                    while True:
                        data = client_connection.recv(32768) # Max. 4Kbites of data
                        if not data:
                            break

                        decoded = data.decode("utf-8")
                        received = json.loads(decoded)
                        if(self.database.handle(received) > 0):
                            print(f"Sucessfully handled the following input: {decoded}")
                        else:
                            print(f"Something failed while handeling the input: {decoded}")


class Database():
    def __init__(self, name):
        self.name = name
        self.connection = sqlite3.connect("auth_users.db")
        print("Connected successfully to the database.")
        self.setupDatabase()

    def create_connection(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            print("Successfully connected to the database. ", sqlite3.version)
        except sqlite3.Error as e:
            print(e)
        finally:
            if self.connection:
                self.connection.close()

    def executeSql(self, createTableSql):
        try:
            cur = self.connection.cursor()
            cur.execute(createTableSql)
        except sqlite3.Error as e:
            print(e)

    def setupDatabase(self):
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS users(
                ID Int AUTO_INCREMENT,

                email TEXT NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,

                PRIMARY KEY (ID)
            )
        ''')
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS data(
                ID INT AUTO_INCREMENT,

                PRIMARY KEY (ID)
            )
        ''')
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS pax_count(
                ID INT AUTO_INCREMENT,
                userID INT NOT NULL REFERENCES users(ID),

                time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dataID INT NOT NULL,

                PRIMARY KEY (ID),
                FOREIGN KEY (userId) REFERENCES users(id),
                FOREIGN KEY (dataID) REFERENCES data(id)
            )
        ''')

    def create_new_user(self, email, password, salt):
        cur = self.connection.cursor()

        rowcount = len(cur.execute('''
            SELECT * FROM users WHERE email = (?)
        ''', [email]).fetchall()) # cur.rowcount returns -1 after a SELECT, because the API does not specify a way to receive the number of rows
        print (f"Searching if user with email \"{email}\" already exists.")
        print (f"Found {rowcount} entries with the specified email.")
        if (rowcount > 0):
            return -1 # If the email is already registered, let this fail
        # FIXME: This already doesn't work
        
        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO users(email,password,salt)
            VALUES (?,?,?)
        ''', (email, password, salt))

        rowcount = cur.rowcount
        cur.close()
        self.connection.commit()
        return rowcount == 1

    def handle(self, input:dict):
        if (input["type"] == "REGISTER"):
            return self.create_new_user(input["email"], input["password"], input["salt"])
        elif (input["type"] == "LOGIN"):
            # return self.login() TODO: Fix login
            pass
        return -9999


# db = Database("Main")

# fThread = FetchThread(Database("Main"))
fThread = FetchThread()
fThread.run()