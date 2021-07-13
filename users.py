import hashlib
from flask import Response
import dbhelpers
import traceback
import json
import helpers
import secrets


def get_users(request):
    try:
        user_id = helpers.check_user_id(request)
    except ValueError:
        return Response("Invalid user ID", mimetype='text/plain', status=422)
    except:
        traceback.print_exc()
        return Response("Something went wrong, please try again", mimetype='text/plain', status=422)
    if user_id != None and user_id != "":
        users = dbhelpers.run_select_statement(
            "SELECT u.email, u.name, u.bio, u.join_date, u.image_url, u.id, u.linked_in_url, u.location_id FROM users u WHERE u.id = ?", [user_id, ])
    else:
        users = dbhelpers.run_select_statement(
            "SELECT u.email, u.name, u.bio, u.join_date, u.image_url, u.id, u.linked_in_url, u.location_id FROM users u", [])
    if type(users) == Response:
        return users
    elif users == None or users == "":
        return Response("No user data available", mimetype='text/plain', status=400)
    elif len(users) == 0 and (user_id != None or user_id != ""):
        return Response("No user data available", mimetype='text/plain', status=500)
    else:
        user_dictionaries = []
        for user in users:
            user_dictionaries.append(
                {"userId": user[5], "email": user[0], "name": user[1], "bio": user[2], "joinDate": user[3], "imageUrl": user[4], "linkedInUrl": user[6], "locationId": user[7]})
        user_json = json.dumps(user_dictionaries, default=str)
        return Response(user_json, mimetype='application/json', status=200)


def create_user(request):
    try:
        name = request.json['name']
        password = request.json['password']
        salt = helpers.createSalt()
        password = salt+password
        password = hashlib.sha512(password.encode()).hexdigest()
        email = request.json['email']
        bio = request.json.get('bio')
        image_url = request.json.get('imageUrl')
        linked_in_url = request.json.get('linkedInUrl')
        city_name = request.json['cityName']
        country_name = request.json['countryName']
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
    sql = "INSERT INTO users (name, password, salt, email, location_id"
    params = [name, password, salt, email, location_id]
    if (image_url == None or image_url == "") and (bio == None or bio == "") and (linked_in_url == None or linked_in_url == ""):
        sql += ") VALUES (?, ?, ?, ?, ?)"
    else:
        if image_url != None and image_url != "":
            sql += ", image_url"
            params.append(image_url)
        if bio != None and bio != "":
            sql += ", bio"
            params.append(bio)
        if linked_in_url != None and linked_in_url != "":
            sql += ", linked_in_url"
            params.append(linked_in_url)
        if len(params) == 6:
            sql += ") VALUES (?, ?, ?, ?, ?, ?)"
        elif len(params) == 7:
            sql += ") VALUES (?, ?, ?, ?, ?, ?, ?)"
        elif len(params) == 8:
            sql += ") VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    last_row_id = dbhelpers.run_insert_statement(sql, params)
    if type(last_row_id) == Response:
        return last_row_id
    elif last_row_id != None:
        login_token = secrets.token_urlsafe(60)
        session_id = dbhelpers.run_insert_statement(
            "INSERT INTO user_session(login_token, user_id) VALUES(?, ?)", [login_token, last_row_id])
        if type(session_id) == Response:
            return session_id
        elif session_id != None:
            join_date_list = dbhelpers.run_select_statement(
                "SELECT u.join_date FROM users u WHERE u.id = ?", [last_row_id])
            if type(join_date_list) == Response:
                return join_date_list
            elif join_date_list != None:
                new_user_dictionary = {
                    "userId": last_row_id, "email": email, "name": name, "bio": bio, "joinDate": join_date_list[0][0], "imageUrl": image_url, "loginToken": login_token, "locationId": location_info[0][4], "linkedInUrl": linked_in_url}
                new_user_json = json.dumps(new_user_dictionary, default=str)
                return Response(new_user_json, mimetype='application/json', status=201)
            else:
                return Response("Error fetching data", mimetype='text/plain', status=500)
        else:
            return Response("Error logging user in", mimetype='text/plain', status=500)
    else:
        return Response("User cannot be created. Please try again", mimetype='text/plain', status=00)


