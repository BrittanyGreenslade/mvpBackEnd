from flask import Response
import dbhelpers
import traceback
import json


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
        "SELECT l.city_name, l.country_name, l.id FROM locations l WHERE l.city_name LIKE ? LIMIT 10", [location_name_start])
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
