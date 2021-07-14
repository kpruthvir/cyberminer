from dbinterface import DatabaseQuery

interface = DatabaseQuery()
keywords = ['differential', 'material', 'analysis']
data = interface.retrieve_data(keywords, 'NOT')
print(data)