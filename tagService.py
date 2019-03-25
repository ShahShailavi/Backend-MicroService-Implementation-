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

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# To add new article with tag or to add new tags for existing article
@app.route("/tag/addtag", methods=['POST'])
@auth.login_required
def addTags():
    if (request.method == 'POST'):
        db = get_database()
        c = db.cursor()
        details = request.get_json()
        update_time = datetime.datetime.now()
        email = request.authorization.username

        try:
            tag_Details=details['tag'].split(',')
            if (not request.json.get('articleId')):
                if not request.json.get('articletitle').strip():
                    return jsonify("You can not create blog without article title")
                elif not request.json.get('articlecontent').strip():
                    return jsonify("You can not create blog without article content")
                temp = str(details['articletitle'].replace(" ", "%20"))
                temp = 'http://127.0.0.1:5000/retrieveArticle/' + temp
                c.execute(
                    "insert into articles_table (article_title, article_content, article_author, createdDate, modifiedDate, URL) values (?,?,?,?,?,?)",
                    [details['articletitle'], details['articlecontent'], request.authorization.username,
                     datetime.datetime.now(), datetime.datetime.now(), temp])
                articleId=c.lastrowid
                print(articleId)
                db.commit()
            else:
                articleId = details['articleId']
            for tags in tag_Details:
                tag=tags.strip()
                c.execute("SELECT tagId FROM tag_master WHERE tagName=?",(tag,))
                rec=c.fetchall()
                rowsaffected=len(rec)
                if rowsaffected == 0:
                    c.execute("INSERT INTO tag_master (tagName,createdTime,updatedTime) VALUES (?,?,?)",(tag,datetime.datetime.now(), datetime.datetime.now()))
                    db.commit()
                    c.execute("SELECT tagId FROM tag_master WHERE tagName=?",(tag,))
                    rec2=c.fetchall()
                    tid=rec2[0][0]
                    c.execute("INSERT INTO tag_detail (article_id,tagId,createdTime,updatedTime) VALUES (?,?,?,?)",(articleId,tid,datetime.datetime.now(), datetime.datetime.now()))
                else:
                    print("inside else")
                    tid=rec[0][0]
                    c.execute("INSERT INTO tag_detail VALUES (?,?,?,?)",(articleId,tid,datetime.datetime.now(), datetime.datetime.now()))

                if (c.rowcount == 1):
                    db.commit()
                    response = Response(status=201, mimetype='application/json')

                else:
                    response = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response


#Delete a tag
@app.route("/tag/deletetag", methods=['DELETE'])
#@auth.login_required
def deletetag():
    if (request.method == 'DELETE'):
        try:
            db = get_database()
            c = db.cursor()
            details = request.get_json()
            artid= details['articleId']
            tag=details['tag']
            print(tag)
            #for tag in tags:
            print("in for loop" + str(artid))
            c.execute("DELETE FROM tag_detail WHERE article_id=? AND tagId IN (SELECT tagId FROM tag_master WHERE tagName=?)",(artid,str(tag),))
            db.commit()
            if (c.rowcount == 1):
                db.commit()
                response = Response(status=200, mimetype='application/json')
            else:
                response = Response(status=404, mimetype='application/json')
        except sqlite3.Error as er:
                print(er)
                response = Response(status=409, mimetype='application/json')

    return response


#Retrive Tags for article id
@app.route("/tag/gettag/<artid>", methods=['GET'])
def getarticle(artid):
    if (request.method == 'GET'):
        try:
            db = get_database()
            db.row_factory = dict_factory
            c = db.cursor()
            c.execute("SELECT * FROM tag_master WHERE tagId IN (SELECT tagId FROM tag_detail WHERE article_id=?)",(artid,))
            row = c.fetchall()
            db.commit()
            if row is not None:
                return jsonify(row)
            else:
                response = Response(status=404, mimetype='application/json')

        except sqlite3.Error as er:
                print(er)
                response = Response(status=409, mimetype='application/json')

    return response

# get all the articles for a specific tag
@app.route('/tag/getarticles/<tag>',methods=['GET'])
def getart(tag):
    try:
        db = get_database()
        db.row_factory = dict_factory
        c = db.cursor()
        c.execute("SELECT URL from articles_table  where article_id =(SELECT article_id FROM tag_detail WHERE tagId IN (SELECT tagId FROM tag_master WHERE tagName=?))",(tag,))

        row = c.fetchall()
        db.commit()
        if row is not None:
            return jsonify(row)
        else:
            response = Response(status=404, mimetype='application/json')

    except sqlite3.Error as er:
            print(er)
            response = Response(status=409, mimetype='application/json')

    return response

if __name__ == '__main__':
    app.run(debug=True)
