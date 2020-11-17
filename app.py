#!/usr/bin/python3  
from flask import Flask, render_template, jsonify, request, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = "capstonefall2020"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atas.sqlite3'
db = SQLAlchemy(app)


# DATABASE MODELS ARE FOLLOWED DIRECTLY BY THE METHODS THAT CORRESPOND TO THOSE OPJECTS
# IF TIME ALLOWS - MOVE MODELS TO THEIR OWN MODELS.PY FILE

# USERS CLASS
class Users(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=False)
    fname = db.Column("first_name", db.String(20))
    lname = db.Column("last_name", db.String(50))
    email = db.Column("email", db.String(50), unique=True)
    password = db.Column("password", db.String(256))
    account_type = db.Column("account_type", db.String(20))
    sec_question = db.Column("question", db.Integer)
    answer = db.Column("answer", db.String(100))
    

    def __init__(self, id, email, password, account_type, fname, lname, sec_question, answer):
        self.email = email
        self.password = password
        self.account_type = account_type
        self.fname = fname
        self.lname = lname
        self.id = id
        self.sec_question = sec_question
        self.answer = answer


# this checks credentials before login
@app.route("/login", methods=["POST", "GET"])
def login():
    error = None
    message = None
    username_attempt = ''
    password_attempt = ''

    if request.method == "POST":
        username_attempt = request.form["email"]
        password_attempt = request.form["password"]

        user = Users.query.filter_by(email=username_attempt).first()
        if not user:
            error = 'Invalid Username/Password!  Please try again.'
            return render_template('login.html', error=error)
        elif check_password_hash(pwhash=user.password, password=password_attempt) and Users.query.filter_by(account_type='admin'):
            return render_template('home.html')
        elif check_password_hash(pwhash=user.password, password=password_attempt):
            return render_template('home.html')
        elif password_attempt == user.password and Users.query.filter_by(account_type='admin'):
            # used to direct to admin home page
            return render_template('home.html')
        elif password_attempt == user.password:
            return render_template('home.html')

    error = 'Invalid Username/Password!  Please try again.'
    return render_template('login.html', error=error)


# this checks db for existing username before returning
@app.route("/register", methods=["POST", "GET"])
def register_user():
    error = None
    if request.method == "POST":
        add_id = request.form['employee_id']
        email = request.form["email"]
        password = request.form["password"]
        employee_id = request.form["employee_id"]
        account_type = request.form["access_level"]
        question_1 = request.form["question_1"]
        answer_1 = request.form["answer_1"]
        #first_name = request.form['first']
        #last_name = request.form['last']

        # output for debugging only
        print("username=" + email)
        print("password=" + password)
        print("employee_id=" + employee_id)
        print("access_level=" + account_type)
        print("question_1=" + question_1)
        print("answer_1=" + answer_1)

        user = Users.query.filter_by(id=add_id).first()

        if user:
            error = "Employee ID is already registered"
            return render_template('register.html', error=error)
                # will remove auto commit later. using for testing currently
        else:
            if account_type == 'admin':
                    # set admin when sent
                new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                new_user = Users(email=email, password=new_password, account_type='admin')
                db.session.add(new_user)
                db.session.commit()
                message = 'Registration sent'
                return render_template('login.html')
            else:
                    # set admin to 0
                new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                new_user = Users(id=add_id, fname='caro', lname='azzone', sec_question=question_1, answer = answer_1, email=email, password=new_password, account_type='instructor')
                db.session.add(new_user)
                db.session.commit()
                message = 'Registration sent'
                return render_template('login.html', message=message)
    else:
        return render_template('register.html')


# INSTRUCTORS CLASS
class Instructor(db.Model):
    inst_id = db.Column("id", db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, fname, lname):
        self.fname = fname
        self.lname = lname


@app.route('/instructors', methods=['GET', 'POST'])
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


@app.route('/instructors', methods=['POST'])
def instructors():
    if request.method=='POST':
        #TODO: UPDATE THIS TO TAKE IN VALUE FROM FORM
        id = 1
        #check for existing instructor id first
        instructor = Instructor.query.filter_by(id=id).first()
        if instructor:
            return 'This employee ID is already registered'
        else:
            ""
    return ""


# STUDENT CLASS
class Student(db.Model):
    student_id = db.Column("id", db.Integer, primary_key=True)
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


#TODO  -- complete endpoint
app.route('/students', methods=['POST'])
def students():
    return ""


#TODO -- complete put students endpoint
app.route('/students', methods=['PUT'])
def students():
    return ""


#TODO -- complete delete students
app.route('/students/<student_id>', methods=['DELETE'])
def students(student_id):
    student = Student.query.filter_by(student_id = student_id).first()
    db.session.delete(student)
    db.commit()

    return "Deleted " + student.id
   

# COURSE CLASS
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


@app.route('/courses', methods=["GET"])
def get_all_courses():
    all_courses = Course.query.all()
    results = []

    for course in all_courses:
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


# gets all courses for specific instructor id
@app.route('/courses/<instructor_id>', methods=['GET'])
def get_instructor_courses(instructor_id):
    courses = Course.query.filter_by(instructor=instructor_id).all()
    results = []

    if request.method == "GET":
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

        return render_template("home.html", courses=results)

    else:
        return render_template("home.html")


