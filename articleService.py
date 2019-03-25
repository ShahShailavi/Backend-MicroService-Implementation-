from flask import Flask, jsonify, request, make_response,g,Response
import sqlite3
import re
from passlib.hash import sha256_crypt
from flask_api import status
from flask_httpauth import HTTPBasicAuth
import datetime
from http import HTTPStatus
import datetime

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

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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

@app.route("/postarticle", methods=['POST'])
@auth.login_required
def post_article():
    if (request.method == 'POST'):
        if not request.json.get('articletitle'):
            return jsonify("You can not create blog without article title")
        elif not request.json.get('articlecontent'):
            return jsonify("You can not create blog without article content")
        else:
            article_details = request.get_json()
            username = request.authorization.username
            temp = str(article_details['articletitle'].replace(" ","%20"))
            temp = 'http://127.0.0.1:5000/retrieveArticle/'+temp
            try:
                db = get_database()
                c = db.cursor()
                c.execute("insert into articles_table (article_title, article_content, article_author, createdDate, modifiedDate, URL) values (?,?,?,?,?,?)",
                    [article_details['articletitle'], article_details['articlecontent'], username, datetime.datetime.now(), datetime.datetime.now(),temp])
                db.commit()
                response_message = Response(status=201, mimetype='application/json')
                response_message.headers['location'] = 'http://127.0.0.1:5000/retrieveArticle/' + article_details['articletitle']

            except sqlite3.Error as er:
                print(er)
                response_message = Response(status=409, mimetype='application/json')
        return response_message

@app.route('/retrieveArticle/<articletitle>', methods=['GET'])
def getarticle(articletitle):
    if (request.method == 'GET'):
        try:
            db = get_database()
            db.row_factory = dict_factory
            c = db.cursor()
            c.execute("select article_id,article_title,article_content,URL from articles_table where article_title=(:title)",{'title':articletitle})
            article = c.fetchone()
            if article is None:
                response_message = Response(status=404, mimetype='application/json')
            else:
                return jsonify(article)
        except sqlite3.Error as er:
            print(er)
            response_message = Response(status=409, mimetype='application/json')
    return response_message

@app.route("/editarticle", methods=['PATCH'])
@auth.login_required
def editarticle():
    if (request.method == 'PATCH'):
        try:
            db = get_database()
            c = db.cursor()
            article_details = request.get_json()
            c.execute("update articles_table set article_content = (:content), modifiedDate = (:updatetime) where article_author=(:username) and article_title=(:title)"
                ,{'content':article_details['articlecontent'],'updatetime':datetime.datetime.now(),'title':article_details['articletitle'],'username':request.authorization.username})
            db.commit()
            if (c.rowcount == 1):
                response_message = Response(status=200, mimetype='application/json')
            else:
                response_message = Response(status=404, mimetype='application/json')
        except sqlite3.Error as er:
                print(er)
                response_message = Response(status=409, mimetype='application/json')
    return response_message

@app.route("/deletearticle", methods=['DELETE'])
@auth.login_required
def delete_article():
    if (request.method == 'DELETE'):
        try:
            db = get_database()
            c = db.cursor()
            article_details = request.get_json()
            c.execute("delete from articles_table where article_title=(:title) and article_author=(:username)",{"username":request.authorization.username,"title":article_details['articletitle']})
            db.commit()
            if (c.rowcount == 1):
                response_message = Response(status=200, mimetype='application/json')
            else:
                response_message = Response(status=404, mimetype='application/json')
        except sqlite3.Error as er:
                print(er)
                response_message = Response(status=409, mimetype='application/json')

    return response_message

@app.route("/retrivenrecentarticle/<numberOfArcticles>", methods=['GET'])
def retrive_Recent_Article(numberOfArcticles):
    try:
        db = get_database()
        db.row_factory = dict_factory
        c = db.cursor()
        c.execute("select article_title,article_content from articles_table order by article_id desc limit (:recentarticle)", {"recentarticle":numberOfArcticles})
        recent_articles = c.fetchall()
        recent_articles_length = len(recent_articles)
        return jsonify(recent_articles)

    except sqlite3.Error as er:
            print(er)
            response_message = Response(status=409, mimetype='application/json')

    return response_message

@app.route("/retrivemetadata/<numberOfArcticles>", methods=['GET'])
def retrive_Recent_meta_Article(numberOfArcticles):
    try:
        db = get_database()
        db.row_factory = dict_factory
        c = db.cursor()
        c.execute("select article_title, article_author, createdDate, modifiedDate, URL from articles_table order by article_id desc limit (:recentarticle)", {"recentarticle":numberOfArcticles})
        recent_articles = c.fetchall()
        recent_articles_length = len(recent_articles)
        return jsonify(recent_articles)

    except sqlite3.Error as er:
            print(er)
            response_message = Response(status=409, mimetype='application/json')

    return response_message


if __name__ == '__main__':
    app.run(debug=True)
