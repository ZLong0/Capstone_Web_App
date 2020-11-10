#!/usr/bin/python3  
from flask import Flask, render_template, json, request
#from flask.ext.mysql import MySQL

#mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = '*'
#app.config['MYSQL_DATABASE_PASSWORD'] = '*'
#app.config['MYSQL_DATABASE_DB'] = '*'
#app.config['MYSQL_DATABASE_HOST'] = '*'
#mysql.init_app(app)


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("login.html")  # this should be the name of your html file


@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")


@app.route("/logout")
def logout():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True)
