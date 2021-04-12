#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, url_for, redirect, render_template, flash, request, session
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy


# In[2]:


app = Flask(__name__)
app.secret_key = "pisnai"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column("name", db.String(100), nullable = False)
    classroom = db.Column("classroom", db.String(100), nullable = False)
    temperature = db.Column("temperature", db.String(100))
    date_time = db.Column(db.DateTime, default = datetime.utcnow)

    def __init__(self, name, classroom, temperature):
        self.name = name
        self.classroom = classroom
        self.temperature = temperature

@app.route("/")
def start_fun():
    return redirect(url_for("home_fun"))

@app.route("/home")
def home_fun():
    return render_template("home.html", content = "請從上方導覽列登錄")

@app.route("/sign_in", methods=["POST", "GET"])
def sign_in_fun():
    if request.method == "POST":
        session.permanet = True
        session.permanent_session_lifetime = timedelta(hours = 1)
        session["name"] = request.form["name"]
        session["classroom"] = request.form["classroom"]
        flash("登錄成功！！")
        return redirect(url_for("temperature_fun"))
    else:
        if "name" in session:
            return redirect(url_for("temperature_fun"))
        return render_template("sign_in.html")

@app.route("/temperature", methods=["POST", "GET"])
def temperature_fun():
    if request.method == "POST":
        session["temperature"] = request.form["choice"]
        temp = data(name=session["name"], classroom=session["classroom"], temperature=session["temperature"])
        db.session.add(temp)
        db.session.commit()
        return render_template("home.html", content = "填寫完畢，可以至資料確認填寫正確與否")
    else:
        name = session["name"]
        classroom = session["classroom"]
        return render_template("temperature.html", name = name, classroom = classroom)

@app.route("/sign_out")
def sign_out_fun():
    name = session["name"]
    session.clear()
    flash("登出成功！")
    return render_template("home.html", content = f"感謝 {name} 的填答，謝謝合作")

@app.route("/view")
def view_fun():
    return render_template("view.html", info = data.query.all())

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)