#TODO  -- complete endpoint
app.route('/courses', methods=['POST'])
def courses():
    return ""


#TODO -- complete put courses endpoint
app.route('/courses', methods=['PUT'])
def courses():
    return ""


#TODO -- complete delete courses
app.route('/courses', methods=['DELETE'])
def courses():
    return ""

    
# OUTCOMES CLASS
class Outcomes(db.Model):
    so_id = db.Column("so_id", db.Integer, primary_key=True)
    so_name = db.Column(db.String(4))
    so_desc = db.Column(db.String(1000))

    def __init__(self, so_name, so_desc):
        self.so_name = so_name
        self.so_desc = so_desc


@app.route("/outcomes", methods=["GET"])
def outcomes():
    outcomes = Outcomes.query.all()

    results = []

    for outcome in outcomes:
        outcome_data = {}
        outcome_data['so_name'] = outcome.so_name
        outcome_data['so_desc'] = outcome.so_desc
        results.append(outcome_data)

    return render_template('outcomes.html', outcomes=results)


# ASSIGNMENTS (SWP) CLASS
class Assignments(db.Model):
    swp_id = db.Column("swp_id", db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    swp_name = db.Column(db.String(100))

    def __init__(self, course_id, swp_name):
        self.course_id = course_id
        self.swp_name = swp_name


@app.route('/swp', methods=["GET"])
def swp():
    swps = Assignments.query.all()

    results = []

    for swp in swps:
        swp_data = {}
        swp_data['swp_id'] = swp.swp_id
        swp_data['swp_name'] = swp.swp_name
        swp_data['course_id'] = swp.course_id
        results.append(swp_data)

    return jsonify(results)


#TODO  -- complete endpoint
app.route('/swp', methods=['POST'])
def swp():
    return ""


#TODO -- complete put swp endpoint
app.route('/swp', methods=['PUT'])
def swp():
    return ""


#TODO -- complete delete swp
app.route('/swp', methods=['DELETE'])
def swp():
    return ""

    
# ATTEMPTS CLASS
class Attempts(db.Model):
    attempt_id = db.Column("id", db.Integer, primary_key=True)
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    so_id = db.Column(db.Integer, db.ForeignKey('outcomes.so_id'))

    def __init__(self, swp_id, so_id):
        self.swp_id = swp_id
        self.so_id = so_id


@app.route('/attempts', methods=["GET"])
def attempts():
    attempts = Attempts.query.all()

    results = []

    for attempt in attempts:
        attempt_data = {}
        attempt_data['attempt_id'] = attempt.attempt_id
        attempt_data['swp'] = attempt.swp_id
        attempt_data['so'] = attempt.so_id
        results.append(attempt_data)

    return jsonify(results)


#TODO  -- complete endpoint
app.route('/attempts', methods=['POST'])
def attempts():
    return ""


#TODO -- complete put attempts endpoint
app.route('/attempts', methods=['PUT'])
def attempts():
    return ""


#TODO -- complete delete attempts
app.route('/attempts', methods=['DELETE'])
def attempts():
    return ""

    
# ENROLLED CLASS
class Enrolled(db.Model):
    enrolled_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id


@app.route('/enrolled', methods=['GET'])
def enrolled():
    enrolled = Enrolled.query.all()
    results = []

    for enroll in enrolled:
        enrollment_data = {}
        enrollment_data['enrolled-id'] = enroll.enrolled_id
        enrollment_data['student-id'] = enroll.student_id
        enrollment_data['course_id'] = enroll.course_id
        results.append(enrollment_data)

    return jsonify(results)


#TODO  -- complete endpoint
app.route('/enrolled', methods=['POST'])
def enrolled():
    return ""


#TODO -- complete put enrolled endpoint
app.route('/enrolled', methods=['PUT'])
def enrolled():
    return ""


#TODO -- complete delete enrolled
app.route('/enrolled', methods=['DELETE'])
def enrolled():
    return ""

    
# RESULTS CLASS
class Results(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'))

    def __init__(self, student_id, attempt_id):
        self.student_id = student_id
        self.attempt_id = attempt_id


app.route('/results', methods=['GET'])
def results():
    results = Results.query.all()
    output = []

    for result in results:
        result_data = {}
        result_data['result id'] = result._id
        result_data['student id'] = result.student_id
        result_data['attempt id'] = results.attempt_id
        output.append(result_data)

    return jsonify(output)


#TODO  -- complete endpoint
app.route('/results', methods=['POST'])
def results():
    return ""


#TODO -- complete put results endpoint
app.route('/results', methods=['PUT'])
def results():
    return ""


#TODO -- complete delete results
app.route('/results', methods=['DELETE'])
def results():
    return ""


# BASE ROUTES (INDEX/HOME/REGISTER) -- THIS MAY BE MOVED LATER
@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("login.html")  # this should be the name of your html file


@app.route("/home", methods=["POST", "GET"])
def home():
    courses = None
    #if user not in session:
    #    return redirect('login')
   # else:
    return render_template("home.html")


@app.route("/logout")
def logout():
    message = "Logout Successful!"
    return render_template("login.html", message=message)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
