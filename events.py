
from flask import Response
import dbhelpers
import traceback
import json
import helpers


def get_events(request):
    try:
        event_id = helpers.check_event_id(request)
    except ValueError:
        return Response("Invalid event ID", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    if event_id != None and event_id != "":
        events = dbhelpers.run_select_statement(
            "SELECT e.id, e.name, e.date_time, e.image_url, e.description, l.city_name, l.country_name, u.name, u.image_url FROM events e INNER JOIN locations l ON l.id = e.location_id INNER JOIN users u ON e.host_id = u.id WHERE e.id = ?", [event_id, ])
    else:
        events = dbhelpers.run_select_statement(
            "SELECT e.id, e.name, e.date_time, e.image_url, e.description, l.city_name, l.country_name, u.name, u.image_url FROM events e INNER JOIN locations l ON l.id = e.location_id INNER JOIN users u ON e.host_id = u.id", [])
    if type(events) == Response:
        return events
    elif events == None or events == "":
        return Response("No event data available", mimetype='text/plain', status=400)
    elif len(events) == 0 and (event_id != None or event_id != ""):
        return Response("No event data available", mimetype='text/plain', status=500)
    else:
        event_dictionaries = []
        for event in events:
            event_dictionaries.append(
                {"eventId": event[0], "eventName": event[1], "dateTime": event[2], "eventImageUrl": event[3], "description": event[4], "cityName": event[5], "countryName": event[6], "userName": event[7], "userImageUrl": event[8]})
        event_json = json.dumps(event_dictionaries, default=str)
        return Response(event_json, mimetype='application/json', status=200)


def create_event(request):
    try:
        login_token = request.json['loginToken']
        name = request.json['eventName']
        date_time = request.json['dateTime']
        city_name = request.json['cityName']
        country_name = request.json['countryName']
        image_url = request.json.get('eventImageUrl')
        description = request.json['description']
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=400)
    location_info = helpers.select_location_info(city_name, country_name)
    if type(location_info) == Response:
        return location_info
    elif location_info == None or len(location_info) != 1:
        return Response("Location not found", mimetype='text/plain', status=400)
    else:
        location_id = location_info[0][4]
        user_id = helpers.get_user_id(login_token)
        if type(user_id) == Response:
            return user_id
        elif user_id == None or len(user_id) != 1:
            return Response("User not found", mimetype='text/plain', status=400)
        else:
            sql = "INSERT INTO events (name, date_time, description, location_id, host_id"
            params = [name, date_time, description, location_id, user_id]
            if (image_url == None or image_url == ""):
                sql += ") VALUES (?, ?, ?, ?, ?)"
            else:
                if image_url != None and image_url != "":
                    sql += ", image_url"
                    params.append(image_url)
                    sql += ") VALUES (?, ?, ?, ?, ?, ?)"
            last_row_id = dbhelpers.run_insert_statement(sql, params)
            if type(last_row_id) == Response:
                return last_row_id
            elif last_row_id != None:
                location_info = helpers.select_location_info(
                    city_name, country_name)
                if type(location_info) == Response:
                    return location_info
                elif location_info != None and len(location_info) == 1:
                    return Response("No location data available", mimetype='text/plain', status=400)
                else:
                    user_info = helpers.get_user_info(user_id)
                    if type(user_info) == Response:
                        return user_info
                    elif user_info != None and len(user_info) == 1:
                        return Response("No user data available", mimetype='text/plain', status=400)
                    else:
                        new_event_dictionary = {
                            "eventId": last_row_id, "eventName": name, "description": description, "dateTime": date_time, "eventImageUrl": image_url, "loginToken": login_token, "locationId": location_info[0][4], "cityName": city_name, "countryName": country_name, "hostName": user_info[0][0], "hostImage": user_info[0][1]}
                        new_event_json = json.dumps(
                            new_event_dictionary, default=str)
                        return Response(new_event_json, mimetype='application/json', status=201)
                    #         else:
                    #             return Response("Error fetching data", mimetype='text/plain', status=500)
                    #     else:
                    #         return Response("Error logging user in", mimetype='text/plain', status=500)
                    # else:
                    #     return Response("User cannot be created. Please try again", mimetype='text/plain', status=500)
# make sure date is in the future
# def update_event(request):

# def delete_event(request):
