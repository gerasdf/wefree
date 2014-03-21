from flask import Flask, Response, request, abort, g
app = Flask(__name__)
import json
import sqlite3

sample = {
    'essid': 'wefreenetworkessid',
    'bssid': 'A0:F3:C1:86:15:0D',
    'passwords': ['weefreenetworkwrongpassword', 'weefreenetworkpassword']
}

report_sample = {
    'essid': 'weefreenetworkwrongpassword',
    'bssid': 'A0:F3:C1:86:15:0D',
    'password': 'wrong_password',
    'success': True,
}


@app.route('/')
def index():
    return 'WeFree'

@app.route('/get', methods=['GET'])
def get_all():
    print db_fetch_all('select essid from ap')
    resp = Response(response=json.dumps(sample), status=200, mimetype="application/json-chunks")
    return resp

@app.route('/report', methods=['POST'])
def report():
    if not request.json:
        return Response(response="{'message': 'bad json'}", status=418, mimetype="application/json")

    if not (set(request.json.keys()) == set(report_sample.keys())):
        return Response(response="{'message': 'invalid keys'}", status=418, mimetype="application/json")
    # add data to db
    return ''

def connect_db():
    return sqlite3.connect("./webdb.sqlite3")

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

def db_fetch_all(query):
    db = get_db()
    cur = db.execute(query)
    return cur.fetchall()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
