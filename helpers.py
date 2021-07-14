from flask import Response, request
from datetime import date
import dbhelpers
import string
import random
# create salt for pw


def createSalt():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters_and_digits) for i in range(10))
    return result_str


def get_user_id(login_token):
    user_id = dbhelpers.run_select_statement(
        "SELECT user_id FROM user_session WHERE login_token = ?", [login_token])
    return user_id

# check if user_id exists (get/args only)


def check_user_id(request):
    user_id = request.args.get('userId')
    if user_id != None:
        user_id = int(user_id)
    return user_id
# check if event_id exists(get/args only)


def get_user_info(user_id):
    user_info = dbhelpers.run_select_statement(
        "SELECT u.name, u.image_url FROM users u WHERE user_id = ?", [user_id])
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


# def select_follows(user_id, id_one, id_two, id_three):
#     select_follows = dbhelpers.run_select_statement(
#         f"SELECT u.email, u.username, u.bio, u.birthdate, u.image_url, {id_one} FROM user_follows uf INNER JOIN users u ON uf.{id_two} = u.id WHERE uf.{id_three} = ?", [user_id, ])
#     return select_follows
