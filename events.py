from datetime import date
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
            "SELECT e.id, e.name, e.date_time, e.image_url, e.description, l.city_name, l.country_name, u.name, u.image_url, u.id, l.id FROM events e INNER JOIN locations l ON l.id = e.location_id INNER JOIN users u ON e.host_id = u.id WHERE e.id = ?", [event_id, ])
    else:
        events = dbhelpers.run_select_statement(
            "SELECT e.id, e.name, e.date_time, e.image_url, e.description, l.city_name, l.country_name, u.name, u.image_url, u.id, l.id FROM events e INNER JOIN locations l ON l.id = e.location_id INNER JOIN users u ON e.host_id = u.id", [])
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
                {"eventId": event[0], "eventName": event[1], "dateTime": event[2], "eventImageUrl": event[3], "description": event[4], "cityName": event[5], "countryName": event[6], "locationId": event[10], "hostName": event[7], "hostImageUrl": event[8], "hostId": event[9]})
        event_json = json.dumps(event_dictionaries, default=str)
        return Response(event_json, mimetype='application/json', status=200)


# stop event from being created twice = name as UK? or name, city combo?
def create_event(request):
    try:
        login_token = request.json['loginToken']
        name = request.json['eventName']
        date_time = request.json['dateTime']
        date_time = helpers.date_time_validity(date_time)
        if type(date_time) == Response:
            return date_time
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
        location_id = int(location_info[0][4])
        user_id = helpers.get_user_id(login_token)
        if type(user_id) == Response:
            return user_id
        elif user_id == None or len(user_id) != 1:
            return Response("User not found", mimetype='text/plain', status=400)
        else:
            user_id = int(user_id[0][0])
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
                    user_info = helpers.get_user_info(user_id)
                    if type(user_info) == Response:
                        return user_info
                    elif user_info != None and len(user_info) == 1:
                        new_event_dictionary = {
                            "eventId": last_row_id, "eventName": name, "description": description, "dateTime": date_time, "eventImageUrl": image_url, "locationId": location_info[0][4], "cityName": city_name, "countryName": country_name, "hostName": user_info[0][0], "hostImageUrl": user_info[0][1], "hostId": user_id}
                        new_event_json = json.dumps(
                            new_event_dictionary, default=str)
                        return Response(new_event_json, mimetype='application/json', status=201)
                    else:
                        return Response("No user data available", mimetype='text/plain', status=400)
                else:
                    return Response("No location data available", mimetype='text/plain', status=400)
            else:
                return Response("Event cannot be created. Please try again", mimetype='text/plain', status=500)


def update_event(request):
    try:
        name = request.json.get('eventName')
        description = request.json.get('description')
        date_time = request.json.get('dateTime')
        image_url = request.json.get('eventImageUrl')
        # fix when udpating location stuff done
        city_name = request.json.get('cityName')
        country_name = request.json.get('countryName')
        login_token = request.json['loginToken']
        event_id = int(request.json['eventId'])
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Please try again", mimetype='text/plain', status=400)
        # update when change city info
    if name == None and description == None and date_time == None and image_url == None and city_name == None and country_name == None:
        return Response("Please update at least one field", mimetype='text/plain', status=400)
    else:
        params = []

        sql = "UPDATE events e INNER JOIN user_session us ON e.host_id = us.user_id SET"
        if name != None and name != "":
            sql += " e.name = ?,"
            params.append(name)
        if description != None and description != "":
            sql += " e.description = ?,"
            params.append(description)
        if date_time != None and date_time != "":
            sql += " e.date_time = ?,"
            params.append(date_time)
        if image_url != None and image_url != "":
            sql += " e.image_url = ?,"
            params.append(image_url)
        # fix when udpating location stuff done
        if city_name != None and city_name != "" and country_name != None and country_name != "":
            location_info = helpers.select_location_info(
                city_name, country_name)
            if type(location_info) == Response:
                return location_info
            elif location_info != None and len(location_info) == 1:
                location_id = location_info[0][4]
                sql += " e.location_id = ?,"
                params.append(location_id)
            else:
                return Response("Error fetching data", mimetype='text/plain', status=500)
        sql = sql[:-1]
        sql += " WHERE us.login_token = ? AND e.id = ?"
        params.append(login_token)
        params.append(event_id)
        rows = dbhelpers.run_update_statement(sql, params)
        if type(rows) == Response:
            return rows
        # rows updated should only ever be 1
        elif rows == 1:
            updated_event = dbhelpers.run_select_statement(
                "SELECT e.id, e.name, e.date_time, e.image_url, e.description, l.city_name, l.country_name, l.id, u.name, u.image_url, u.id FROM events e INNER JOIN user_session us ON e.host_id = us.user_id INNER JOIN locations l on l.id = e.location_id INNER JOIN users u ON u.id = us.user_id WHERE us.login_token = ? AND e.id = ?", [login_token, event_id])
            if type(updated_event) == Response:
                return updated_event
            elif updated_event != None and len(updated_event) == 1:
                updated_event_dictionary = {
                    "eventId": updated_event[0][0], "eventName": updated_event[0][1], "dateTime": updated_event[0][2], "eventImageUrl": updated_event[0][3], "description": updated_event[0][4], "cityName": updated_event[0][5],  "countryName": updated_event[0][6], "locationId": updated_event[0][7], "userName": updated_event[0][8], "userImageUrl": updated_event[0][9], "userId": updated_event[0][10]}
                updated_event_json = json.dumps(
                    updated_event_dictionary, default=str)
                return Response(updated_event_json, mimetype='application/json', status=201)
            else:
                return Response("Error fetching data. Please refresh the page", mimetype='text/plain', status=500)
        else:
            return Response("Error updating data", mimetype='text/plain', status=500)


def delete_event(request):
    try:
        login_token = request.json['loginToken']
        event_id = int(request.json['eventId'])
    except KeyError:
        return Response("Please enter the required data", mimetype='application/json', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=401)
    rows = dbhelpers.run_delete_statement(
        "DELETE e FROM events e INNER JOIN user_session us ON e.host_id = us.user_id WHERE us.login_token = ? AND e.id = ?", [login_token, event_id])
    if type(rows) == Response:
        return rows
    elif rows == 1:
        return Response("Event deleted!", mimetype='text/plain', status=200)
    else:
        return Response("Delete error", mimetype='text/plain', status=500)

# need to find events in user current city


def get_events_at_location(request):
    try:
        location_id = int(request.args['locationId'])
    except KeyError:
        return Response("Please enter the required data", mimetype='application/json', status=401)
    except ValueError:
        return Response("Invalid location ID", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    if location_id != None and location_id != "":
        events = dbhelpers.run_select_statement(
            "SELECT e.id, e.name, e.date_time, e.image_url, e.description, l.city_name, l.country_name, u.name, u.image_url, u.id, l.id FROM events e INNER JOIN locations l ON l.id = e.location_id INNER JOIN users u ON e.host_id = u.id WHERE l.id = ?", [location_id, ])
    if type(events) == Response:
        return events
    elif events == None or events == "":
        return Response("No event data available", mimetype='text/plain', status=400)
    else:
        event_dictionaries = []
        for event in events:
            event_dictionaries.append(
                {"eventId": event[0], "eventName": event[1], "dateTime": event[2], "eventImageUrl": event[3], "description": event[4], "cityName": event[5], "countryName": event[6], "locationId": event[10], "hostName": event[7], "hostImageUrl": event[8], "hostId": event[9]})
        event_json = json.dumps(event_dictionaries, default=str)
        return Response(event_json, mimetype='application/json', status=200)
