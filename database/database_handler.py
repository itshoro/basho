import sqlite3
import threading
import socket
import secrets

import json

import datetime

import utils.server_constants as types

class FetchThread():
    # def __init__(self, db):
    def __init__(self):
        # threading.Thread.__init__(self)
        self.database = Database("Main")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Starting FetchThread with db: {self.database.name}")
            s.bind(("127.0.0.1", 50007)) # TODO: Resolve via DNS
            s.listen(5) # Only listen to one Connection at a time.

            # TODO Add timeout
            # Listen forever
            while True:
                client_connection, client_address = s.accept()
                with client_connection:
                    print(f"New connection by {client_address}")
                    data = client_connection.recv(32768) # Max. 4Kbites of data
                    if not data:
                        client_connection.close()

                    decoded = data.decode("utf-8")
                    received = json.loads(decoded)
                    result = self.database.execute_function(received["type"], received)
                    if(result[0]):
                        print(f"Sucessfully handled the following input: {decoded}")
                        print(f"Responding with: {result[1]}")
                        client_connection.sendall(bytes(str(result[1]), "utf-8"))
                    else:
                        print(f"Something failed while handeling the input: {decoded}")

                    print(f"Closing connection for {client_connection}")
                    client_connection.close()



# Currently any of the ...Helper classes pose a potential security risk and could be made more secure, by
# instead of requiring the ownerId / mapId, we would require the users sessionToken
class Database():
    def __init__(self, name):
        self.name = name
        self.connection = sqlite3.connect("auth_users.db")

        self.user = UserHelper()
        self.device = DeviceHelper()
        self.data = DataHelper()

        print("Connected successfully to the database.")
        self.setupDatabase()

    def setupDatabase(self):
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS users(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,

                email TEXT NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,

                sessionToken TEXT,
                sessionExpiry DATETIME
            )
        ''')
        self.executeSql('''
            CREATE TABLE IF NOT EXISTS devices(
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ownerId Integer NOT NULL,
                title TEXT NOT NULL,

                density INT,
                timestamp DATETIME,
                
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

    # def requires_authentication(self, type):
    #     if (type == types.TYPE_ADD_DEVICE):
    #         return True
    #     elif (type == types.TYPE_DELETE_DEVICE):
    #         return True
    #     else:
    #         return False

    def execute_function(self, type, args):
        # if self.requires_authentication(type) and "auth" not in args.keys():
        #     return False
        function = self.get_function_from_type(type)
        
        cursor = self.connection.cursor()
        try:
            result = function(cursor, **args)
        except:
            return False, None
        finally:
            cursor.close()

        if result and self.connection.total_changes > 0:
            self.connection.commit()
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

# TODO: Implement API Endpoints
class DeviceHelper(Helper):
    def add(self, cursor, **args):
        """
        Adds a new device to the table, owned by the map specified in the userId, with the given title.
        """
        self.stopRequestOnInsufficientArguments({"userId", "title"}, args)

        result = cursor.execute('''SELECT ID from devices WHERE ownerID = (?) and title = (?)''', [args["userId"], args["title"]]).fetchone()

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

    def remove(self, userId, token):
        """
        Removes a device by it's token if a map with the specified Id owns it.
        """
        pass


# TODO: Implement API Endpoints
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

    # Devices need to send data in a set interval. When a device doesn't send within let's say 60 seconds,
    # throw an error that the device is not running
    def get_latest_data(self, cursor, **args):
        self.stopRequestOnInsufficientArguments({"id"}, args)
        result = cursor.execute('''SELECT timestamp, density from devices WHERE ownerID = (?) and title = (?)''', [args["userId"], args["title"]]).fetchone()

        # TODO Improve response (see comment above)
        if result:
            return True, result[1]
        return False, None


fThread = FetchThread()
fThread.run()