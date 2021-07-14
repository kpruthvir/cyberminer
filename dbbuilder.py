import mysql.connector
import csv
from config import Config

db_config = Config().db_config

conn = mysql.connector.connect(**db_config)

cur = conn.cursor()

#delete and re-create the cyberminer database
cur.execute("DROP DATABASE IF EXISTS cyberminer")
cur.execute("CREATE DATABASE cyberminer")
cur.execute("USE cyberminer")

#set up the data table
cur.execute("CREATE TABLE `cyberminer`.`tbl_data` ( `dataid` INT NOT NULL AUTO_INCREMENT , `title` VARCHAR(256) NOT NULL , `url` VARCHAR(512) NOT NULL , `keywords` VARCHAR(15000) NOT NULL , `ranking` INT NOT NULL DEFAULT '0' , PRIMARY KEY (`dataid`))")

#place entries into data table
datafile = open('dataset.csv', 'r', encoding='utf-8')
dataset = csv.reader(datafile)

for row in dataset:
	cur.execute('INSERT INTO tbl_data(title, url, keywords) VALUES (%s, %s, %s)', (row[0], row[1], row[2]))

conn.commit()
cur.close()