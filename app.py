#!/usr/bin/python3  
from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = '*'
app.config['MYSQL_DATABASE_PASSWORD'] = '*'
app.config['MYSQL_DATABASE_DB'] = '*'
app.config['MYSQL_DATABASE_HOST'] = '*'
mysql.init_app(app)


@app.route('/')
def index():
    return render_template("index.html")  # this should be the name of your html file

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')
