from flask import *
import sqlite3
import datetime
import time

app = Flask(__name__)

DATABASE = '/var/www/DraftStocked/FlaskApp/Application/redditdata.db'
secondsDay = 86400



def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = connect_to_database()
	return db

def connect_to_database():
	return sqlite3.connect(DATABASE)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
	playerList = []
	cur = get_db().cursor()
	cur.execute("SELECT * FROM Players")
	rows = cur.fetchall()
	for row in rows:
		playerList.append((row[1],row[2],row[3],row[4]))
	return render_template('index.html',playerList=playerList)

@app.route("/player/<name>")
def playerpage(name):
	commentList = []
	cur = get_db().cursor()

	cur.execute("SELECT Fullname,Stock,Change FROM Players WHERE Nickname=?",(name,))
	temp = cur.fetchone()
	playername = temp[0]
	stock = temp[1]
	change = temp[2]

	recentList = []
	otherList = []
	currentTime = int(time.time())
	cur.execute("SELECT Score,Body,Permalink,Dateposted FROM Comments WHERE Player=?",(name,))
	rows = cur.fetchall()

	for row in rows:
		t = datetime.datetime.fromtimestamp(row[3]).strftime('%m-%d-%Y')
		if row[0] > 0:
			if row[3] > currentTime-(2*secondsDay):
				recentList.append((row[0],row[1],row[2],t))
			else:
				otherList.append((row[0],row[1],row[2],t))
	recentList.sort(key=lambda x: x[0],reverse=True)			
	otherList.sort(key=lambda x: x[0],reverse=True)

	return render_template('player.html',name=playername,stock=stock,change=change,rcomments=recentList,ocomments=otherList)

if __name__ == "__main__":
    app.run()
