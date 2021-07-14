import mysql.connector

class DatabaseQuery:
	def __init__(self):
		self.con = mysql.connector.connect(host='localhost', port='8889', user='root', passwd='root')
		self.cur = self.con.cursor()
		self.cur.execute("USE cyberminer")

	#keywords: list of strings
	#mode: "AND", "OR", or "NOT"
	def retrieve_data(self, keywords, mode):
		query = "SELECT title, url, ranking FROM tbl_data WHERE keywords "
		if mode == 'NOT':
			query += "NOT LIKE '%" + keywords[0] + "%' "
		else:
			query += "LIKE '%" + keywords[0] + "%' "
		for i in range(1, len(keywords)):
			if mode == 'OR':
				query += "OR keywords LIKE '%" + keywords[i] + "%' "
			elif mode == 'AND':
				query += "AND keywords LIKE '%" + keywords[i] + "%' "
			elif mode == 'NOT':
				query += "AND keywords NOT LIKE '%" + keywords[i] + "%' "
		self.cur.execute(query)

		results = self.cur.fetchall()
		return results

	#closes connection. use when done.
	def close(self):
		self.cur.close()