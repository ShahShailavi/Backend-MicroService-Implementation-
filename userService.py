from flask import Flask, jsonify, request, make_response,g,Response
import sqlite3
import re
from passlib.hash import sha256_crypt
from flask_api import status
from flask_httpauth import HTTPBasicAuth
import datetime
from http import HTTPStatus

app = Flask(__name__)
auth = HTTPBasicAuth()

microservice_database = 'microservice.db'

def get_database():
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect(microservice_database)
        database.cursor().execute("PRAGMA foreign_keys = ON")
        database.commit()
    return database

@app.teardown_appcontext
def close_connection(exception):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

@auth.verify_password
def verify(username, password):
    db = get_database()
    c = db.cursor()
    try:
        c.execute("select userpassword from users_table where username=(:email)", {'email':username})
        row = c.fetchone()
        if row is not None:
            p = row[0]
        else:
            return False

        if (sha256_crypt.verify(password,p)):
            return True

    except sqlite3.Error as er:
        print(er)

    return False

@app.route("/createuser", methods=['POST'])
def createuser():
    if (request.method == 'POST'):
        user_details = request.get_json()
        if not request.json.get('name'):
            return jsonify("Please enter your name")
        elif not request.json.get('username'):
            return jsonify("Please enter email address")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", user_details['username']):
            return jsonify("Please enter valid email address")
        elif not request.json.get('userpassword'):
            return jsonify("Please enter your password")
        else:
            user_password = sha256_crypt.encrypt((str(user_details['userpassword'])))
            db = get_database()
            try:
                db.cursor().execute("insert into users_table (name, username, userpassword) values (?,?,?)",
                    [user_details['name'], user_details['username'], user_password])
                db.commit()
                response_message = Response(status=201, mimetype='application/json')
                response_message.headers['location'] = 'https://127.0.0.1:5000/createuser'
                return response_message
            except sqlite3.Error as e:
                print(e)
                response_message = Response(status=409, mimetype='application/json')
                return response_message
    else:
        return jsonify("enter valid details")

@app.route("/display", methods=['GET'])
def display():
    db = get_database()
    c = db.cursor()
    for row in c.execute("select * from users_table"):
        print(row)

    message = {
        'status': 201,
        'test': 'works fine: ' + request.url,
    }
    return jsonify(message)

@app.route("/deleteuser", methods=['DELETE'])
@auth.login_required
def deleteuser():
    db = get_database()
    c = db.cursor()
    username = request.authorization.username
    try:
        c.execute("delete from users_table where username=(:email)",{'email':username})
        db.commit()
        response_message = Response(status=200, mimetype='application/json')
        return response_message
    except sqlite3.Error as er:
        print(er)
        response_message = Response(status=409, mimetype='application/json')
        return response_message

@app.route("/updatepassword", methods=['PATCH'])
@auth.login_required
def updatepassword():
    db = get_database()
    c = db.cursor()
    username = request.authorization.username
    user_details = request.get_json()
    new_password = sha256_crypt.encrypt((str(user_details['new_password'])))
    try:
        c.execute("update users_table set userpassword = (:password) where username=(:email)",{'email':username,'password':new_password})
        db.commit()
        response_message = Response(status=200, mimetype='application/json')
        return response_message
    except sqlite3.Error as er:
        print(er)
        response_message = Response(status=409, mimetype='application/json')
        return response_message

if __name__ == '__main__':
    app.run(debug=True)
