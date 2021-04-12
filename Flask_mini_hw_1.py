#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, url_for, redirect, render_template, flash, request, session
from datetime import timedelta, datetime
import pandas as pd
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from bokeh.embed import components
from Project_AMT import diff, stationary_test, ts_plot, acf_plot, pacf_plot, fitting_ARIMAX_model, diagnostics

# In[2]:


app = Flask(__name__)
app.secret_key = "pisnai"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    model = db.Column("model", db.String(100), nullable = False)
    data = db.Column("data", db.String(100), nullable = False)
    diff = db.Column("diff", db.String(100), nullable = False)
    log = db.Column("log", db.String(100), nullable = False)

    def __init__(self, model, data, diff, log):
        self.model = model
        self.data = data
        self.diff = diff
        self.log = log

@app.route("/")
def start_fun():
    return redirect(url_for("home_fun"))

@app.route("/home")
def home_fun():
    return render_template("home.html", content = "Choose the data from the BEGINNING buttom")

@app.route("/beginning", methods=["POST", "GET"])
def beginning():
    if request.method == "POST":
        session.permanet = True
        session.permanent_session_lifetime = timedelta(hours = 1)
        session["model"] = request.form["model"]
        session["data"] = request.form["data"]
        session["diff"] = request.form["diff"]
        session["log"] = request.form["log"]
        temp = data(model=session["model"], data=session["data"], diff=session["diff"], log=session["log"])
        db.session.add(temp)
        db.session.commit()
        if request.form["model"] == "1":
            return redirect(url_for("specification"))
        else:
            return redirect(url_for("diagnostics_1"))
    else:
    #     if "name" in session:
    #         return redirect(url_for("home_fun"))
        return render_template("beginning.html")


@app.route("/spec")
def specification():
    df = pd.read_csv('data.csv')[['date', 'australia',"indonesia"]]
    date_ = pd.date_range(start="2009-11-01",end="2019-10-31",freq='MS').to_numpy()
    if session["data"] == "1":
        if session["log"] == "1":
            if  session["diff"] == "1":
                ts_array = diff(np.log((df.australia).to_numpy()))
            else:
                ts_array = np.log((df.australia).to_numpy())
        else:
            if  session["diff"] == "1":
                ts_array = diff((df.australia).to_numpy())
            else:
                ts_array = (df.australia).to_numpy()

    else:

        if session["log"] == "1":
            if  session["diff"] == "1":
                ts_array = diff(np.log((df.indonesia).to_numpy()))
            else:
                ts_array = np.log((df.indonesia).to_numpy())
        else:
            if  session["diff"] == "1":
                ts_array = diff((df.indonesia).to_numpy())
            else:
                ts_array = (df.indonesia).to_numpy()
    if session["diff"] == "1":
        lag_ = 1
    else:
        lag_ = 0

    sta_test1, sta_test2= stationary_test(ts_array)
    p1 = ts_plot(date_[lag_:], ts_array)
    acf = acf_plot(date_[lag_:], ts_array, title = "ACF plot")
    pacf = pacf_plot(date_[lag_:], ts_array, title = "PACF plot")

    script, div = components(p1)
    script2, div2 = components(acf)
    script3, div3 = components(pacf)

    return render_template('specification.html',sta_test1 = sta_test1, sta_test2 = sta_test2
        , script = script,div = div, script2 = script2, div2 = div2, script3 = script3, div3 = div3)


@app.route("/diag1", methods=["POST", "GET"])
def diagnostics_1():
    if request.method == "POST":
        session.permanet = True
        session.permanent_session_lifetime = timedelta(hours = 1)
        session["AR"] = request.form["AR"]
        session["MA"] = request.form["MA"]
        session["exog"] = request.form["exog"]
        return redirect(url_for("diagnostics_2"))

    else:
        return render_template("diagnostics_1.html")

@app.route("/diag2")
def diagnostics_2():
    df = pd.read_csv('data.csv')[['date', 'australia',"indonesia"]]
    date_ = pd.date_range(start="2009-11-01",end="2019-10-31",freq='MS').to_numpy()
    if session["data"] == "1":
        if session["log"] == "1":
            ts_array = np.log((df.australia).to_numpy())
        else:
            ts_array = (df.australia).to_numpy()

    else:

        if session["log"] == "1":
            ts_array = np.log((df.indonesia).to_numpy())
        else:
            ts_array = (df.indonesia).to_numpy()

    if session["diff"] == "1":
        lag_ = 1
    else:
        lag_ = 0

    exog_ = np.zeros(len(ts_array))
    if not (session["exog"] == ""):
        exog_[int(session["exog"])] = 1

    residuals, mod ,summary = fitting_ARIMAX_model( ts_array, exog_, int(session["AR"]), int(session["MA"]), lag_)
    p, nor_t = diagnostics(residuals, date_, lag_)
    script, div = components(p)
    est_table = pd.DataFrame(summary.tables[1].data[1:], columns = summary.tables[1].data[0])
    AIC = summary.tables[0].data[2][3]

    return render_template('diagnostics_2.html',ts_array = ts_array ,nor_t = nor_t, AIC = AIC
        , est_table = [est_table.to_html(classes='data', header="true")] , script = script, div = div)


if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)





