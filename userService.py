from flask import Flask, jsonify, request, make_response,g
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
        c.execute("select userpassword from users_table where useremail=(:email)", {'email':username})
        row = c.fetchone()
        if row is not None:
            print("Inside If")
            p = row[0]
            print(p)
        else:
            return False

        if (sha256_crypt.verify(password,p)):
            return True
        '''
        c.execute("select * from users where email=(:email) and password=(:password)",{'email':username,'password':password})
        n = c.fetchone()[0]

        if (n == 1):
            return True
        '''
    except sqlite3.Error as er:
        print(er)

    return False


@app.route("/createuser", methods=['POST'])
def createuser():
    if (request.method == 'POST'):
        print("Inside Post method")
        user_details = request.get_json()
        print(user_details)
        if not user_details['name']:
            print("Inside If")
            response_message = 'Please enter your name'
        elif not user_details['username'] or not re.match(r"[^@]+@[^@]+\.[^@]+", user_details['username']):
            print("Inside elif")
            response_message = 'Please enter your valid email address'
        elif not user_details['userpassword']:
            response_message = 'Please enter your password'
        else:
            user_password = sha256_crypt.encrypt((str(user_details['userpassword'])))
            db = get_database()
            try:
                db.cursor().execute("insert into users_table (username, useremail, userpassword) values (?,?,?)",
                    [user_details['name'], user_details['username'], user_password])
                db.commit()
                response_message = {
                    'status': 201,
                    'message': 'Created: ' + request.url,
                }
            except sqlite3.Error as e:
                print(e)
                return make_response(jsonify({'Error Message': 'Conflict'}), 409)

        #for row in db.cursor().execute("select * from users_table"):
            #print(row)
    else:
        return jsonify("enter valid details")
    response = jsonify(response_message)
    return make_response(response)

@app.route("/display", methods=['POST'])
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

@app.route("/deleteuser", methods=['POST'])
@auth.login_required
def deleteuser():
    db = get_database()
    c = db.cursor()
    print("Inside delete user function")
    user_details = request.get_json()
    message = {}
    try:
        c.execute("select userpassword from users_table where useremail=(:email)", {'email':user_details['useremail']})
        row = c.fetchone()
        if row is not None:
            print("Inside If")
            p = row[0]
            print(p)
            if(sha256_crypt.verify(user_details['userpassword'],p)):
                print("Inside If")
                c.execute("delete from users_table where useremail=(:email)",{'email':user_details['useremail']})
                db.commit()
                print("Record deleted")
                message = {
                    'status': 201,
                    'mesg': 'Deleted: ' + request.url,
                }
            else:
                message = {
                    'status': 201,
                    'mesg': 'Password does not match: ' + request.url,
                }
        else:
            message = {
                'status': 201,
                'mesg': 'User does not match: ' + request.url,
            }

    except sqlite3.Error as er:
            print(er)

    return jsonify(message)

@app.route("/updatepassword", methods=['POST'])
@auth.login_required
def updatepassword():
    db = get_database()
    c = db.cursor()
    message = {}
    print("inside update password")
    user_details = request.get_json()
    new_password = sha256_crypt.encrypt((str(user_details['new_password'])))
    #print(details['name'])
    print(user_details['useremail'])
    #print(details['password'])
    #print(pas)
    try:
        c.execute("select userpassword from users_table where useremail=(:email)", {'email':user_details['useremail']})
        row = c.fetchone()
        if row is not None:
            p = row[0]
            print(p)
            if(sha256_crypt.verify(user_details['userpassword'],p)):
                print("Inside If")
                c.execute("update users_table set userpassword = (:password) where useremail=(:email)",{'email':user_details['useremail'], 'password':new_password})
                db.commit()
                print("password updated")
                message = {
                    'status': 201,
                    'mesg': 'Password Updated: ' + request.url,
                }
            else:
                message = {
                    'status': 201,
                    'mesg': 'Password does not match: ' + request.url,
                }
        else:
            message = {
                'status': 201,
                'mesg': 'User does not match: ' + request.url,
            }

    except sqlite3.Error as er:
        print(er)

    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)
