__author__ = 'cj'

from flask import Flask, request, jsonify
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
    pass

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
                        'firstName': firstname,
                        'lastName': lastname,
                        'passengerID': passenger_id,
                    } for (firstname, lastname, passenger_id) in map(db.get_passenger_info, ride_ids)
                ]
            }  # More of these
        ] for (driverFirst, driverLast, driverID, fromLat, fromLong, destLat, destLong, maxPassengers, departureTime,
               ) in map(db.get_all_from_ride, ride_ids)
    }
    return jsonify(json_object)

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
    data = request.args
    data['start_time'] = data.get('start_time', datetime.now())
    data['goal_time'] = data.get('goal_time', data['time_min']+timedelta(hours=2))
    # Get the difference between start and end time. Assume 2 hours past if nothing given.
    data['time_range'] = data['goal_time'] - data['time_min']
    if 'source' in data.keys():
        data['latitude'], data['longitude'] = get_from_source(data['source']) # Need to implement the get_from_source
    if all(x in data.keys() for x in ('latitude', 'longitude', 'radius', 'dest')):
        # Need lat, long, radius and dest to get anything meaninful out of this
        data['src'] = (data['latitude'], data['longitude'])
        return format_rides(db.query_rides(**data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)