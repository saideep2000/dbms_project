from flask import render_template, session,request, redirect, url_for, Blueprint
from db import db
events_bp = Blueprint("events_bp", __name__)


@events_bp.route("/events")
def events():
    user_id = session["user_id"]
    with db.cursor() as cursor:
        # get the events user is hosting
        query1 = "SELECT * FROM User_Event WHERE user_id=%s"
        cursor.execute(query1, user_id)
        user_events = cursor.fetchall()
        user_hosting_events = []
        for user_event in user_events:
            query2 = "SELECT * FROM UEvent WHERE event_id=%s"
            cursor.execute(query2, user_event.get("event_id"))
            user_hosting_events.append(cursor.fetchone())

        # get the events user is/will be attending
        query3 = "SELECT * FROM attended_by WHERE user_id=%s"
        cursor.execute(query3, user_id)
        user_events = cursor.fetchall()
        user_attending_events = []
        for user_event in user_events:
            query4 = "SELECT * FROM UEvent WHERE event_id=%s"
            cursor.execute(query4, user_event.get("event_id"))
            user_attending_events.append(cursor.fetchone())

        # get all events
        query5 = "SELECT * FROM UEvent"
        cursor.execute(query5)
        all_events = cursor.fetchall()

        return render_template("events.html", all_events=all_events,
                               user_hosting_events=user_hosting_events,
                               user_attending_events=user_attending_events)


@events_bp.route("/event")
def event():
    user_id = session["user_id"]
    event_id = request.args.get("event_id")
    with db.cursor() as cursor:
        query = "SELECT * FROM UEvent WHERE event_id=%s"
        cursor.execute(query, event_id)
        event = cursor.fetchone()

        already_registered = False
        query1 = "SELECT * FROM Attended_by WHERE event_id=%s AND user_id=%s"
        cursor.execute(query1, (event_id, user_id))
        if cursor.rowcount == 1:
            already_registered = True
        query2 = "SELECT * FROM nuser WHERE id=%s"
        cursor.execute(query2, user_id)
        host = cursor.fetchone()
        host_name = host.get("first_name") + " " + host.get("last_name")

        query_get_carpools_for_this_event = "SELECT carpool_id FROM carpool WHERE event_id=%s"
        cursor.execute(query_get_carpools_for_this_event, event_id)
        carpools_this_event = cursor.fetchall()
        user_joined_carpool = 0
        for carpool in carpools_this_event:
            query_carpools_user = "SELECT * FROM joins WHERE carpool_id=%s AND user_id=%s"
            cursor.execute(query_carpools_user, (carpool.get("carpool_id"), user_id))
            carpool_user = cursor.fetchone()
            if cursor.fetchone():
                user_joined_carpool = carpool_user.get("carpool_id")
                break
        if user_joined_carpool:
            query_get_carpool = "SELECT * FROM carpool WHERE carpool_id=%s"
            cursor.execute(query_get_carpool, user_joined_carpool)
            carpool = cursor.fetchone()

            query_get_user_name = "SELECT first_name, last_name, phone_number FROM nuser WHERE id=%s"
            cursor.execute(query_get_user_name, carpool.get("user_id"))
            user = cursor.fetchone()
            carpool["user_name"] = user.get("first_name") + " " + user.get("last_name")
            carpool["host_phone_number"] = user.get("phone_number")

            query_get_vehicle = "SELECT * FROM vehicle WHERE vehicle_id=%s AND user_id=%s"
            cursor.execute(query_get_vehicle, (carpool.get("vehicle_id"), carpool.get("user_id")))
            vehicle = cursor.fetchone()
            carpool["vehicle_type"] = vehicle.get("vehicle_type")
            return render_template("event_carpool_dont_register.html", event=event, host_name=host_name,
                                   already_registered=already_registered, carpool=carpool)
        else:
            return render_template("event_carpool_allow_register.html", event=event, host_name=host_name,
                                   already_registered=already_registered)

@events_bp.route("/event_attended_by")
def event_attendies():
    user_id = session["user_id"]
    event_id = request.args.get("event_id")
    print("event id: " + event_id)
    with db.cursor() as cursor:
        query = "SELECT * FROM Attended_by WHERE event_id=%s AND user_id=%s"
        cursor.execute(query, (event_id, user_id))
        if cursor.rowcount == 1:
            print("Already registered for the event")
        else:
            query_attended = "INSERT INTO Attended_by(event_id, user_id) VALUES(%s, %s)"
            cursor.execute(query_attended, (event_id, user_id))
            db.commit()
            query = "SELECT * FROM UEvent WHERE event_id=%s"
            cursor.execute(query, event_id)
            event = cursor.fetchone()

            already_registered = False
            query1 = "SELECT * FROM Attended_by WHERE event_id=%s AND user_id=%s"
            cursor.execute(query1, (event_id, user_id))
            if cursor.rowcount == 1:
                already_registered = True
            query2 = "SELECT * FROM nuser WHERE id=%s"
            cursor.execute(query2, user_id)
            host = cursor.fetchone()
            host_name = host.get("first_name") + " " + host.get("last_name")
    return render_template("event_carpool_allow_register.html", event=event, host_name=host_name,
                           already_registered=already_registered)


@events_bp.route("/create_event")
def create_event():
    return render_template("create_event.html")

@events_bp.route("/create_event", methods=["POST"])
def create_event_post():
    title = request.form["title"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    max_people = request.form["max_people"]
    fees = request.form["fees"]
    requirements = request.form["requirements"]
    street = request.form["street"]
    city = request.form["city"]
    zipcode = request.form["zipcode"]
    min_age = request.form["min_age"]
    interest_type = request.form["interest_type"]
    agenda = request.form["agenda"]
    user_id = session["user_id"]
    with db.cursor() as cursor:
        # check if the username already exists
        query = "SELECT * FROM uevent WHERE title=%s"
        cursor.execute(query, title)
        event = cursor.fetchone()

        if event:
            return redirect(url_for("events_bp.events"))
        else:
            # insert the new user into the database
            # TODO: When user creates an event, he should be added to attended by
            query = "INSERT INTO uevent (start_time, end_time, max_people, fees, requirements, street_name, city, zip_code, min_age, title, agenda, host_id, interest_type)" \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (start_time, end_time, max_people, fees, requirements, street, city, zipcode, min_age, title, agenda, user_id, interest_type))
            db.commit()
            return redirect(url_for("events_bp.events"))