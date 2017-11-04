import sqlite3
from datetime import datetime, timezone, timedelta
from math import cos, radians, sqrt

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
    def query_rides(self, src, radius, depart_time, time_range):
        good_rides = []
        for ride_id, ride_lat, ride_long, ride_time in \
            self.cur.execute('SELECT ride_id, ride_lat, ride_long, depart_time FROM rides'):
            if abs(ride_time - depart_time) <= time_range and est_dist(src, (ride_lat, ride_long)) <= radius:
                good_rides.append(ride_id)
        return good_rides

    # returns list of ride_ids within *radius* miles of src(lat, long)
    def filter_rides_by_src(self, src, radius):
        return [ride_id for ride_id, ride_lat, ride_long in self.cur.execute('SELECT ride_id, src_lat, src_long FROM rides')
                if est_dist(src, (ride_lat, ride_long)) <= radius]

    # closes database connectin
    def close_db(self):
        self.connection.close()

    def print_debug(self):
        print ('USERS\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM users').fetchmany(10))))
        print ('Rides\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM rides').fetchmany(10))))
        print ('Passengers\n{}'.format(rows_to_str(self.cur.execute('SELECT * FROM passengers').fetchmany(10))))

# calculates and returns *estimated* distance between two (latitude, longitude) pairs
# errors will grow large for points that are far apart
# uses simple euclidean distance between the points, multiplied by the length of one degree (110.25).
# length of a degree of longitude depends on latitude, so adjust by multiplying long by cos(lat)'
def est_dist(location1, location2):  # todo: testing
    return 110.25 * sqrt((location2[0] - location1[0])**2 +
                         cos(radians(location1[0])) * ((location2[1] - location1[1]) ** 2))

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

def test_distances():
    haegis = (42.387440, -72.526423)  # Haegis Mall
    dubois = (42.390045, -72.528268)  # W.E.B. DuBois
    hadley = (42.356632, -72.547779)  # Hadley Mall
    copley = (42.350230, -71.076577)  # Copley Square
    cvs = (42.377306, -72.520417)  # amherst CVS
    print (est_dist(haegis, dubois))
    print (est_dist(haegis, hadley))
    print (est_dist(dubois, cvs))
    print (est_dist(dubois, hadley))
    print (est_dist(copley, dubois))
    print (est_dist(dubois, copley))

if __name__ == '__main__':
    db = Database(db_file)
    db.print_debug()
    db.close_db()