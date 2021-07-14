from flask import Flask, request
# import dbhelpers
# import json
import sys
import users
import login
import events
import usersEvents
import location
app = Flask(__name__)

# user calls


@app.get("/api/users")
def get_users():
    return users.get_users(request)


@app.post("/api/users")
def create_user():
    return users.create_user(request)


@app.patch("/api/users")
def update_user():
    return users.update_user(request)


@app.delete("/api/users")
def delete_user():
    return users.delete_user(request)
# login calls


@app.post("/api/login")
def user_login():
    return login.user_login(request)


@app.delete("/api/login")
def user_logout():
    return login.user_logout(request)

# event calls


@app.get("/api/events")
def get_events():
    return events.get_events(request)


@app.post("/api/events")
def create_event():
    return events.create_event(request)


@app.patch("/api/events")
def update_event():
    return events.update_event(request)


@app.delete("/api/events")
def delete_event():
    return events.delete_event(request)


@app.get("/api/users-events")
def get_users_attends():
    return usersEvents.attends(request)


@app.post("/api/users-events")
def attend_event():
    return usersEvents.attend_event(request)


@app.delete("/api/users-events")
def unattend_event():
    return usersEvents.unattend_event(request)


@app.get("/api/events-users")
def get_events_attendees():
    return usersEvents.get_events_attendees(request)


@app.get("/api/location")
def get_location_options():
    return location.get_location_options(request)


if(len(sys.argv) > 1):
    mode = sys.argv[1]
else:
    print("No mode argument, please pass a mode argument when invoking the file")
    exit()

if(mode == "production"):
    import bjoern  # type: ignore
    bjoern.run(app, "0.0.0.0", 5016)
elif(mode == "testing"):
    from flask_cors import CORS
    CORS(app)
    app.run(debug=True)
else:
    print("Invalid mode, please select either 'production' or 'testing'")
    exit()
