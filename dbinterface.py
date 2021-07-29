import mysql.connector
from config import Config

class DatabaseQuery:
	def __init__(self, userid):
		db_config = Config().db_config
		self.con = mysql.connector.connect(**db_config)
		self.cur = self.con.cursor()
		self.cur.execute("USE cyberminer")
		self.user = userid

	#keywords: list of strings
	#mode: "AND", "OR", or "NOT"
	def retrieve_data(self, keywords, mode, sort_order):
		#retrieve filter list, and remove all filtered characters from the search keywords
		filters = self.get_filters()

		keywords_filtered = []

		for keywd in keywords:
			for fltr in filters:
				keywd = keywd.replace(fltr[0],"")
			keywords_filtered.append(keywd)

		query = "SELECT title, url, visits FROM tbl_data WHERE keywords "
		if mode == 'NOT':
			query += "NOT LIKE '%" + keywords_filtered[0] + "%' "
		else:
			query += "LIKE '%" + keywords_filtered[0] + "%' "
		for i in range(1, len(keywords)):
			if mode == 'OR':
				query += "OR keywords LIKE '%" + keywords_filtered[i] + "%' "
			elif mode == 'AND':
				query += "AND keywords LIKE '%" + keywords_filtered[i] + "%' "
			elif mode == 'NOT':
				query += "AND keywords NOT LIKE '%" + keywords_filtered[i] + "%' "

		if sort_order == 'Alphabetical':
			query += "ORDER BY title "
		elif sort_order == 'MostFrequent':
			query += "ORDER BY visits DESC "

		self.cur.execute(query)

		results = self.cur.fetchall()
		return results

	# return a list of filters for the logged-in user
	def get_filters(self):
		filter_query = "SELECT filter FROM tbl_filter WHERE userid = " + str(self.user)

		self.cur.execute(filter_query)
		filters = self.cur.fetchall()
		return filters

	#add a new filter to the "filters" database table
	def add_filter(self, new_filter):
		filters = self.get_filters()
		for row in filters:
			if new_filter == row[0]: #return if the filter is already in the table, to avoid duplicates
				return

		query = "INSERT INTO tbl_filter (userid, filter) VALUES (" + str(self.user) + ",'" + new_filter + "')"
		self.cur.execute(query)
		self.con.commit()

	#remove the specified filter from the "filters" database table
	def remove_filter(self, target_filter):
		query = "DELETE FROM tbl_filter WHERE userid=" + str(self.user) + " AND filter='" + target_filter + "'"
		print(query)
		self.cur.execute(query)
		self.con.commit()

	#closes connection. use when done.
	def close(self):
		self.cur.close()