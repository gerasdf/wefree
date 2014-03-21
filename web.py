from flask import Flask, Response, request, abort, g, stream_with_context
app = Flask(__name__)
import json
import sqlite3
from datetime import datetime
from web_db import db_session

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
    #def generate():
    #    for row in get_db().execute('SELECT essid FROM ap'):
    #        yield ','.join(row) + '\n'
    #
    print get_db().execute('SELECT essid FROM ap').fetchall()
    return "" #Response(stream_with_context(generate()), status=200, mimetype="application/json-chunks")

@app.route('/report', methods=['POST'])
def report():
    if not request.json:
        return Response(response="{'message': 'bad json'}", status=418, mimetype="application/json")

    if not (set(request.json.keys()) == set(report_sample.keys())):
        return Response(response="{'message': 'invalid keys'}", status=418, mimetype="application/json")
    import ipdb;ipdb.set_trace()
    j = request.json
    ap = get_db().execute("SELECT bssid FROM ap WHERE bssid=?", (j['bssid'],)).fetchall()


    if not ap:
        ap = get_db().execute("INSERT INTO ap (essid, bssid), WHERE bssid=?", (j['bssid'],)).fetchall()

    data = (j['essid'], j['bssid'], j['password'], j['success'], datetime.now())
    get_db().execute('INSERT INTO report (essid,bssid,password,success,date) VALUES (?,?,?,?,?)', data)
    db = get_db()
    return ''

def connect_db():
    return sqlite3.connect("./webdb.sqlite3")

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
