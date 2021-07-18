import dbhelpers
from haversine import haversine
from flask import Response

# gets all pairs of cities that are within 25km of each other and puts them into their own table in db


def get_25km():
    all_cities = dbhelpers.run_select_statement(
        "SELECT l.id, l.latitude, l.longitude FROM locations l", [])
    if type(all_cities) == Response:
        print("response error")
    elif all_cities != None and len(all_cities) >= 1:
        for city in all_cities:
            for test_city in all_cities:
                if test_city[0] == city[0]:
                    continue
                city_coordinates = (city[1], city[2])
                test_city_coordinates = (test_city[1], test_city[2])
                distance = haversine(city_coordinates, test_city_coordinates)
                if distance <= 25:
                    lastrowid = dbhelpers.run_insert_statement(
                        "INSERT INTO locations_25(city_id, test_city_id) VALUES(?, ?)", [city[0], test_city[0]])
                    if type(lastrowid) == Response:
                        print("response error")
                    elif lastrowid >= 1:
                        continue
                    else:
                        print("Error inserting city into db")
    else:
        print("error fetching cities")


def get_50km():
    all_cities = dbhelpers.run_select_statement(
        "SELECT l.id, l.latitude, l.longitude FROM locations l", [])
    if type(all_cities) == Response:
        print("response error")
    elif all_cities != None and len(all_cities) >= 1:
        for city in all_cities:
            for test_city in all_cities:
                if test_city[0] == city[0]:
                    continue
                city_coordinates = (city[1], city[2])
                test_city_coordinates = (test_city[1], test_city[2])
                distance = haversine(city_coordinates, test_city_coordinates)
                if distance > 25 and distance <= 50:
                    lastrowid = dbhelpers.run_insert_statement(
                        "INSERT INTO locations_50(city_id, test_city_id) VALUES(?, ?)", [city[0], test_city[0]])
                    if type(lastrowid) == Response:
                        print("response error")
                    elif lastrowid >= 1:
                        continue
                    else:
                        print("Error inserting city into db")
    else:
        print("error fetching cities")


def get_100km():
    all_cities = dbhelpers.run_select_statement(
        "SELECT l.id, l.latitude, l.longitude FROM locations l", [])
    if type(all_cities) == Response:
        print("response error")
    elif all_cities != None and len(all_cities) >= 1:
        for city in all_cities:
            for test_city in all_cities:
                if test_city[0] == city[0]:
                    continue
                city_coordinates = (city[1], city[2])
                test_city_coordinates = (test_city[1], test_city[2])
                distance = haversine(city_coordinates, test_city_coordinates)
                if distance > 50 and distance <= 100:
                    lastrowid = dbhelpers.run_insert_statement(
                        "INSERT INTO locations_100(city_id, test_city_id) VALUES(?, ?)", [city[0], test_city[0]])
                    if type(lastrowid) == Response:
                        print("response error")
                    elif lastrowid >= 1:
                        continue
                    else:
                        print("Error inserting city into db")
    else:
        print("error fetching cities")


# get_25km()
get_50km()
get_100km()
