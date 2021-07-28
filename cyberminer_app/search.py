from cyberminer_app import app

from flask import render_template, request, redirect, session, url_for, abort, Response, jsonify
from cyberminer_app.dbinterface import DatabaseQuery


#redirect to home page without manually typing full URL
@app.route('/')
def index():
    return redirect('/search')

#endpoint for search
@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == "POST":
        print('enter search method', session)
        # add anon user for first access to search
        if 'user' not in session:
            user = {}
            user['name'] = 'anon'
            user['visited'] = {}
            user['id'] = 0 #anonymous user has ID of 0
            session['user'] = user
        
        keywords = request.form['searchbar']
        # Pass the above user input to interface and specify mode

        keywords_split = keywords.split()
        search_mode = keywords_split[0]

        mode_specified = False
        mode = "OR"

        #determine search mode. if the first word of the search is "OR", "AND", or "NOT", set that search mode. otherwise, default to "OR".
        if search_mode in ["OR", "AND", "NOT"]:
            mode_specified = True
            mode = search_mode

        #if the user specifies a search mode, do NOT use the first word of the query as a keyword.
        if mode_specified == True:
            keywords_split.pop(0)

        sort_order = request.form['sortOrder']
        if sort_order not in ['Alphabetical', 'MostFrequent']:
            sort_order = None

        interface = DatabaseQuery(session['user']['id'])
        data = interface.retrieve_data(keywords_split, mode, sort_order)

        return render_template('search.html', keywords=keywords, data=data, sortOrder=sort_order)
    
    return render_template('search.html')

#retrieves search suggestions
@app.route('/getSuggestions', methods=['GET'])
def getSuggestions():
    term = request.args.get('term') #current search term is passed by autocomplete

    db = DatabaseQuery(0)

    query = "SELECT term FROM tbl_searches WHERE term LIKE '" + term + "%' ORDER BY searches DESC LIMIT 5"
    print(query)

    db.cur.execute(query)
    data = db.cur.fetchall()

    if len(data) > 0:
        data_arr = []
        for row in data:
            data_arr.append(row[0])
        return jsonify(data_arr)
    else:
        return jsonify([])


@app.route('/visit')
def visit_website():
    """
        track no. of visits for every website any user visits using session
    """
    url = request.args.get('url', '')

    visited = session['user']['visited']

    if url not in visited:
        visited[url] = 1
    else:
        visited[url] += 1
    
    # mark session as modified to save the current  visit
    session.modified = True
    # redirect to orginal URL
    return redirect(url)

#returns the current session's username, or "None" if no one is logged in.
@app.route('/getUsername', methods=["GET"])
def getUsername():  
    
    if 'user' in session and session['user']['id'] > 0:
        db = DatabaseQuery(0)

        db.cur.execute("SELECT * FROM tbl_user WHERE userid = %s", (session['user']['id'],))
        data = db.cur.fetchall()

        if len(data) > 0:
            return str(data[0][1])
        else:
            return 'None'
    return 'None'


#TODO user maynot logout -> add session timeout and reset timeout on activity
@app.route('/logout')
def logout():
    """
        Delete user from current session and update no. of visits to Database
        Assuming all users are same
    """
    user = session.pop('user', None)
    if user:
        # insert visits to db
        visited_dict = user.get('visited', None)
        if visited_dict:
            db = DatabaseQuery(0)
            
            for url, visits in visited_dict.items():
                update_query = "UPDATE tbl_data SET visits= visits + %s WHERE url= %s"
                db.cur.execute(update_query, (visits, url))
        
            db.con.commit()
            db.cur.close()
            db.con.close()

    return redirect(url_for('search')) 
