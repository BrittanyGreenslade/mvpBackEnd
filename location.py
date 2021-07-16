from flask import Response
import dbhelpers
import traceback
import json
# looks like default unit is km but check?

from haversine import haversine
# , Unit


def get_location_options(request):
    try:
        location_name_start = request.args['firstThree']
        location_name_start = location_name_start + '%'
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=400)
    location_options = dbhelpers.run_select_statement(
        "SELECT l.city_name, l.country_name, l.id FROM locations l WHERE l.city_name LIKE ? LIMIT 10", [location_name_start, ])
    if type(location_options) == Response:
        return location_options
    elif location_options != None and len(location_options) >= 1:
        locations_list = []
        for location in location_options:
            locations_list.append({
                "cityNames": location[0], "countryNames": location[1], "locationId": location[2]})
        location_json = json.dumps(locations_list, default=str)
        return Response(location_json, mimetype='application/json', status=200)
    else:
        return Response("Error fetching data", mimetype='text/plain', status=400)

# dist from user to event


def distance_user_event(request):
    try:
        user_id = int(request.args['userId'])
        event_id = int(request.args['eventId'])
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except ValueError:
        return Response("Invalid input", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    user_location_list = dbhelpers.run_select_statement(
        "SELECT l.latitude, l.longitude FROM users u INNER JOIN locations l ON u.location_id = l.id WHERE u.id = ?", [user_id, ])
    event_location_list = dbhelpers.run_select_statement(
        "SELECT l.latitude, l.longitude FROM events e INNER JOIN locations l ON e.location_id = l.id WHERE e.id = ?", [event_id, ])
    user_coordinates = (user_location_list[0][0], user_location_list[0][1])
    event_coordinates = (event_location_list[0][0], event_location_list[0][1])
    distance = haversine(user_coordinates, event_coordinates)
    print(distance)
    # event_coordinates = {
    #     "eventLatitude": event_location_list[0][0], "eventLongitude": event_location_list[0][1]}
    # event_coordinates_json = json.dumps(event_coordinates, default=str)

    return Response("very good", mimetype='text/plain', status=201)
# events within certain km of user (drop down option?)
