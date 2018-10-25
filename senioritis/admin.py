from flask import request, render_template, redirect
from senioritis import app, basic_auth, getvalidtags, dbthing


@app.route("/admin")
@basic_auth.required
def admin():
    return 'k.'


@app.route("/admin/thelonelyandtagless/")
@app.route("/admin/thelonelyandtagless/<int:num>")
@basic_auth.required
@dbthing
def untagged(c, num=15):
    c.execute("SELECT ID, name FROM files where ID NOT IN (SELECT file_id from tags)")
    # c.execute("SELECT ID, name FROM files")
    res = [i for i in c]
    names = [i[1] for i in res]
    ids = [i[0] for i in res]
    return render_template('taggableimagegrid.html', ress=names[:num], ids=ids)


@app.route("/admin/tagimage/<int:image_id>")
@basic_auth.required
@dbthing
def tagimage(c, image_id):
    c.execute("SELECT name FROM files WHERE ID=%s", (image_id,))
    image_url = ["https://s3.amazonaws.com/kyle-picture-bucket/Pictures/" + i[0].replace(" ", "+") for i in c][0]
    c.execute("SELECT name FROM tags WHERE file_id=%s", (image_id,))
    selected = [i[0] for i in c]
    return render_template('singleimage.html', img_url=image_url, selected=selected, ID=image_id, tags=getvalidtags())


@app.route("/admin/tagsubmit/<image_id>", methods=["POST"])
@basic_auth.required
@dbthing
def tagsubmit(c, image_id):
    newtags = request.form.getlist("tags")
    c.execute("DELETE FROM tags WHERE file_id=%s", (image_id,))
    c.executemany("INSERT INTO tags VALUES (%s, %s)", list(zip([image_id] * len(newtags), newtags)))
    # conn.commit()
    return redirect("/admin/tagimage/" + image_id)


@app.route("/admin/deleteimage/<int:image_id>")
@basic_auth.required
@dbthing
def deleteimage(c, image_id):
    c.execute("DELETE FROM files WHERE ID=%s", (image_id,))
    return "Okay? Okay."


@app.route("/admin/tageditor")
@basic_auth.required
def tageditor():
    return render_template("tageditor.html")


@app.route("/admin/addnewtag", methods=["POST"])
@basic_auth.required
@dbthing
def addnewtag(c):
    tagname = request.form["tagname"]
    c.execute("INSERT INTO all_tags VALUES (%s)", (tagname,))
    # conn.commit()
    return "You got it, boss"


@app.route("/admin/delbyfilename/<filename>")
@basic_auth.required
@dbthing
def delbyfilename(c, filename):
    a = c.execute("DELETE FROM files WHERE name=(%s)", (filename,))
    return "Kay" + a