def update_user(request):
    salt = None
    try:
        email = request.json.get('email')
        name = request.json.get('name')
        password = request.json.get('password')
        if password != None:
            salt = helpers.createSalt()
            password = salt+password
            password = hashlib.sha512(password.encode()).hexdigest()
        bio = request.json.get('bio')
        image_url = request.json.get('imageUrl')
        linked_in_url = request.json.get('linkedInUrl')
        city_name = request.json.get('cityName')
        # how to make it necessary to update country if you update city?
        if city_name != None:
            country_name = request.json['countryName']
        else:
            country_name = request.json.get('countryName')
        login_token = request.json['loginToken']
    except KeyError:
        return Response("Please enter the required data", mimetype='text/plain', status=401)
    except:
        traceback.print_exc()
        return Response("Please try again", mimetype='text/plain', status=400)
    if email == None and name == None and password == None and bio == None and image_url == None and linked_in_url == None and city_name == None:
        return Response("Please update at least one field", mimetype='text/plain', status=400)
    else:
        params = []
        sql = "UPDATE users u INNER JOIN user_session us on u.id = us.user_id SET"
        if email != None and email != "":
            sql += " u.email = ?,"
            params.append(email)
        if name != None and name != "":
            sql += " u.name = ?,"
            params.append(name)
        if password != None and password != "":
            sql += " u.password = ?,"
            params.append(password)
        if bio != None and bio != "":
            sql += " u.bio = ?,"
            params.append(bio)
        if linked_in_url != None and linked_in_url != "":
            sql += " u.linked_in_url = ?,"
            params.append(linked_in_url)
        if image_url != None and image_url != "":
            sql += " u.image_url = ?,"
            params.append(image_url)
        if salt != None and salt != "":
            sql += "u.salt = ?,"
            params.append(salt)
        if city_name != None and city_name != "":
            location_info = helpers.select_location_info(
                city_name, country_name)
            if type(location_info) == Response:
                return location_info
            elif location_info != None and len(location_info) == 1:
                location_id = location_info[0][4]
                sql += "u.location_ud = ?,"
                params.append(location_id)
            else:
                return Response("Error fetching data", mimetype='text/plain', status=500)
        sql = sql[:-1]
        params.append(login_token)
        sql += " WHERE login_token = ?"
        rows = dbhelpers.run_update_statement(sql, params)
        if type(rows) == Response:
            return rows
        # rows updated should only ever be 1
        elif rows == 1:
            updated_user = dbhelpers.run_select_statement(
                "SELECT u.email, u.name, u.bio, u.join_date, u.image_url, u.id, u.linked_in_url, u.location_id FROM users u INNER JOIN user_session us ON u.id = us.user_id WHERE login_token = ?", [login_token, ])
            if type(updated_user) == Response:
                return updated_user
            elif updated_user != None and len(updated_user) == 1:
                updated_user_dictionary = {
                    "userId": updated_user[0][5], "email": updated_user[0][0], "name": updated_user[0][1], "bio": updated_user[0][2], "joinDate": updated_user[0][3], "imageUrl": updated_user[0][4], "linkedInUrl": updated_user[0][6], "locationId": updated_user[0][7]}
                updated_user_json = json.dumps(
                    updated_user_dictionary, default=str)
                return Response(updated_user_json, mimetype='application/json', status=201)
            else:
                return Response("Error fetching data. Please refresh the page", mimetype='text/plain', status=500)
        else:
            return Response("Error updating data", mimetype='text/plain', status=500)


def delete_user(request):
    try:
        login_token = request.json['loginToken']
        password = request.json['password']
        salt = dbhelpers.get_salt_delete(login_token)
        password = salt + password
        password = hashlib.sha512(password.encode()).hexdigest()
    except KeyError:
        return Response("Please enter the required data", mimetype='application/json', status=401)
    except:
        traceback.print_exc()
        return Response("Sorry, something went wrong", mimetype='text/plain', status=401)
    rows = dbhelpers.run_delete_statement(
        "DELETE u FROM users u INNER JOIN user_session us ON u.id = us.user_id WHERE us.login_token = ? AND u.password = ?", [login_token, password])
    if type(rows) == Response:
        return rows
    elif rows == 1:
        return Response("User deleted!", mimetype='text/plain', status=200)
    else:
        return Response("Delete error", mimetype='text/plain', status=500)
