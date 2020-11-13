#!/usr/bin/python3  
from flask import Flask, render_template, json, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "capstonefall2020"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atas.sqlite3'
db = SQLAlchemy(app)


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(256))
    password = db.Column("password", db.String(256))
    is_Admin = db.Column("admin", db.Boolean(0))
    is_active = db.Column(db.Boolean(0))

    def __init__(self, username, password, is_admin, is_active):
        self.username = username
        self.password = password
        self.is_Admin = is_admin
        self.is_active = is_active


class Instructor(db.Model):
    inst_id = db.Column("id", db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    
    def __init__(self, fname, lname):
        self.fname=fname
        self.lname = lname

 
class Student(db.Model):
    student_id = db.Column("id",db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, fname, lname):
        self.fname = fname
        self.lname = lname


class Course(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100))
    term = db.Column(db.String(11))
    year = db.Column(db.String(4))
    department = db.Column(db.String(5))
    course_number = db.Column(db.String(10))
    section = db.Column(db.String(5))
    instructor = db.Column(db.Integer, db.ForeignKey('instructor.id'))

    def __init__(self, course_name, term, year, deparment, course_number, section, instructor):
        self.course_name = course_name
        self.term = term
        self.year = year
        self.department = deparment
        self.course_number = course_number
        self.section = section
        self.instructor = instructor


class Outcomes(db.Model):
    so_id = db.Column("so_id",db.Integer, primary_key=True)
    so_name = db.Column(db.String(4))
    so_desc = db.Column(db.String(1000))

    def __init__(self, so_name, so_desc):
        self.so_name = so_name
        self.so_desc = so_desc


class Assignments(db.Model):
    swp_id = db.Column("swp_id", db.Integer,primary_key=True)
    course_id  = db.Column(db.Integer, db.ForeignKey('course.id'))
    swp_name = db.Column(db.String(100))

    def __init__(self, course_id, swp_name):
        self.course_id = course_id
        self.swp_name = swp_name



class Attempts(db.Model):
    attempt_id = db.Column("id", db.Integer, primary_key=True)
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    so_id = db.Column(db.Integer, db.ForeignKey('outcomes.so_id'))



    def __init__(self, swp_id, so_id):
        self.swp_id = swp_id
        self.so_id = so_id


class Enrolled(db.Model):
    enrolled_id = db.Column(db.Integer, primary_key=True)
    student_id= db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id


class Results(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'))

    def __init__(self, student_id, attempt_id):
        self.student_id = student_id
        self.attempt_id = attempt_id


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



@app.route("/outcomes")
def outcomes():
    return {'so_name': 'SO1', 'so_desc': 'this is a test'}


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

