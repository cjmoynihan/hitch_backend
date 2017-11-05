__author__ = 'cj'

from flask import Flask, request, jsonify, abort
app = Flask(__name__)
from database import Database
db = Database()
from datetime import datetime, timedelta

def get_from_source(source):
    """
    :param source:
    Given a real place, as in something that Google Maps can understand, return latitude and longitude
    """
    # Logic goes here
    return source

def format_rides(ride_ids):
    """
    Turns the rides given from a query into a viewable json object
    """
    # Logic goes here
    json_object = {
        'Ride': [
            {
                'driver': {
                    'driverFirst': driverFirst,
                    'driverLast': driverLast,
                    'driverID': driverID,
                },
                'fromLoc': {
                    'lat': fromLat,
                    'long': fromLong,
                },
                'destLoc': {
                    'lat': destLat,
                    'long': destLong,
                },
                'maxPassengers': maxPassengers,
                'departureTime': departureTime,
                'passengers': [
                    {
                        'firstName': row['firstname'],
                        'lastName': row['lastname'],
                        'passengerID': row['passenger_id'],
                    } for (row,) in filter(bool, map(db.get_passenger_info, ride_ids))
                ]
            }  # More of these
        ] for (driverFirst, driverLast, driverID, fromLat, fromLong, destLat, destLong, maxPassengers, departureTime) in
        map(db.get_all_from_ride, ride_ids)
    }
    return jsonify(json_object)

@app.route('/add_account', methods=['GET'])
def add_account():
    """
    Adds the user to the account
    Expects to be passed 'email', 'firstname', and 'lastname'
    """
    data = dict(request.args)
    headers = ('email', 'firstname', 'lastname')
    json_object = {header: data.get(header) for header in headers}
    if not all(json_object.values()):
        abort(406)  # Expected user info, didn't get it
    if db.has_email(data['email']):
        abort(409)  # Conflict with other email
    db.add_user(**json_object)
    return jsonify(json_object)

@app.route('/user/<email>')
def get_user_info(email):
    result = db.user_info(email)
    headers = ('email', 'firstname', 'lastname')
    if not result:
        abort(406)  # Email doesn't exist
    return jsonify(dict(zip(headers, result)))

@app.route('/rides', methods=['GET'])
def rides():
    """
    Accepts REST api calls to get rides nearby
    :params accepted:
    # source (where looking for a ride)
    Alternatively, latitude (as float), longitude (as float)
    radius (in miles)
    start_time (current time assumed if not supplied)
    goal_time (2 hours past start_time if not supplied)
    empty_seats (true by default) Filters possible rides
    """
    # Pull out the get calls
    data = dict(request.args)
    data['start_time'] = data.get('start_time', datetime.now())
    data['goal_time'] = data.get('goal_time', data['start_time']+timedelta(hours=2))
    # Get the difference between start and end time. Assume 2 hours past if nothing given.
    data['time_range'] = data['goal_time'] - data['start_time']
    if 'source' in data.keys():
        data['latitude'], data['longitude'] = get_from_source(data['source'])  # Need to implement the get_from_source
    if all(x in data.keys() for x in ('latitude', 'longitude', 'radius', 'dest')):
        # Need lat, long, radius and dest to get anything meaninful out of this
        data['src'] = (data['latitude'], data['longitude'])
        return format_rides(db.query_rides(**data))
    # Got to return something else, if I don't have this information
    elif all(x in data.keys() for x in ('latitude', 'longitude', 'radius')):
        #return format_rides(db.find_nearby_rides(**data))
        for header in ('latitude', 'longitude', 'radius'):
            data[header] = float(data[header][0] if isinstance(data[header], list) else data[header])
        return format_rides(db.find_nearby_rides(data['radius'], data['latitude'], data['longitude']))
    else:
        return format_rides([ride_id for (ride_id,) in db.get_driver_ids()])

if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5002)
    app.run(host='127.0.0.1')
