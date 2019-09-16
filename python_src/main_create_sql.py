import csv
import sqlite3
import os

import sys

print(sys.version)

database_name = "../sql/first.sqlite3"

os.remove(database_name)

con = sqlite3.connect(database_name)
cur = con.cursor()
columns = ('''Hanzi''', '''English''')
cur.execute('''CREATE TABLE Translations
             (
                 [generated_id] INTEGER PRIMARY KEY,
                 [%s] text, 
                 [%s] text
             )
             ''' % columns)

with open('../raw_data/first.csv', 'rt') as fin:  # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin)  # comma is default delimiter
    to_db = [
                (
                    i[('%s' % columns[0])],
                    i[('%s' % columns[1])],
                )
            for i in dr]

cur.executemany("INSERT INTO Translations (%s, %s) VALUES (?, ?);" % columns, to_db)
con.commit()
con.close()
