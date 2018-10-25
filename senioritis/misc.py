from flask import render_template
from senioritis import app, dbthing


@app.route('/user/<username>')
def user_profile(username):
    return 'User %s' % username


@app.route('/hello/<name>')
def hello(name=None):
    return render_template('greeter.html', name=name)


@app.route('/peeps')
@dbthing
def peeps(c):
    c.execute("""SELECT * FROM peeps""")
    a = [i[0] for i in c]
    print(a)
    return render_template('imagegrid.html', ress=a)