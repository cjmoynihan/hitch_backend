import sqlite3
from datetime import datetime, timezone, timedelta
from math import cos, radians, sqrt

db_file = 'hitch.db'

# todo: how storing+accessing latitude and longitude?
class Database:
    """Handle to a database."""
    # init database handle
    def __init__(self, db_file = db_file):
        self.db_file = db_file
        # check_same_thread = False so that we can use multi-threading
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        # configure to return as Sqlite3 Rowfactory
        self.connection.row_factory = sqlite3.Row
        self.cur = self.connection.cursor()

    # runs the script in given schema_file to instantiate (or overwrite) the database
    def _init_db(self):
        with open('schema.sql', mode='r') as f:
            self.cur.executescript(f.read())
        self.connection.commit()
        print('Initialized Database')

    # returns id for given email
    def get_id(self, email):
        return self.cur.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()[0]

    def find_nearby_rides(self, radius, latitude, longitude, **kwargs):
        """
        Radius is in miles
        """
        self.cur.execute("""SELECT firstname, lastname, users.user_id, src_lat, src_long, dest_lat, dest_long, total_seats,
        depart_time FROM users JOIN rides ON users.user_id = rides.user_id""")
        return [selection for selection in self.cur if est_dist(latitude, selection.src_lat) <= radius and
                est_dist(longitude, selection.src_long) <= radius]

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

    # filters available rides based on proximity to depart_time and distance from source, destination
    # goal_src is the target starting location (latitude, longitude tuple)
    # goal_dest is the target ending location (latitude, longitude tuple)
    # src_radius and dest_radius are respective radiuses from src and dst (miles) todo: update this comment
    def query_rides(self, src, dest, radius, goal_time, time_range, use_depart=True, **kwargs):
        good_rides = []
        # build query using either depart_time or arrive_time depending on use_depart
        query = 'SELECT ride_id, src_lat, src_long, dest_lat, dest_long, {0} FROM rides'\
            .format('depart_time' if use_depart else 'arrive_time')
        for ride_id, ride_slat, ride_slong, ride_dlat, ride_dlong, time in self.cur.execute(query):
            if abs(time - goal_time) <= time_range and est_dist(src, (ride_slat, ride_slong)) <= radius and \
                    est_dist(dest, (ride_dlat, ride_dlong)) <= radius:
                good_rides.append(ride_id)
        return good_rides

    # returns info for all ri
    def get_active_user_rides(self, user_id):
        return

    def get_all_user_rides(self, user_id):
        return

    def get_all_from_ride(self, ride_id):
        # Needs troubleshooting
        self.cur.execute("""SELECT firstname, lastname, users.user_id, src_lat, src_long, dest_lat, dest_long, total_seats,
        depart_time FROM users JOIN rides ON users.user_id = rides.user_id WHERE ride_id = ?""", (ride_id,))
        return list(self.cur.fetchone())
#        result = self.cur.fetchone()
#        return list() if not result else result[0]

    def get_passenger_info(self, ride_id):
        # Need troubleshooting
        self.cur.execute("""SELECT firstname, lastname, passenger_id FROM users JOIN passengers ON users.user_id =
        passengers.passenger_id WHERE ride_id = ?""", (ride_id,))
        return self.cur.fetchall()

    def get_driver_ids(self):
        return self.cur.execute("SELECT (ride_id) FROM rides").fetchall()

    def user_info(self, email):
        return self.cur.execute("SELECT email, firstname, lastname FROM users WHERE email = ?", (email,)).fetchone()

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

haegis = (42.387440, -72.526423)  # Haegis Mall
dubois = (42.390045, -72.528268)  # W.E.B. DuBois
hadley = (42.356632, -72.547779)  # Hadley Mall
copley = (42.350230, -71.076577)  # Copley Square
cvs = (42.377306, -72.520417)  # amherst CVS

t1 = 1510388820.74 # 11/11/17 at 4:27 am
t2 = 1510389720.74 # 11/11/17 at 4:42 am
t3 = 1510390620.74 # 11/11/17 at 4:57 am
t4 = 1510392420.74 # 11/11/17 at 5:27 am
t5 = 1510406820.74 # 11/11/17 at 9:27 am

test_user1 = ('user1@umass.edu', 'User1First', 'User1Last')
test_user2 = ('user2@umass.edu', 'User2First', 'User2Last')
test_user3 = ('user3@bu.edu', 'User3First', 'User3Last')
test_ride1 = (1, haegis, dubois, t1, t2, 5, 2.50)
test_ride2 = (1, haegis, hadley, t1, t3, 4, 1.50)
test_ride3 = (2, hadley, cvs, t2, t4, 5, 1.00)
test_ride4 = (3, hadley, copley, t1, t4, 5, 20)
test_passenger1 = (1, 2)
test_passenger2 = (1, 3)

# def query_rides(self, src, dest, radius, goal_time, time_range, use_depart=True):
test_query1 = (haegis, hadley, 5, t1 + 300, 500)

# basic method to set up a new database with basic values. REWRITES THE DATABASE
def test_db():
    db = Database(db_file)
    db._init_db()
    db.add_user(*test_user1)
    db.add_user(*test_user2)
    db.add_user(*test_user3)
    db.add_ride(*test_ride1)
    db.add_ride(*test_ride2)
    db.add_ride(*test_ride3)
    db.add_ride(*test_ride4)
    db.add_passenger(*test_passenger1)
    db.add_passenger(*test_passenger2)
    return db

def test_distances():
    print (est_dist(haegis, dubois))
    print (est_dist(haegis, hadley))
    print (est_dist(dubois, cvs))
    print (est_dist(dubois, hadley))
    print (est_dist(copley, dubois))
    print (est_dist(dubois, copley))

def test_queries():
    print (db.query_rides(*test_query1))

if __name__ == '__main__':
    db = Database(db_file)
    db.print_debug()
    test_queries()
    db.close_db()
