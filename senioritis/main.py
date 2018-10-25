from flask import render_template, request, redirect
from senioritis import app, basic_auth, getvalidtags, scon, dbthing


@app.route('/')
def index():
    return 'k.'


@app.route("/home")
def home():
    return render_template('homescreen.html', tags=getvalidtags())


@app.route("/multi", methods=["POST"])
@dbthing
def multi(c):
    includes = request.form.getlist("includes")
    excludes = request.form.getlist("excludes")
    if len(includes) > 0:
        c.execute("SELECT file_id FROM tags WHERE name IN %s GROUP BY file_id HAVING COUNT(*) = %s",
                  (tuple([str(i) for i in includes]), len(includes)))
        included_ids = []
        for i in c:
            if i[0] not in included_ids:
                included_ids.append(i[0])
        # included_ids = set(i[0] for i in c)
    else:
        return "You must select at least one tag to include."
    if len(excludes) > 0:
        c.execute("SELECT file_id FROM tags WHERE name IN %s", (tuple([str(i) for i in excludes]),))
        excluded_ids = set(i[0] for i in c)
        result_set = included_ids.difference(excluded_ids)
    else:
        result_set = included_ids
    if len(result_set) > 0:
        c.execute("SELECT name from files where ID IN %s", (tuple(result_set),))
        names = [i[0] for i in c]
        if basic_auth.authenticate():
            return render_template('taggableimagegrid.html', ress=names, ids=list(sorted(result_set)))
        else:
            return render_template('imagegrid.html', ress=names, ids=list(sorted(result_set)))
    else:
        return "No Results"


@app.route("/uploader")
# @basic_auth.required
def uploader():
    return render_template("uploadform.html")


@app.route('/upload', methods=["POST"])
@dbthing
# @basic_auth.required
def upload(c):
    # name = request.form["Name"]
    files = request.files.getlist("file")
    if files:
        for f in files:
            scon.upload(f.filename, f.stream, 'kyle-picture-bucket/Pictures')
            c.execute("DELETE FROM files WHERE name=%s", (f.filename,))
            c.execute("INSERT INTO files (name) VALUES (%s)", (f.filename,))
            # conn.commit()
    return redirect("/uploader")


@app.route('/uploadbot', methods=["POST"])
@dbthing
# @basic_auth.required
def uploadbot(c):
    files = request.files["file"]
    if files:
        scon.upload(files.filename, files.stream, 'kyle-picture-bucket/Pictures')
        c.execute("SELECT * FROM files where name=%s", (files.filename,))
        if not c.fetchone():
            c.execute("INSERT INTO files (name) VALUES (%s)", (files.filename,))
        # c.execute("DELETE FROM files WHERE name=%s", (files.filename,))
        # print "delete line was successful"
        # c.execute("INSERT INTO files (name) VALUES (%s)", (files.filename,))
        # print "Executed the two SQL commands (I think this is where everything breaks)"
        # conn.commit()
        # print "Changes committed, we're probably fine now."
        return "https://s3.amazonaws.com/kyle-picture-bucket/Pictures/" + files.filename.replace(" ", "%20")
    else:
        print("Turns out I didn't, what a shame, returning a sadface instead of a url.")
        return "sadface"


@app.route("/random")
@dbthing
def randimage(c):
    # c.execute("""SELECT files.name FROM files WHERE files.id IN (
    #               SELECT file_id FROM tags WHERE name <> 'pony' ORDER BY random() LIMIT 1
    #              ) LIMIT 1;""")
    c.execute("""SELECT files.name FROM files ORDER BY random() LIMIT 1;""")
    image_url = "https://s3.amazonaws.com/kyle-picture-bucket/Pictures/" + c.fetchone()[0].replace(" ", "+")
    return render_template("randomimage.html", imagelink=image_url)


@app.route("/recent/")
@app.route("/recent/<int:number>")
@dbthing
def recent(c, number=15):
    c.execute("SELECT name FROM files")
    names = [i[0] for i in c][-1 * number:]
    return render_template('imagegrid.html', ress=names)
