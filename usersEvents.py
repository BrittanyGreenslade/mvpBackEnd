from flask import Response
import dbhelpers
import traceback
import json
import helpers


def get_users_events(request):
    try:
        user_id = int(request.args['userId'])
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except ValueError:
        return Response("Invalid user ID", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    # user_id sent here is the id of the user whose events we're seeing(not host)
    events = dbhelpers.run_select_statement(
        "SELECT e.id, e.name, e.date_time, e.image_url, e.description, e.host_id, u.name, u.image_url, l.city_name, l.country_name FROM users_events ue INNER JOIN events e ON ue.event_id = e.id INNER JOIN users u ON e.host_id = u.id INNER JOIN locations l on e.location_id = l.id WHERE ue.user_id = ?", [user_id, ])
    if type(events) == Response:
        return events
    if events == None and events == "":
        return Response("Sorry, something went wrong", mimetype='text/plain', status=500)
    else:
        events_dictionaries = []
        for event in events:
            events_dictionaries.append({"userId": user_id, "eventId": event[0], "eventName": event[1], "dateTime": event[2], "eventImageUrl": event[3],
                                        "description": event[4], "hostId": event[5], "hostName": event[6], "hostImageUrl": event[7], "eventCityName": event[8], "eventCountryName": event[9]})
        event_json = json.dumps(events_dictionaries, default=str)
        return Response(event_json, mimetype='application/json', status=200)


def attend_event(request):
    try:
        login_token = request.json['loginToken']
        event_id = int(request.json['eventId'])
    except ValueError:
        return Response("Invalid event ID", mimetype='text/plain', status=422)
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=400)
    user_id = helpers.get_user_id(login_token)
    if type(user_id) == Response:
        return user_id
    elif user_id != None and len(user_id) != 0:
        user_id = int(user_id[0][0])
        last_row_id = dbhelpers.run_insert_statement(
            "INSERT INTO users_events(user_id, event_id) VALUES(?, ?)", [user_id, event_id])
        if type(last_row_id) == Response:
            return last_row_id
        if last_row_id != None:
            # refactor this?
            # new_attend = helpers.select_follows(
            #     last_row_id, 'follow_id', 'follow_id', 'id')
            new_attend = dbhelpers.run_select_statement(
                "SELECT e.id, e.name, e.date_time, e.image_url, e.description, e.host_id, u.name, u.image_url, l.city_name, l.country_name FROM users_events ue INNER JOIN users u ON u.id = ue.user_id INNER JOIN events e ON e.id = ue.event_id INNER JOIN locations l on l.id = e.location_id WHERE ue.id = ?", [last_row_id])
            if type(new_attend) == Response:
                return new_attend
            if new_attend != None and len(new_attend) == 1:
                attend_dictionary = {

                    "eventId": new_attend[0][0], "eventName": new_attend[0][1], "dateTime": new_attend[0][2], "eventImageUrl": new_attend[0][3], "description": new_attend[0][4], "hostId": new_attend[0][5], "hostName": new_attend[0][6], "hostImageUrl": new_attend[0][7], "cityName": new_attend[0][8], "countryName": new_attend[0][9]}
                attend_json = json.dumps(attend_dictionary, default=str)
                return Response(attend_json, mimetype='application/json', status=201)
        else:
            return Response("Error attending event", mimetype='text/plain', status=401)
    else:
        return Response("Sorry, something went wrong", mimetype='text/plain', status=400)


def unattend_event(request):
    try:
        login_token = request.json['loginToken']
        event_id = int(request.json['eventId'])
    except ValueError:
        return Response("Invalid event ID", mimetype='text/plain', status=422)
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
    rows = dbhelpers.run_delete_statement(
        "DELETE ue FROM users_events ue INNER JOIN user_session us ON ue.user_id = us.user_id WHERE ue.event_id = ? AND us.login_token = ?", [event_id, login_token])
    if type(rows) == Response:
        return rows
    if rows == 1:
        return Response("Unattend success!", mimetype='text/plain', status=200)
    else:
        return Response("Please try again", mimetype='text/plain', status=500)


def get_events_attendees(request):
    try:
        event_id = int(request.args['eventId'])
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except ValueError:
        return Response("Invalid event ID", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    attendees = dbhelpers.run_select_statement(
        "SELECT u.id, u.name, u.image_url, u.email, u.bio FROM users u INNER JOIN users_events ue ON ue.user_id = u.id WHERE ue.event_id = ?", [event_id, ])
    if type(attendees) == Response:
        return attendees
    if attendees == None and attendees == "":
        return Response("Sorry, something went wrong", mimetype='text/plain', status=500)
    else:
        attendees_dictionaries = []
        for attendee in attendees:
            attendees_dictionaries.append({"eventId": event_id, "attendeeId": attendee[0], "attendeeName": attendee[1], "attendeeImageUrl": attendee[2], "attendeeEmail": attendee[3],
                                           "attendeeBio": attendee[4]})
        attendee_json = json.dumps(attendees_dictionaries, default=str)
        return Response(attendee_json, mimetype='application/json', status=200)
