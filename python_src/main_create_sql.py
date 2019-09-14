import csv
import sqlite3
import os


import sys

print(sys.version)
# print("Hello World!")

database_name = "../sql/first.sqlite3"

os.remove(database_name)

con = sqlite3.connect(database_name)
# con = sqlite3.connect("local.sqlite3")
cur = con.cursor()
# cur.execute("CREATE TABLE t (col1, col2);")  # use your column names here
cur.execute('''CREATE TABLE CLIENTS
             ([generated_id] INTEGER PRIMARY KEY,[col1] text, [col2] text)''')
#              ([generated_id] INTEGER PRIMARY KEY,[col1] text, [col2] integer, [Date] date)''')

with open('../raw_data/first.csv', 'rt') as fin:  # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin)  # comma is default delimiter
    to_db = [(i['col1'], i['col2']) for i in dr]

cur.executemany("INSERT INTO CLIENTS (col1, col2) VALUES (?, ?);", to_db)
con.commit()
con.close()
