from flask import render_template, request
from senioritis import app, c


@app.route('/entry')
def entry():
    # Uses Upload, Textbox, Checkbox
    return render_template('inputtypetesting.html')


@app.route("/textbox", methods=["POST"])
def textbox():
    n = request.form["txt"]
    c.execute("SELECT file_id FROM tags WHERE name=%s", (n,))
    ids = [i[0] for i in c]
    if len(ids) != 0:
        c.execute("SELECT name from files where ID IN %s", (tuple(ids[:10]),))
        names = [i[0] for i in c]
        return render_template('imagegrid.html', ress=names)
    else:
        return "No results found. Check the spelling of your tag and try again."


@app.route("/checkbox", methods=["POST"])
def checkbox():
    checked = request.form.getlist("include")
    c.execute("SELECT file_id FROM tags WHERE name IN %s GROUP BY file_id HAVING COUNT(*) = %s",
              (tuple([str(i) for i in checked]), len(checked)))
    ids = [i[0] for i in c]
    if len(ids) != 0:
        c.execute("SELECT name from files where ID IN %s", (tuple(ids),))
        names = [i[0] for i in c]
        return render_template('imagegrid.html', ress=names)
    else:
        return "No Results"