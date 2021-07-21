from flask import Response
import dbhelpers
import string
import random
from datetime import datetime
import json
# create salt for pw


def createSalt():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters_and_digits) for i in range(10))
    return result_str


def get_user_id(login_token):
    user_id = dbhelpers.run_select_statement(
        "SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
    return user_id
# this works b/c email is a UK


# def get_user_id(email):
#     user_id = dbhelpers.run_select_statement(
#         "SELECT user_id FROM user_session WHERE login_token = ?", [email])
#     return user_id

# check if user_id exists (get/args only)


def check_user_id(request):
    user_id = request.args.get('userId')
    if user_id != None:
        user_id = int(user_id)
    return user_id
# check if event_id exists(get/args only)


def get_user_info(user_id):
    user_info = dbhelpers.run_select_statement(
        "SELECT u.name, u.image_url FROM users u WHERE u.id = ?", [user_id])
    return user_info


def check_event_id(request):
    event_id = request.args.get('eventId')
    if event_id != None:
        event_id = int(event_id)
    return event_id

# get location info


def select_location_info(city_name, country_name):
    location_info = dbhelpers.run_select_statement(
        "SELECT l.city_name, l.country_name, l.longitude, l.latitude, l.id FROM locations l WHERE l.city_name = ? AND l.country_name = ?", [city_name, country_name])
    return location_info


def select_location_info_id(location_id):
    location_info = dbhelpers.run_select_statement(
        "SELECT l.city_name, l.country_name, l.longitude, l.latitude, l.id FROM locations l WHERE l.id = ?", [location_id, ])
    return location_info


# def get_img(user_id):
#     image_url = dbhelpers.run_select_statement(
#         "SELECT u.image_url FROM users u WHERE u.id = ?", [user_id, ])
#     return image_url


def date_time_validity(date_time):
    if date_time != "":
        date_time = datetime.fromisoformat(date_time)
        # this converts the bday input string to a number so can do math
        if date_time <= datetime.now():
            result = Response("Invalid date input",
                              mimetype='text/plain', status=400)
        else:
            result = date_time
    else:
        result = Response("Invalid date input",
                          mimetype='text/plain', status=400)
    return result

# events within 25 km of user


def within_25(city_location_id, user_id):
    user_city_info = dbhelpers.run_select_statement(
        "SELECT u.location_id FROM users u WHERE u.id = ?", [user_id, ])
    if type(user_city_info) == Response:
        city_dictionaries = user_city_info
    elif user_city_info == None or user_city_info == "":
        city_dictionaries = Response(
            "No city data available", mimetype='text/plain', status=400)
    elif len(user_city_info) >= 0:
        cities = dbhelpers.run_select_statement(
            "SELECT l.test_city_id FROM locations_25 l INNER JOIN users u ON l.city_id = u.location_id WHERE u.location_id = ? and u.id = ?", [city_location_id, user_id])
        if type(cities) == Response:
            city_dictionaries = cities
        elif cities == None or cities == "":
            city_dictionaries = Response(
                "No city data available", mimetype='text/plain', status=400)
        elif len(cities) >= 0:
            city_dictionaries = []
            # print(user_city_info[0][0])
            city_dictionaries.append({"cityId": user_city_info[0][0]})
            for city in cities:
                city_dictionaries.append(
                    {"cityId": city[0]})
    return city_dictionaries
# events within 50 km of user


def within_50(city_location_id, user_id):
    cities_25 = dbhelpers.run_select_statement(
        "SELECT l.test_city_id FROM locations_25 l INNER JOIN users u ON l.city_id = u.location_id WHERE u.location_id = ? and u.id = ?", [city_location_id, user_id])
    cities_50 = dbhelpers.run_select_statement(
        "SELECT l.test_city_id FROM locations_50 l INNER JOIN users u ON l.city_id = u.location_id WHERE u.location_id = ? and u.id = ?", [city_location_id, user_id])
    if type(cities_25) == Response:
        city_dictionaries = cities_25
    if type(cities_50) == Response:
        city_dictionaries = cities_50
    elif cities_25 == None or cities_25 == "" or cities_50 == None or cities_50 == "":
        city_dictionaries = Response(
            "No city data available", mimetype='text/plain', status=400)
    elif len(cities_25) >= 0 and len(cities_50) >= 0:
        city_dictionaries = []
        for city in cities_25:
            city_dictionaries.append(
                {"cityId": city[0]})
        for city in cities_50:
            city_dictionaries.append(
                {"cityId": city[0]})
    return city_dictionaries

# events within 100 km of user


def within_100(city_location_id, user_id):
    cities_25 = dbhelpers.run_select_statement(
        "SELECT l.test_city_id FROM locations_25 l INNER JOIN users u ON l.city_id = u.location_id WHERE u.location_id = ? and u.id = ?", [city_location_id, user_id])
    cities_50 = dbhelpers.run_select_statement(
        "SELECT l.test_city_id FROM locations_50 l INNER JOIN users u ON l.city_id = u.location_id WHERE u.location_id = ? and u.id = ?", [city_location_id, user_id])
    cities_100 = dbhelpers.run_select_statement(
        "SELECT l.test_city_id FROM locations_100 l INNER JOIN users u ON l.city_id = u.location_id WHERE u.location_id = ? and u.id = ?", [city_location_id, user_id])
    if type(cities_25) == Response:
        city_dictionaries = cities_25
    elif type(cities_50) == Response:
        city_dictionaries = cities_50
    elif type(cities_100) == Response:
        city_dictionaries = cities_100
    elif cities_25 == None or cities_25 == "" or cities_50 == None or cities_50 == "" or cities_100 == None or cities_100 == "":
        city_dictionaries = Response(
            "No city data available", mimetype='text/plain', status=400)
    elif len(cities_25) >= 0 and len(cities_50) >= 0 and len(cities_100) >= 0:
        city_dictionaries = []
        for city in cities_25:
            city_dictionaries.append(
                {"cityId": city[0]})
        for city in cities_50:
            city_dictionaries.append(
                {"cityId": city[0]})
        for city in cities_100:
            city_dictionaries.append(
                {"cityId": city[0]})
    return city_dictionaries
