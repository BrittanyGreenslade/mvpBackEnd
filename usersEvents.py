from flask import Response
import dbhelpers
import traceback
import json
import helpers
# def get_users_attends(request):


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
                "SELECT u.name, u.image_url, ue.event_id FROM users_events ue INNER JOIN users u ON u.id = ue.user_id WHERE ue.id = ?", [last_row_id])
            if type(new_attend) == Response:
                return new_attend
            if new_attend != None and len(new_attend) == 1:
                attend_dictionary = {
                    "name": new_attend[0][0], "userImageUrl": new_attend[0][1], "eventId": new_attend[0][2]}
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
# def get_events_attendees(request):
