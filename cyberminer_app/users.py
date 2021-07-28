from cyberminer_app import app
from flask import render_template, request, redirect, session
from cyberminer_app.dbinterface import DatabaseQuery

#directs user to a login page
@app.route('/login')
def login():
    return render_template('login.html')

#validates the user's login, and logs them in
#TODO: hash passwords rather than storing them raw
@app.route("/validateLogin", methods=["POST"])
def validateLogin():
    username = request.form['username']
    password = request.form['password']

    db = DatabaseQuery(0)

    db.cur.execute("SELECT * FROM tbl_user WHERE username = %s", (username,))

    data = db.cur.fetchall()

    if len(data) > 0 and password == data[0][2]: #accept login only if username and password match
        user = {}
        user['name'] = data[0][1]
        user['visited'] = {}
        user['id'] = data[0][0]
        user['isadmin'] = data[0][5]
        session['user'] = user

        return redirect('/search')

    return redirect('/') #PLACEHOLDER

    #else:
        #TODO: error handling

#directs user to a create account page
@app.route("/create")
def create():
    return render_template('account_create.html')

#attempts to create an account, and adds it to database if successful
@app.route("/createAccount", methods=["POST"])
def createAccount():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    db = DatabaseQuery(0)

    db.cur.execute("SELECT * FROM tbl_user WHERE username = %s", (username,))

    data = db.cur.fetchall()

    if len(data) != 0:
        return redirect('/') #PLACEHOLDER, need real error handling!
    else:
        db.cur.execute("INSERT INTO tbl_user (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        db.con.commit()
        db.cur.close()
        db.con.close()
        return redirect('/')

