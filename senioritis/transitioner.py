import urllib.parse
import sqlite3

import os
import psycopg2
import tinys3


url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
scon = tinys3.Connection(os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"], tls=True)
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
heroku_cursor = conn.cursor()

conn2 = sqlite3.connect("PicDB.db")
local_cursor = conn2.cursor()

# As the file table remotely is defined as a SERIAL, the IDs will be filled in automatically,
# we just need to maintain the order
alllocalfiles = local_cursor.execute("SELECT ID, name FROM files").fetchall()
alllocalfiles.sort()
sortedfilenames = [i[1] for i in alllocalfiles]
# sys.exit()

# Compacts the numbering of each file to start at 1 with no gaps, retaining the relative sorted positio
# The tag list however can have multiple lines sharing an ID
alllocaltags = local_cursor.execute("SELECT * FROM tags").fetchall()
alllocaltags.sort()
#
numberinglist = [0]  # Starts with 0 bacause can't max() empty list
prev = 0
for i in alllocaltags:
    if i[0] > prev:
        numberinglist.append(max(numberinglist) + 1)
        prev = i[0]
    elif i[0] == prev:
        numberinglist.append(max(numberinglist))
numberinglist.pop(0)  # Remove leading 0
justtagnames = [i[1] for i in alllocaltags]
tagnumbersreset = list(zip(numberinglist, justtagnames))

# Now we upload this to the remote db

for i in sortedfilenames:
    heroku_cursor.execute("INSERT INTO files (name) VALUES (%s)", (i,))
for i in tagnumbersreset:
    heroku_cursor.execute("INSERT INTO tags (file_id, name) VALUES (%s, %s)", (i[0], i[1]))

conn.commit()
conn.close()
conn2.close()