import sqlite3
import threading
import socket
import secrets
import sqlite3

import json

import datetime

import utils.server_constants as types

class FetchThread():
    def __init__(self):
        self.database = Database("Main")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Starting FetchThread with db: {self.database.name}")
            s.bind(("0.0.0.0", 50007)) # TODO: Resolve via DNS
            s.listen()

            # Listen forever
            while True:
                client_connection, client_address = s.accept()
                client_connection.settimeout(3) # 3 second timeout
                with client_connection:
                    print(f"New connection by {client_address}")

                    try:
                        data = client_connection.recv(32768) # Max. 4Kbites of data
                    except socket.timeout:
                        print(f"Client timed out during sending.")
                        client_connection.close()
                        continue

                    if not data.strip() or client_connection._closed:
                        print("Client closed connection during sending.")
                        client_connection.close()
                        continue

                    decoded = data.decode("utf-8")
                    try:
                        received = json.loads(decoded)
                    except:
                        # Sometimes filtering doesn't work so this is a safe guard, so that the db handler doesn't break during parsing.
                        print("Connection is cut due to malformed input.")
                        client_connection.close()
                        continue

                    try:
                        self.database.connect()
                    except:
                        print("No hosts are online.")
                        client_connection.close()
                        continue

                    result = self.database.execute_function(received["type"], received)

                    if(result[0]):
                        print(f"Sucessfully handled the following input: {decoded}")
                        print(f"Responding with: {result[1]}")
                        client_connection.sendall(bytes(str(result[1]), "utf-8"))
                    else:
                        print(f"Something failed while handeling the input: {decoded}")

                    print(f"Closing connection for {client_connection}")
                    client_connection.close()

class Database():
    def __init__(self, name):
        self.validHosts = [
            ("primary.db"),
            ("secondary.db"),
        ]

        self.name = name

        self.user = UserHelper()
        self.device = DeviceHelper()
        self.data = DataHelper()

        print("Connected successfully to the database.")
        for host in self.validHosts:
            self.connection = sqlite3.connect(host)
            self.setupDatabase()
            self.connection.close()

    def connect(self, user="vsy", password="vsy", database="vsy"):
        for host in self.validHosts:
            try:
                self.connection = sqlite3.connect(host)
                return
            except:
                print (f"Can't connect to host {host}")
        raise Exception("No valid host online.")

    def close(self):
        self.connection.close()

    def setupDatabase(self):
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS users(
                id int NOT NULL AUTO_INCREMENT,

                email TEXT NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,

                sessionToken TEXT DEFAULT NULL,
                sessionExpiry DATETIME DEFAULT NULL,

                primary key (id)
            )
        ''')
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS devices(
                id int AUTO_INCREMENT,
                ownerId Integer NOT NULL,
                title TEXT NOT NULL,

                density INT,
                timestamp DATETIME,

                primary key (id),
                FOREIGN KEY (ownerId) REFERENCES users(ID)
            )
        ''')

    def executeSql(self, createTableSql):
        try:
            cur = self.connection.cursor()
            cur.execute(createTableSql)
        except sqlite3.Error as e:
            print(e)


    def create_connection(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            print("Successfully connected to the database. ", sqlite3.version)
        except sqlite3.Error as e:
            print(e)
        finally:
            if self.connection:
                self.connection.close()

    def execute_function(self, type, args):
        try:
            function = self.get_function_from_type(type)
        except NotImplementedError:
            return False, None # Type not supported

        cursor = self.connection.cursor(buffered=True) # i think that's wrong; but i'm getting an Unread result error
        try:
            result = function(cursor, **args)
        except:
            return False, None
        finally:
            cursor.close()

        if result and self.connection.total_changes > 0:
            self.connection.commit()
        self.connection.close()
        return result

    def get_function_from_type(self, type):
        """
        Returns the corresponding function to a type if it can find in the shared type library.
        If there is no corresponding function, it returns a "False". As would be the case with a failed request.
        If the type *doesn't* exist it raises a ValueError.
        """

        # For comedic relieve: I invested twenty minutes into writing the following commented code that allows me to get the content of
        # all the type variables, until I realized through rubber duck debugging, that this is unecessary, since the following code will
        # just waste computation power and will not bring anything to the table, since it would be the same end result if I just traverse
        # through the if / else.
        # --- Enjoy ---
        # members = [attr for attr in vars(types) if not callable(getattr(types, attr)) and not attr.startswith("__")]
        # supportedMembers = [member for member in members.keys() if not member.contains(" ")]

        # if (type not in supportedMembers):
        #     raise ValueError("Type is not supported.")
        
        if type == types.TYPE_LOGIN_USER:
            return self.user.login
        elif type == types.TYPE_REGISTER_USER:
            return self.user.register
        elif type == types.TYPE_GET_SALT:
            return self.user.get_salt
        elif type == types.TYPE_VALIDATE_SESSION:
            return self.user.verify_active_session

        elif type == types.TYPE_ADD_DEVICE:
            return self.device.add
        elif type == types.TYPE_GET_DEVICES:
            return self.device.get_all

        elif type == types.TYPE_ADD_DEVICE_DATA:
            return self.data.add
        elif type == types.TYPE_GET_DATA:
            return self.data.get_latest_data
        else:
            raise NotImplementedError()

class Helper:
    def stopRequestOnInsufficientArguments(self, required_arguments: list, actual_arguments : dict, error = None):
        if set(required_arguments).issubset(set(actual_arguments.items())):
            raise error or ValueError("Insufficient Arguments.")

class UserHelper(Helper):

    def login(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"email", "password"}, args)

        data = cursor.execute('''
            SELECT ID FROM users WHERE email = (?) AND password = (?)
        ''', [args["email"], args["password"]]).fetchone()
        if (data == None):
            # No user with the email and password combo is found => invalid data.
            return False, None

        # User credentials were correct, create a new session.
        # Sessions are valid for 7 days.
        token = self._generateSessionToken()
        cursor.execute('''
            UPDATE users
            SET sessionToken = (?), sessionExpiry = (?)
            WHERE ID = (?)
        ''',
        [
            token,
            datetime.datetime.now() + datetime.timedelta(days=7),
            data[0]
        ])
        response = {
            "user_id": data[0],
            "token": token
        }
        return True, response

    def register(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"email", "password", "salt"}, args)

        rowcount = len(cursor.execute('''
            SELECT * FROM users WHERE email = (?)
        ''', [args["email"]]).fetchall()) # cur.rowcount returns -1 after a SELECT, because the API does not specify a way to receive the number of rows
        print (f"Searching if user with email \"{args['email']}\" already exists.")
        print (f"Found {rowcount} entries with the specified email.")

        if (rowcount > 0):
            return False, None # If the email is already registered, let this fail

        cursor.execute('''
            INSERT INTO users(email,password,salt)
            VALUES (?,?,?)
        ''', (args["email"], args["password"], args["salt"]))

        rowcount = cursor.rowcount
        id = cursor.lastrowid
        return rowcount == 1, id

    def get_salt(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"email"}, args)
        data = cursor.execute('''
            SELECT salt FROM users WHERE email = (?)
        ''', [args["email"]]).fetchone()

        if (data == None or len(data) == 0):
            return False, None

        return True, data[0]

    def _generateSessionToken(self):
        return secrets.token_hex(8) # 16 character random string, ref: https://stackoverflow.com/a/50842164

    def _clearSession(self, cursor, user_id):
        cursor.execute('''
            UPDATE users 
            SET sessionToken = NULL AND sessionExpiry = NULL
            WHERE ID = (?)
        ''', [user_id])

    def verify_active_session(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"user_id", "token"}, args)
        result = cursor.execute('''
            SELECT sessionExpiry from users WHERE ID = (?) AND sessionToken = (?)
        ''', [args["user_id"], args["token"]]).fetchone()

        if result:
            expiryTime = datetime.datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f")
            if expiryTime < datetime.datetime.now():
                self._clearSession(cursor, args["user_id"])
                return False, None
            
            cursor.execute('''
                UPDATE users
                SET sessionExpiry = (?)
                WHERE ID = (?)
            ''', [datetime.datetime.now() + datetime.timedelta(days=7), args["user_id"]])
            return True, args["token"]

        self._clearSession(cursor, args["user_id"])
        return False, None

