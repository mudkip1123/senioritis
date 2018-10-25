import urllib.parse
from functools import wraps
import os
from flask import Flask
from flask.ext.basicauth import BasicAuth
import psycopg2
import tinys3


app = Flask(__name__)
# app.debug = True
app.config['BASIC_AUTH_USERNAME'] = os.environ["ADMIN_USERNAME"]
app.config['BASIC_AUTH_PASSWORD'] = os.environ["ADMIN_PASSWORD"]
# app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
app.secret_key = "hunter2"

scon = tinys3.Connection(os.environ["AWS_ACCESS_KEY_ID"], os.environ["AWS_SECRET_ACCESS_KEY"], tls=True)


def dbthing(f):
    @wraps(f)
    def inner(*args, **kwargs):
        con = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cee = con.cursor()
        res = f(cee, *args, **kwargs)
        con.commit()
        con.close()
        return res
    return inner


@dbthing
def getvalidtags(c):
    c.execute("SELECT tagname FROM all_tags")
    return [i[0] for i in c]


@app.after_request
def gnu_terry_pratchett(resp):
    resp.headers.add("X-Clacks-Overhead", "GNU Terry Pratchett")
    return resp

import senioritis.main
import senioritis.admin
import senioritis.misc
# import senioritis.prerelease

if __name__ == "__main__":
    app.run(debug=True)
