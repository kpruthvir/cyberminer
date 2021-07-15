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
cur.execute("CREATE TABLE `cyberminer`.`tbl_data` ( `dataid` INT NOT NULL AUTO_INCREMENT , `title` VARCHAR(256) NOT NULL , `url` VARCHAR(512) NOT NULL , `keywords` VARCHAR(15000) NOT NULL , `visits` INT NOT NULL DEFAULT '0' , PRIMARY KEY (`dataid`))")
cur.execute("CREATE TABLE `tbl_user` (`userid` int(11) NOT NULL AUTO_INCREMENT,`username` varchar(60) NOT NULL,`password` varchar(60) NOT NULL,`email` varchar(120) NOT NULL,`searchmode` int(11) NOT NULL DEFAULT '0',`isadmin` tinyint(1) NOT NULL DEFAULT '0',PRIMARY KEY (`userid`))")
cur.execute("CREATE TABLE `tbl_filter` (`ruleid` int(11) NOT NULL AUTO_INCREMENT,`userid` int(11) NOT NULL,`filter` char(1) NOT NULL,PRIMARY KEY (`ruleid`),KEY `userid` (`userid`),CONSTRAINT `tbl_filter_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `tbl_user` (`userid`))")

#place entries into data table
datafile = open('dataset.csv', 'r', encoding='utf-8')
dataset = csv.reader(datafile)

for row in dataset:
	cur.execute('INSERT INTO tbl_data(title, url, keywords) VALUES (%s, %s, %s)', (row[0], row[1], row[2]))

#insert sample entries, for now
cur.execute("INSERT INTO tbl_user(username, password, email) VALUES (%s, %s, %s)", ("testuser", "test", "testemail@test.com"))
cur.execute("INSERT INTO tbl_filter(userid, filter) VALUES (%s, %s)", ("1", "@"))
cur.execute("INSERT INTO tbl_filter(userid, filter) VALUES (%s, %s)", ("1", "\""))

conn.commit()
cur.close()