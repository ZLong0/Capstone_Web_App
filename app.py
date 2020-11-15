#!/usr/bin/python3  
from flask import Flask, render_template, jsonify, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = "capstonefall2020"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atas.sqlite3'
db = SQLAlchemy(app)


#DATABASE MODELS ARE FOLLOWED DIRECTLY BY THE METHODS THAT CORRESPOND TO THOSE OPJECTS
#IF TIME ALLOWS - MOVE MODELS TO THEIR OWN MODELS.PY FILE


#USERS CLASS
class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(256))
    password = db.Column("password", db.String(256))
    is_Admin = db.Column("admin", db.Boolean(0))
    is_active = db.Column(db.Boolean(0))

    def __init__(self, username, password, is_Admin, is_active):
        self.username = username
        self.password = password
        self.is_Admin = is_Admin
        self.is_active = is_active


#INSTRUCTORS CLASS
class Instructor(db.Model):
    inst_id = db.Column("id", db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    
    def __init__(self, fname, lname):
        self.fname=fname
        self.lname = lname


@app.route('/instructors', methods=['GET'])
def get_all_instructors():
    instructors = Instructor.query.all()
    results = []

    for instructor in instructors:
        instructor_data = {}
        instructor_data['instructor_id'] = instructor.inst_id
        instructor_data['first_name'] = instructor.fname
        instructor_data['last_name'] = instructor.lname
        results.append(instructor_data)
    
    return jsonify(results)


#STUDENT CLASS
class Student(db.Model):
    student_id = db.Column("id",db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, fname, lname):
        self.fname = fname
        self.lname = lname


@app.route('/students', methods=['GET'])
def get_all_students():
    students = Student.query.all()
    results = []
    for student in students:
        student_data = {}
        student_data['student_id'] = student.student_id
        student_data['first_name'] = student.fname
        student_data['last name'] = student.lname
        results.append(student_data)
    
    return jsonify(results)


#COURSE CLASS
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


@app.route('/courses', methods =["GET"])
def get_all_courses():
    courses = Course.query.all()
    results = []
    
    for course in courses:
        course_info = {}
        course_info['course_name'] = course.course_name
        course_info['term'] = course.term
        course_info['year'] = course.year
        course_info['course_department'] = course.department
        course_info['course_number'] = course.course_number
        course_info['section'] = course.section
        course_info['instructor_id'] = course.instructor
        results.append(course_info)

    return jsonify(results)


#gets all courses for specific instructor id
@app.route('/courses/<instructor_id>', methods=['GET'])
def get_instructor_courses(instructor_id):
    courses = Course.query.filter_by(instructor = instructor_id).all()
    results = []
    
    if not courses:
        return {"No courses assigned to this instructor"}
    

    for course in courses:
        course_info = {}
        course_info['course_name'] = course.course_name
        course_info['term'] = course.term
        course_info['year'] = course.year
        course_info['course_department'] = course.department
        course_info['course_number'] = course.course_number
        course_info['section'] = course.section
        results.append(course_info)

    return jsonify(results)


#OUTCOMES CLASS
class Outcomes(db.Model):
    so_id = db.Column("so_id",db.Integer, primary_key=True)
    so_name = db.Column(db.String(4))
    so_desc = db.Column(db.String(1000))

    def __init__(self, so_name, so_desc):
        self.so_name = so_name
        self.so_desc = so_desc


@app.route("/outcomes", methods=["GET"])
def get_all_outcomes():
    outcomes = Outcomes.query.all()

    results = []

    for outcome in outcomes:
        outcome_data = {}
        outcome_data['so_name'] = outcome.so_name
        outcome_data['so_desc'] = outcome.so_desc
        results.append(outcome_data)
    
    return jsonify(results)


#ASSIGNMENTS (SWP) CLASS
class Assignments(db.Model):
    swp_id = db.Column("swp_id", db.Integer,primary_key=True)
    course_id  = db.Column(db.Integer, db.ForeignKey('course.id'))
    swp_name = db.Column(db.String(100))

    def __init__(self, course_id, swp_name):
        self.course_id = course_id
        self.swp_name = swp_name


@app.route('/swp', methods=["GET"])
def get_all_swp():
    swps = Assignments.query.all()

    results = []

    for swp in swps:
        swp_data = {}
        swp_data['swp_id'] = swp.swp_id
        swp_data['swp_name'] = swp.swp_name
        swp_data['course_id'] = swp.course_id
        results.append(swp_data)
    
    return jsonify(results)


#ATTEMPTS CLASS
class Attempts(db.Model):
    attempt_id = db.Column("id", db.Integer, primary_key=True)
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    so_id = db.Column(db.Integer, db.ForeignKey('outcomes.so_id'))

    def __init__(self, swp_id, so_id):
        self.swp_id = swp_id
        self.so_id = so_id


@app.route('/attempts', methods=["GET"])
def get_all_attempts():
    attempts = Attempts.query.all()

    results = []

    for attempt in attempts:
        attempt_data = {}
        attempt_data['attempt_id'] = attempt.attempt_id
        attempt_data['swp'] = attempt.swp_id
        attempt_data['so'] = attempt.so_id
        results.append(attempt_data)
    
    return jsonify(results)


#ENROLLED CLASS
class Enrolled(db.Model):
    enrolled_id = db.Column(db.Integer, primary_key=True)
    student_id= db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id


@app.route('/enrolled', methods=['GET'])
def get_all_enrolled():
    enrolled = Enrolled.query.all()
    results = []

    for enroll in enrolled:
        enrollment_data = {}
        enrollment_data['enrolled-id'] = enroll.enrolled_id
        enrollment_data['student-id'] = enroll.student_id
        enrollment_data['course_id'] = enroll.course_id
        results.append(enrollment_data)

    return jsonify(results)


#RESULTS CLASS
class Results(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'))

    def __init__(self, student_id, attempt_id):
        self.student_id = student_id
        self.attempt_id = attempt_id


app.route('/results', methods=['GET'])
def get_all_results():
    results = Results.query.all()
    output = []

    for result in results:
        result_data = {}
        result_data['result id'] = result._id
        results_data['student id'] = result.student_id
        result_data['attempt id'] = results.attempt_id
        output.append(result_data)

    return jsonify(output)


#BASE ROUTES (INDEX/HOME/REGISTER) -- THIS MAY BE MOVED LATER
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("login.html")  # this should be the name of your html file


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print("username=" + username)
        print("password=" + password)
    return redirect("/home")


@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("home.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")


@app.route("/send_reg", methods=["POST", "GET"])
def register_user():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        employee_id = request.form["employee_id"]
        access_level = request.form["access_level"]
        question_1 = request.form["question_1"]
        answer_1 = request.form["answer_1"]
        question_2 = request.form["question_2"]
        answer_2 = request.form["answer_2"]
        question_3 = request.form["question_3"]
        answer_3 = request.form["answer_3"]

        print("username=" + username)
        print("email=" + email)
        print("password=" + password)
        print("employee_id=" + employee_id)
        print("access_level=" + access_level)
        print("question_1=" + question_1)
        print("answer_1=" + answer_1)
        print("question_2=" + question_2)
        print("answer_2=" + answer_2)
        print("question_3=" + question_3)
        print("answer_3=" + answer_3)
    return redirect("/")


@app.route("/logout")
def logout():
    return redirect("/")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