class DeviceHelper(Helper):
    def add(self, cursor, **args):
        """
        Adds a new device to the table, owned by the map specified in the userId, with the given title.
        """
        self.stopRequestOnInsufficientArguments({"userId", "title"}, args)

        result = cursor.execute('''SELECT ID from devices WHERE ownerId = (?) and title = (?)''', [args["userId"], args["title"]]).fetchone()

        if result: 
            return True, result[0]
        else:
            # Add new device
            cursor.execute('''
                INSERT INTO devices(ownerID,title)
                VALUES (?,?)
            ''', (args["userId"], args["title"]))

            rowcount = cursor.rowcount
            id = cursor.lastrowid
            return rowcount == 1, id

    def get_all(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"owner"}, args)

        result = cursor.execute('''SELECT * FROM devices WHERE ownerId=(?)''', [args["owner"]]).fetchall()

        timedelta = datetime.datetime.now() - datetime.timedelta(seconds=10) # devices are inactive after not sending data for 10 seconds
        devices = []
        for device in result:
            lastActivity = datetime.datetime.strptime(device[4], "%Y-%m-%d %H:%M:%S.%f")
            active = timedelta <= lastActivity

            devices.append({
                "token": device[0],
                "title": device[2],
                "density": device[3],
                "active": active,
                "timestamp": device[4]
            })
        return True, json.dumps(devices, skipkeys=True)

class DataHelper(Helper):
    def add(self, cursor, **args):
        """
        Adds a new data point to the list.
        """
        self.stopRequestOnInsufficientArguments({"device_token", "density"}, args)
        cursor.execute('''
            UPDATE devices
            SET density = (?), timestamp = (?)
            WHERE ID = (?)
        ''', [args["density"], datetime.datetime.now(), args["device_token"]])
        return True, True

    def get_latest_data(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"id"}, args)
        result = cursor.execute('''SELECT * from devices WHERE ID = (?)''', [args["id"]]).fetchone()

        if result:
            device = {
                "density": result[3],
                "timestamp": result[4]
            }
            return True, json.dumps(device, skipkeys=True)
        return False, None


fThread = FetchThread()
fThread.run()
