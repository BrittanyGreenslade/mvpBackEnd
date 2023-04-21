import hashlib
from flask import Response
import dbhelpers
import traceback
import json
import secrets
import helpers


def user_login(request):
    try:
        email = request.json['email']
        password = request.json['password']
        salt = dbhelpers.get_salt(email)
        password = salt + password
        password = hashlib.sha512(password.encode()).hexdigest()
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=400)
    user = dbhelpers.run_select_statement(
        "SELECT u.id, u.name, u.bio, u.email, u.join_date, u.image_url, u.linked_in_url, u.location_id FROM users u WHERE u.password = ? and u.email = ?", [password, email])
    # creates a user session
    login_id = None
    if type(user) == Response:
        return user
    elif user != None and len(user) == 1:
        user_id = int(user[0][0])
        login_token = secrets.token_urlsafe(60)
        login_id = dbhelpers.run_insert_statement(
            "INSERT INTO user_session (login_token, user_id) VALUES(?, ?)", [login_token, user_id])
        if type(login_id) == Response:
            return login_id
        elif login_id != None:
            location_info = helpers.select_location_info_id(user[0][7])
            if type(location_info) == Response:
                return location_info
            elif location_info == None or len(location_info) != 1:
                return Response("Location not found", mimetype='text/plain', status=400)
            else:
                login_dictionary = {"loginToken": login_token,
                                    "userId": user[0][0], "email": user[0][3], "name": user[0][1], "bio": user[0][2], "joinDate": user[0][4], "imageUrl": user[0][5], "linkedInUrl": user[0][6], "locationId": user[0][7], "cityName": location_info[0][0], "countryName": location_info[0][1]}
                login_json = json.dumps(login_dictionary, default=str)
                return Response(login_json, mimetype='application/json', status=201)
        else:
            return Response("Invalid login - please try again", mimetype='text/plain', status=400)
    else:
        return Response("Sorry, login information incorrect", mimetype='text/plain', status=400)


def user_logout(request):
    try:
        login_token = request.json['loginToken']
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=400)
    rows = dbhelpers.run_delete_statement(
        "DELETE us FROM user_session us WHERE us.login_token = ?", [login_token])
    if type(rows) == Response:
        return rows
    elif rows == 1:
        return Response("Logout success", mimetype='text/plain', status=200)
    else:
        return Response("Logout failed, please try again", mimetype='application/json', status=400)
