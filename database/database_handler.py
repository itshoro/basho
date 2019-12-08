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
                    while True: # FIXME Right now we just read 4kb of data. We should change this so the client specifies the data length.
                        data = client_connection.recv(32768) # Max. 4Kbites of data
                        if not data:
                            break

                        decoded = data.decode("utf-8")
                        received = json.loads(decoded)

                        result = self.database.handle(received)
                        if(result[0]):
                            print(f"Sucessfully handled the following input: {decoded}")
                            if (result[1]):
                                client_connection.sendall(bytes(str(result[2]), "utf-8"))
                                print(f"Responding with: {result[2]}")
                        else:
                            print(f"Something failed while handeling the input: {decoded}")
                            client_connection.close()
                            break


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
                ID INTEGER PRIMARY KEY AUTOINCREMENT,

                email TEXT NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        ''')
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS data(
                ID INTEGER PRIMARY KEY AUTOINCREMENT
                deviceId INTEGER,



                FOREIGN KEY (device_id) REFERENCES device(ID)
            )
        ''')
        # TODO: Add data column
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS devices(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ownerId Integer NOT NULL,
                name TEXT,

                FOREIGN KEY (ownerId) REFERENCES users(ID)
            )
        ''')
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS pax_counts(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                userId INTEGER NOT NULL,
                deviceId INTEGER NOT NULL

                time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dataId INTEGER NOT NULL,

                FOREIGN KEY (userId) REFERENCES users(ID),
                FOREIGN KEY (dataId) REFERENCES data(ID)
                FOREIGN KEY (deviceId) REFERENCES device(ID)
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

        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO users(email,password,salt)
            VALUES (?,?,?)
        ''', (email, password, salt))

        rowcount = cur.rowcount
        cur.close()
        self.connection.commit()
        return rowcount == 1

    def salt(self, email):
        cur = self.connection.cursor()
        data = cur.execute('''
            SELECT salt FROM users WHERE email = (?)
        ''', [email]).fetchone()
        
        if (len(data) == 0):
            return False, False, None

        cur.close()
        return True, True, data[0]

    def login(self, email, password):
        cur = self.connection.cursor()
        data = cur.execute('''
            SELECT ID FROM users WHERE email = (?) AND password = (?)
        ''', [email, password]).fetchone()

        cur.close()
        if (type(data[0]) is not int):
            return False, False, None
        return True, True, data[0]

    def add_device(self, user_id, device_name):
        cur = self.connection.cursor()
        device = cur.execute('''
            INSERT INTO devices(ownerId,name)
            VALUES (?,?)
        ''', [user_id, device_name]).fetchone()

        cur.close()
        return True, True, device[0]

    # FIXME: Test this
    def add_data(self, user_id, device_id, data = None): # Ommiting data 
        cur = self.connection.cursor()

        # TODO Actually add data.
        data = cur.execute('''
            INSERT INTO data(deviceId)
        ''', [device_id]).fetchone()

        cur.execute('''
            INSERT INTO pax_counts(userId,deviceId,dataId)
            VALUES (?,?,?)
        ''', [user_id, device_id, data[0]])

    # Handle returns output in the following format:
    #  - Sucessfully handled Request: True / False
    #  - Has data to return to the client: True / False
    #  - Data that should be returned: obj
    def handle(self, input:dict):
        if (input["type"] == "REGISTER"):
            return self.create_new_user(input["email"], input["password"], input["salt"])
        elif (input["type"] == "GET_SALT"):
            return self.salt(input["email"])
        elif (input["type"] == "LOGIN"):
            return self.login(input["email"], input["password"])
        return -9999


# db = Database("Main")

# fThread = FetchThread(Database("Main"))
fThread = FetchThread()
fThread.run()