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

    def setupDatabase(self):
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS users(
                ID Int AUTO_INCREMENT,

                email TEXT NOT NULL,
                passwordHash TEXT NOT NULL,
                passwordSalt TEXT NOT NULL,

                PRIMARY KEY (ID)
            )
        ''')
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS data(
                ID INT AUTO_INCREMENT,

                PRIMARY KEY (ID)
            )
        ''')
        self.connection.execute('''
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

    def newUser(self, email, password, salt):
        cursor = self.connection.cursor()
        if(cursor.execute('''
            SELECT * FROM users WHERE email = (?)
        ''', [email]).rowcount > 0):
            return -1 # If the email is already registered, let this fail
        
        rows = cursor.execute('''
            INSERT INTO users(ID,email,passwordHash,passwordSalt) VALUES (NULL,?,?,?)
        ''', [email, password, salt]).fetchall()

        return len(rows) == 1

    def handle(self, input:dict):
        if (input["type"] == "REGISTER"):
            return self.newUser(input["email"], input["password"], input["salt"])
        elif (input["type"] == "LOGIN"):
            # return self.login() TODO: Fix login
            pass
        return -9999


# db = Database("Main")

# fThread = FetchThread(Database("Main"))
fThread = FetchThread()
fThread.run()