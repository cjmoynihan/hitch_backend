import sqlite3
from datetime import datetime, timezone, timedelta
from math import cos, radians

db_file = 'hitch.db'

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

    # returns id for given email
    def get_id(self, email):
        return self.cur.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()[0]

    # returns whether given email is registered in the user database
    def has_email(self, email):
        return bool(self.cur.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone())

    # adds user to database, given email, firstname, lastname
    def add_user(self, email, firstname, lastname):
        self.cur.execute('INSERT INTO users VALUES (NULL, ?, ?, ?)', (email, firstname, lastname))
        self.connection.commit()

    # removes user from user table given user_id
    def rmv_user(self, user_id):
        self.cur.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        self.connection.commit()

    # adds a ride to the database, given all necessary information
    # source_coords and dest_coords are (latitude, longitude pairs)
    # depart_time and arrive_time are timestamps (i.e. double-precision)
    def add_ride(self, user_id, src, dest, depart_time, arrive_time, total_seats, cost):
        self.cur.execute('INSERT INTO rides VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (user_id, src[0], src[1], dest[0],
                          dest[1], depart_time, arrive_time, total_seats, cost))
        self.connection.commit()

    # removes ride from rides table given ride_id
    def rmv_ride(self, ride_id):
        self.cur.execute('DELETE FROM rides WHERE ride_id = ?', (ride_id,))
        self.connection.commit()

    # adds given user to the given ride
    def add_passenger(self, passenger_id, ride_id):
        self.cur.execute('INSERT INTO passengers VALUES(NULL, ?, ?)', (ride_id, passenger_id))
        self.connection.commit()

    # removes passenger from passengers table given id
    def rmv_passenger(self, id):
        self.cur.execute('DELETE FROM passengers WHERE id = ?', (id,))
        self.connection.commit()

    # filters available rides based on given constraints
    # src is the target starting location (latitude, longitude tuple)
    # dest is the target ending location (latitude, longitude tuple)
    # src_radius and dest_radius are respective radiuses from src and dst (miles)
    # todo: time_precision is the number of minutes we can look around depart_time and arrive_time--set to None for 0
    def query_rides(self, src, dest, src_radius, dest_radius, time_range, depart_time):
        # filtering by distance from (lat, long):
        # - 1 deg. latitude = about 69 miles
        # - 1 degree longitude = cosine(decimal latitude in degrees) * 55.2428 miles
        # see dist() function for more information
        '''Length of 1 degree of Longitude = cosine (latitude in decimal degrees) * length of degree (miles) at equator.

Convert your latitude into decimal degrees ~ 37.26383

Convert your decimal degrees into radians ~ 0.79863

1 degree of Longitude = ~0.79863 * 69.172 = ~ 55.2428 miles

More useful information from the about.com website:

Degrees of latitude are parallel so the distance between each degree remains almost constant but since degrees of longitude are farthest apart at the equator and converge at the poles, their distance varies greatly.

Each degree of latitude is approximately 69 miles (111 kilometers) apart. The range varies (due to the earth's slightly ellipsoid shape) from 68.703 miles (110.567 km) at the equator to 69.407 (111.699 km) at the poles. This is convenient because each minute (1/60th of a degree) is approximately one [nautical] mile.'''
        # self.cur.execute('SELECT * FROM rides WHERE src_lat = ? ')
        return

    # closes database connectin
    def close_db(self):
        self.connection.close()

    def print_debug(self):
        print ('USERS\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM users').fetchmany(10))))
        print ('Rides\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM rides').fetchmany(10))))
        print ('Passengers\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM passengers').fetchmany(10))))

# calculates and returns distance between two (latitude, longitude) pairs
# we get an approximation of distance with the following formula, plugging in
# the differences in latitude and longitude:
# 1 deg. latitude = about 69 miles
# 1 deg. longitude = cosine(decimal latitude in degrees) * 55.2428 miles
def dist(location1, location2):
    return abs(69 * (location2[0] - location1[0]) + 55.2428 * cos(location2[1] - location1[1]))

# str() method for list of sqlite3.Row objects
def rows_to_str(rows):
    string = ''
    for row in rows:
        string += ', '.join([str(field) for field in row[:]]) + '\n'
    return string

# returns current time instance AS DATETIME OBJECT
def get_curr_time(timezone=None):
    return datetime.now(tz=timezone)

test_user1 = ('user1@umass.edu', 'User1First', 'User1Last')
test_user2 = ('user2@umass.edu', 'User2First', 'User2Last')
test_user3 = ('user3@bu.edu', 'User3First', 'User3Last')
test_ride1 = (1, (35, 40), (36, 40), get_curr_time().timestamp(), 5, 2.50)
test_ride2 = (1, (39, 41), (38, 40), get_curr_time().timestamp(), 4, 1.50)
test_ride3 = (1, (84.871, 90.0011), (85, 90), get_curr_time().timestamp(), 5, 1.00)
test_passenger1 = (1, 2)
test_passenger2 = (1, 3)

# basic method to set up a new database with basic values. REWRITES THE DATABASE
def test_db():
    db = Database(db_file)
    db.init_db('schema.sql')
    db.add_user(*test_user1)
    db.add_user(*test_user2)
    db.add_user(*test_user3)
    db.add_ride(*test_ride1)
    db.add_ride(*test_ride2)
    db.add_ride(*test_ride3)
    db.add_passenger(*test_passenger1)
    db.add_passenger(*test_passenger2)
    return db

if __name__ == '__main__':
    # test_db()
    db = Database(db_file)
    db.print_debug()
    db.close_db()
