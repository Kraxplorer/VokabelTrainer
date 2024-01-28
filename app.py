import random
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import webview

app = Flask(__name__)
app.secret_key = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vokabeln.db"
db = SQLAlchemy(app)
window = webview.create_window(
    "Vokabeltrainer",
    app,  # type: ignore
)


class Vokabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    franzoesisch = db.Column(db.String(100))
    deutsch = db.Column(db.String(100))


@app.route("/")
def index():
    vokabeln = Vokabel.query.all()
    if not vokabeln:
        return render_template("noVokabeln.html")
    vokabel_id = random.choice([v.id for v in vokabeln])
    vokabel = Vokabel.query.get(vokabel_id)
    return render_template("index.html", vokabel=vokabel)


@app.route("/check", methods=["POST"])
def check():
    vokabel_id = request.form["vokabel_id"]
    eingabe = request.form["eingabe"]
    vokabel = Vokabel.query.get(vokabel_id)
    if eingabe.lower() is None or eingabe.lower() == "":
        return render_template("index.html", vokabel=vokabel, wrong=True)
    if eingabe.lower() in vokabel.deutsch.lower():  # type: ignore
        return redirect(url_for("next", current_id=vokabel_id))
    else:
        return render_template("index.html", vokabel=vokabel, wrong=True)


@app.route("/next/<int:current_id>")
def next(current_id):
    vokabeln = Vokabel.query.all()
    if not vokabeln:
        return "Es sind keine Vokabeln vorhanden."
    available_vokabel_ids = [v.id for v in vokabeln if v.id != current_id]
    if not available_vokabel_ids:
        return redirect(url_for("index"))
    next_id = random.choice(available_vokabel_ids)
    next_vokabel = Vokabel.query.get(next_id)
    return render_template("index.html", vokabel=next_vokabel)


@app.route("/edit")
def edit():
    vokabeln = Vokabel.query.all()
    return render_template("edit.html", vokabeln=vokabeln)


@app.route("/add", methods=["POST"])
def add():
    franzoesisch = request.form["franzoesisch"]
    deutsch = request.form["deutsch"]
    vokabel = Vokabel(franzoesisch=franzoesisch, deutsch=deutsch)  # type: ignore
    db.session.add(vokabel)
    db.session.commit()
    return redirect(url_for("edit"))


@app.route("/delete/<int:vokabel_id>")
def delete(vokabel_id):
    vokabel = Vokabel.query.get(vokabel_id)
    db.session.delete(vokabel)
    db.session.commit()
    return redirect(url_for("edit"))


@app.route("/save", methods=["POST"])
def save():
    neu_franzoesisch = request.form.get("neu_franzoesisch")
    neu_deutsch = request.form.get("neu_deutsch")

    if neu_franzoesisch and neu_deutsch:
        neue_vokabel = Vokabel(franzoesisch=neu_franzoesisch, deutsch=neu_deutsch)  # type: ignore
        db.session.add(neue_vokabel)
        db.session.commit()

    return redirect("/edit")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    webview.start(debug=True)
