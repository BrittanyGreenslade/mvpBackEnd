from flask import Response
import dbhelpers
import traceback
import json
import helpers
# looks like default unit is km but check?



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
                "cityName": location[0], "countryName": location[1], "locationId": location[2]})
        location_json = json.dumps(locations_list, default=str)
        return Response(location_json, mimetype='application/json', status=200)
    else:
        return Response("Error fetching data", mimetype='text/plain', status=400)


def citiesWithinDistance(request):
    try:
        city_location_id = int(request.args['cityLocationId'])
        radius = int(request.args['radius'])
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except ValueError:
        return Response("Invalid input", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    if radius == 25:
        cities = helpers.within_25(city_location_id)
    elif radius == 50:
        cities = helpers.within_50(city_location_id)
    elif radius == 100:
        cities = helpers.within_100(city_location_id)
    if type(cities) == Response:
        return cities
    elif cities == None or cities == "":
        return Response("No city data available", mimetype='text/plain', status=400)
    elif len(cities) >= 0:
        city_json = json.dumps(cities, default=str)
        return Response(city_json, mimetype='application/json', status=200)
