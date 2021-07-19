from flask import Flask, render_template, request, redirect, session, url_for
from dbinterface import DatabaseQuery
from urllib.request import urlopen
from urllib.parse import quote, urlsplit, urlunsplit
import urllib.error
from multiprocessing.dummy import Pool

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'secret_key'

#redirect to home page without manually typing full URL
@app.route('/')
def main():
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

#directs user to a login page
@app.route('/login')
def login():
    return render_template('login.html')

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
        session['user'] = user

        return redirect('/search')

    return redirect('/') #PLACEHOLDER

    #else:
        #TODO: error handling


#TODO user maynot logout -> add session timeout and reset timeout on activity
@app.route('/logout')
def logout():
    """
        Delete user from current session and insert visits to Database table `TODO`
        Assuming all users are same
    """
    user = session.pop('user', None)
    if user:
        # TODO
        # insert visits to db
        # assuming current schema with an additional Column: visits
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

def sort_by_most_freq(res):
    # make use of previous results if they are not None rather than a new query to database
    # TODO change the index for lambda
    res = sorted(res, key= lambda res_item: res_item[3], reverse= True)
    return res

# TODO temporary, doesnot need a route
# add a background scheduler
@app.route('/clean')
def delete_out_of_date_url_periodically():
    # status code == 4xx or 5xx 
    #   delete
    dataid_of_out_of_date_urls = []
    results = []
    
    db = DatabaseQuery(0)
    
    query_get_all_urls = "SELECT dataid, url FROM tbl_data"
    db.cur.execute(query_get_all_urls)
    results = db.cur.fetchall()

    # thread pool object which controls a pool of worker threads
    pool = Pool(2)

    # parallel execution of map using thread pool
    dataid_of_out_of_date_urls = pool.map(is_reachable, results)

    for dataid in dataid_of_out_of_date_urls:
        if dataid is None:
            continue

        try:
            # TODO modify query to delete 
            query_delete = "SELECT * from tbl_data WHERE dataid= %s"
            db.cur.execute(query_delete, (dataid,))
            result = db.cur.fetchone()
        except mysql.connector.Error as err:
            print(err)
        else:
            print(result)
    db.cur.close()
    db.con.close()
    
    return "Deleted {} out-of-date urls".format(len(dataid_of_out_of_date_urls))

def is_reachable(r):
    (dataid, url) = r
    url = convert_unicode_to_uri(url)
    reachable = True
    try:
        handler = urlopen(url)
    except urllib.error.HTTPError as e:
        print('Exception reason for', url,':', e.reason)
        reachable = False
    except urllib.error.URLError as e:
        print('Exception reason for', url, ':', e.reason)
    else:
        if handler.getcode() and handler.getcode() >= 400:
            reachable = False

    if not reachable:
        return dataid

def convert_unicode_to_uri(unicode_url):
    """"""
    (scheme, netloc, path, query, fragment) = urlsplit(unicode_url)
    path = quote(path)
    query = quote(query)
    fragment = quote(query)
    url = urlunsplit((scheme, netloc, path, query, fragment))
    
    return url

if __name__ == '__main__':
    app.debug = True
    app.run()