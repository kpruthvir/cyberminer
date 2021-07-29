from cyberminer_app import app

from flask import session, abort, Response, request, render_template
from cyberminer_app.dbinterface import DatabaseQuery

from urllib.request import urlopen
from urllib.parse import quote, urlsplit, urlunsplit
import urllib.error
from multiprocessing.dummy import Pool
import mysql


# TODO temporary, doesnot need a route
# add a background scheduler
@app.route('/clean', methods=['GET', 'POST'])
def delete_out_of_date_url_periodically():
    """
        deletes url's with status codes == 4xx or 5xx
        only Admin can access this route
    """
    # abort if user is not an admin
    user = session.get('user', None)
    if user is None or user.get('isadmin', 0) != 1:
        abort(Response('Not Authorized', 403))

    if request.method == "GET":
        return render_template('clean.html')

    dataid_of_out_of_date_urls = []
    results = []

    db = DatabaseQuery(0)

    if request.form.get('numOfUrls', None) != None:
        query_get_all_urls = "SELECT dataid, url FROM tbl_data LIMIT {}".format(request.form.get('numOfUrls'))
    else:
        query_get_all_urls = "SELECT dataid, url FROM tbl_data"

    db.cur.execute(query_get_all_urls)
    selected_urls_to_delete = db.cur.fetchall()
    # return dict(selected_urls_to_delete)
    # thread pool object which controls a pool of worker threads
    pool = Pool(2)

    # parallel execution of map using thread pool
    dataid_of_out_of_date_urls = pool.map(is_reachable, selected_urls_to_delete)
    deleted_count = 0
    deleted_urls_dataid = ''

    for dataid in dataid_of_out_of_date_urls:
        if dataid is None:
            continue

        try:
            query_delete = "DELETE from tbl_data WHERE dataid= %s"
            db.cur.execute(query_delete, (dataid,))
            deleted_count += 1
        except mysql.connector.Error as err:
            print(err)
        else:
            deleted_urls_dataid += str(dataid) + ' '

    db.con.commit()
    db.cur.close()
    db.con.close()

    return "Deleted {} out-of-date urls. Data id's:".format(deleted_count) + deleted_urls_dataid

def is_reachable(r):
    (dataid, url) = r
    url = convert_unicode_to_uri(url)
    reachable = True
    try:
        handler = urlopen(url)
    except urllib.error.HTTPError as e:
        print('HTTP Exception reason for', url,':', e.reason)
        reachable = False
    except urllib.error.URLError as e:
        print('URL Exception reason for', url, ':', e.reason)
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