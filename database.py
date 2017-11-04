import sqlite3

db_file = 'hitch.db'
test_user1 = ('user1@umass.edu', 'User1First', 'User1Last')
test_user2 = ('user2@umass.edu', 'User2First', 'User2Last')
test_user3 = ('user3@bu.edu', 'User3First', 'User3Last')
# test_ride1 = (1, (35, 40), (36, 40), )

# todo: how storing+accessing latitude and longitude?
class Database:
    """Handle to a database."""

    # init database handle
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = sqlite3.connect(db_file)
        # configure to return as Sqlite3 Rowfactory
        self.connection.row_factory = sqlite3.Row
        self.cur = self.connection.cursor()

    # runs the script in given schema_file to instantiate (or overwrite) the database
    def init_db(self, schema_file):
        with open('schema.sql', mode='r') as f:
            self.cur.executescript(f.read())
        self.connection.commit()
        print ('Initialized Database')

    # adds user to database, given email, firstname, lastname
    # returns user's new id, or -1 if user already exists in database
    def add_user(self, email, firstname, lastname):
        return self.cur.execute('INSERT INTO users VALUES (NULL, ?, ?, ?)', (email, firstname, lastname))

    # adds a ride to the database, given all necessary information
    # source_coords and dest_coords are (latitude, longitude pairs)
    # depart_time is a timestamp (i.e. double-precision)
    # returns ride's new id, or -1 if ride already exists in database
    def add_ride(self, user_id, source_coords, dest_coords, depart_time, total_seats, cost):
        return self.cur.execute('INSERT INTO rides VALUES (NULL, ? ?, ?, ?, ?, ?, ?, ?)',
                                (user_id, source_coords[0], source_coords[1], dest_coords[0],
                                 dest_coords[1], depart_time, total_seats, cost))

    # adds given user to the given ride
    # returns id of new ride-passenger combo, or -1 if it already exists
    def add_passenger(self, passenger_id, ride_id):
        return self.cur.execute('INSERT INTO passengers VALUES(NULL, ?, ?)', (ride_id, passenger_id))

    # closes database connectin
    def close_db(self):
        self.connection.close()

    def print_debug(self):
        print ('USERS\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM users').fetchmany(10))))
        print ('Rides\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM rides').fetchmany(10))))
        print ('Passengers\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM passengers').fetchmany(10))))

# str() method for list of sqlite3.Row objects
def rows_to_str(rows):
    string = ''
    for row in rows:
        string += ', '.join([str(field) for field in row[:]]) + '\n'
    return string

if __name__ == '__main__':
    db = Database(db_file)
    # db.init_db('schema.sql')
    db.add_user(*test_user1)
    db.add_user(*test_user2)
    db.add_user(*test_user3)
    db.print_debug()
    db.close_db()
