from flask import Flask, render_template, request, redirect
from dbinterface import DatabaseQuery
app = Flask(__name__)

#endpoint for search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        keywords = request.form['searchbar']
        # Pass the above user input to interface and specify mode

        keywords_split = keywords.split()
        search_mode = keywords_split[0]
        print(search_mode)

        mode_specified = False
        mode = "OR"

        #determine search mode. if the first word of the search is "OR", "AND", or "NOT", set that search mode. otherwise, default to "OR".
        if search_mode == "OR":
        	mode_specified = True
        elif search_mode == "AND":
        	mode = "AND"
        	mode_specified = True
        elif search_mode == "NOT":
        	mode = "NOT"
        	mode_specified = True

        #if the user specifies a search mode, do NOT use the first word of the query as a keyword.
        if mode_specified == True:
        	keywords_split.pop(0)

        interface = DatabaseQuery()
        data = interface.retrieve_data(keywords_split, mode)
        return render_template('search.html', data=data)
    return render_template('search.html')

if __name__ == '__main__':
    app.debug = True
    app.run()