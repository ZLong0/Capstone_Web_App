#!/usr/bin/python3  
import os
from flask import Flask, render_template, jsonify, request, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import create_engine, distinct, func, delete, insert, update
from flask_mail import Mail, Message

app = Flask('__name__')
app.secret_key = "capstonefall2020"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atas.sqlite3'
db = SQLAlchemy(app)
engine = create_engine('sqlite:///atas.sqlite3')
login_manager = LoginManager(app)
mail = Mail(app)
sender_pass = os.environ.get('sendgrid_api_key')
sender = os.environ.get('sendgrid_sender_email')

app.config['SECRET_KEY'] = 'capstone_project_2020'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = sender_pass
app.config['MAIL_DEFAULT_SENDER'] = sender
mail = Mail(app)


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
    pending = db.Column("pending", db.Integer)

    def __init__(self, id, email, password, account_type, fname, lname, sec_question, answer, pending):
        self.email = email
        self.password = password
        self.account_type = account_type
        self.fname = fname
        self.lname = lname
        self.id = id
        self.sec_question = sec_question
        self.answer = answer
        self.pending = pending

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self.id

    def is_anonymous(self):
        return False


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)


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
            print("PASSWORD/USERNAME FAILED")
            error = 'Invalid Username/Password!  Please try again.'
            return render_template('login.html', error=error)
        elif user.pending == 1:
            print("PENDING USER REDIRECT")
            error = 'Account is unactivated, please wait for an email on when you account has been activated.'
            return render_template('login.html', error=error)
        elif user.pending == 0:
            # DEBUGGING STATEMENTS
            print(user.pending)
            if check_password_hash(pwhash=user.password, password=password_attempt):
                login_user(user)
                print("####################################")
                print("USER ACTIVE!  SUCCESSFULLY LOGGED IN")
                return redirect(url_for('home'))
    error = 'Invalid Username/Password!  Please try again.'
    return render_template('login.html', error=error)


# BASE ROUTES (INDEX/HOME/REGISTER)
@app.route("/", methods=["POST", "GET"])
def index():
    user = current_user.get_id()
    active = Users.query.filter_by(id=user).first()
    if not active:
        print("user not active -- redirect login")
        return render_template("login.html")
    else:
        print("user found -- redirect home")
        return redirect(url_for('home'))


# HOME -- CHECKS ACCOUNT TYPE, GATHERS NECESSARY INFORMATION FOR DROP DOWNS THEN RENDERS
# TEMPLATE BASED ON TYPE
@app.route("/home", methods=["POST", "GET"])
@login_required
def home():
    user_id = current_user.get_id()
    user = Users.query.get(user_id)
    user_list = Users.query.all()
    dbconnection = engine.connect()

    if user.account_type == 'instructor':
        semesters_list = get_instructor_courses(user_id)
        return render_template("inst_home.html", current_user=user, semesters=semesters_list)
    elif user.account_type == 'root':
        semesters_list = get_all_courses()
        return render_template("root_home.html", current_user=user, user_list=user_list, semesters=semesters_list)
    else:
        semesters_list = get_all_courses()
        return render_template("home.html", current_user=user, semesters=semesters_list)


@app.route("/register", methods=["POST", "GET"])
def register_user():
    error = None
    dbempty = db.session.query(Users).count()
    if request.method == "POST":
        add_id = request.form['employee_id']
        add_email = request.form["email"]
        password = request.form["password"]
        employee_id = request.form["employee_id"]
        account_type = request.form["access_level"]
        question_1 = request.form["question_1"]
        answer_1 = request.form["answer_1"]
        first_name = request.form['fname']
        last_name = request.form['lname']

        # output for debugging only
        print("email=" + add_email)
        print("password=" + password)
        print("employee_id=" + employee_id)
        print("access_level=" + account_type)
        print("question_1=" + question_1)
        print("answer_1=" + answer_1)

        if dbempty == 0:
            new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = Users(fname=first_name, lname=last_name, id=employee_id, email=add_email,
                             password=new_password, account_type='root',
                             sec_question=question_1, answer=answer_1, pending=0)
            msg = Message('ATAS Root Account Registration', recipients=[add_email])
            msg.body = 'ATAS Root Account Registration'
            msg.html = '<p>Thank you for registering a root account for ATAS ' + \
                       add_email + '. ATAS is now ready to be used by other users.</p>'
            mail.send(msg)
            db.session.add(new_user)
            db.session.commit()
            message = 'Application Ready'
            return render_template('login.html')
        elif dbempty != 0:
            user = Users.query.filter_by(id=add_id).first()
            email = Users.query.filter_by(email=add_email).first()
            root_cc = Users.query.filter_by(account_type='root').first()
            if user:
                error = "Employee ID is already registered"
                return render_template('register.html', error=error)
            elif email:
                error = "This email is already registered.  Please try again."
                msg = Message('ATAS Registration Attempt', recipients=[add_email])
                msg.body = 'ATAS Registration Attempt'
                msg.html = '<p>There was an attempt to register a new account in ATAS using the email ' + \
                           add_email + ', if this was not you, make sure to secure your ATAS account</p>'
                mail.send(msg)
                return render_template('register.html', error=error)
            else:
                if account_type == 'admin':
                    new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                    new_user = Users(fname=first_name, lname=last_name, id=employee_id, email=add_email,
                                     password=new_password, account_type='admin',
                                     sec_question=question_1, answer=answer_1, pending=1)
                    msg = Message('ATAS Registration Sent', recipients=[add_email], bcc=[root_cc.email])
                    msg.body = 'ATAS Registration Sent'
                    msg.html = '<p>Thank you for registering a new account in ATAS using ' + \
                               add_email + '. We will notify you when your account is ready to use</p>'
                    mail.send(msg)
                    db.session.add(new_user)
                    db.session.commit()
                    message = 'Registration sent'
                    return render_template('login.html')
                else:
                    new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                    new_user = Users(fname=first_name, lname=last_name, id=employee_id, email=add_email,
                                     password=new_password, account_type='instructor',
                                     sec_question=question_1, answer=answer_1, pending=1)
                    # new_instructor = Instructor(inst_id=employee_id, fname=first_name, lname=last_name)
                    msg = Message('ATAS Registration Sent', recipients=[add_email], bcc=[root_cc.email])
                    msg.body = 'ATAS Registration Sent'
                    msg.html = '<p>Thank you for registering a new account in ATAS using ' + \
                               add_email + '. We will notify you when your account is ready to use</p>'
                    mail.send(msg)
                    message = 'Registration sent'
                    db.session.add(new_user)
                    db.session.commit()
                    return render_template('login.html', message=message)
    else:
        return render_template('register.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    message = "Logout Successful!"
    return render_template("login.html", message=message)


@app.route("/root_pending", methods=["POST", "GET"])
@login_required
def pending_list_update():
    user_list = Users.query.all()
    if request.method == "POST":
        user_pending = request.form['user_pending']
        selected_user = Users.query.filter_by(email=request.form['user_select']).first()
        root_cc = Users.query.filter_by(account_type='root').first()
        instructor_check = Instructor.query.filter_by(inst_id=selected_user.id).first()
        if user_pending == 'approved':
            selected_user = Users.query.filter_by(email=selected_user.email).first()
            selected_user.pending = 0
            if selected_user.account_type == 'instructor':
                new_instructor = Instructor(inst_id=selected_user.id,
                                            fname=selected_user.fname, lname=selected_user.lname)
                db.session.add(new_instructor)
            msg = Message('ATAS Registration Approved', recipients=[selected_user.email], bcc=[root_cc.email])
            msg.body = 'ATAS Registration Approved'
            msg.html = '<p>Your account with the username/email of ' + selected_user.email + \
                       ' has been approved and is ready to use. Thank you for using ATAS.</p>'
            db.session.commit()
            mail.send(msg)
            message = "User " + selected_user.email + " approved successfully!"
            return redirect(url_for('home', message=message, user_list=user_list))
        elif user_pending == 'revoked':
            selected_user = Users.query.filter_by(email=selected_user.email).first()
            selected_user.pending = 1
            if selected_user.account_type == 'instructor' and instructor_check:
                instructor_check.delete()
            msg = Message('ATAS Account Suspended', recipients=[selected_user.email], bcc=[root_cc.email])
            msg.body = 'ATAS Account Suspended'
            msg.html = '<p>Your account with the username/email of ' + selected_user.email + \
                       ' has been suspended and can no longer be used. Please contact an administrator' \
                       ' to begin the process of account reactivation.</p>'
            db.session.commit()
            mail.send(msg)
            message = "User " + selected_user.email + " suspended successfully!"
            return redirect(url_for('home', message=message, user_list=user_list))
        elif user_pending == 'denied':
            if selected_user.account_type == 'instructor':
                instructor_check.delete()
            Users.query.filter_by(email=selected_user.email).delete()
            db.session.commit()
            message = "User deleted successfully!"
            return redirect(url_for('home', message=message, user_list=user_list))
    return redirect(url_for('home', user_list=user_list))


# INSTRUCTORS CLASS
class Instructor(db.Model):
    inst_id = db.Column("id", db.Integer, primary_key=True, autoincrement=False)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, inst_id, fname, lname):
        self.inst_id = inst_id
        self.fname = fname
        self.lname = lname


# GET ALL INSTRUCTORS
@app.route('/instructors', methods=['GET'])
@login_required
def get_instructors():
    instructors = Instructor.query.all()
    results = []

    user = current_user
    if user.account_type == 'instructor':
        return redirect(url_for('home'))
    else:
        for instructor in instructors:
            instructor_data = {}
            instructor_data['instructor_id'] = instructor.inst_id
            instructor_data['first_name'] = instructor.fname
            instructor_data['last_name'] = instructor.lname
            results.append(instructor_data)

        return results


# GET ONE INSTRUCTORS INFO
@app.route('/instructors/<int:instructor_id>', methods=['GET'])
@login_required
def get_one_instructor(instructor_id):
    user = current_user
    id = instructor_id
    if user.account_type == 'instructor':
        id = user.get_id()
    else:
        id = instructor_id

    instructor = Instructor.query.get(id)
    results = []
    instructor_data = {}
    instructor_data['instructor_id'] = instructor.inst_id
    instructor_data['first_name'] = instructor.fname
    instructor_data['last_name'] = instructor.lname
    results.append(instructor_data)

    return jsonify(results)


# UPDATE ONE INSTRUCTOR
@app.route('/instructors/<instructor_id>', methods=['POST', 'GET'])
@login_required
def update_instructor(instructor_id):
    user = current_user
    if user.account_type == 'instructor':
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            # check for existing instructor id first
            instructor = Instructor.query.get(instructor_id)
            if instructor:
                instructor.fname = request.form['first_name']
                instructor.lname = request.form['last_name']
                db.session.commit()
                print('Instructor Updated!')
                return redirect(url_for('get_instructors'))
            else:
                print("Instructor not found. Cannot update")
        else:
            return redirect(url_for('get_one_instructor', instructor_id=instructor_id))


# ADD NEW INSTRUCTOR
@app.route('/instructors', methods=['POST', 'GET'])
@login_required
def add_instructor():
    user = current_user
    if user.account_type == 'instructor':
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            # check for existing instructor id first
            try:
                instructor = Instructor.query.get(request.form['id'])
            except:
                print("EXCEPTION ERROR")
                return redirect(url_for('get_instructors'))

            if instructor:
                print("instructor found")
                return redirect(url_for('get_instructors'))
            else:
                print("instructor not found -- add")
                id = request.form['id']
                print(id)
                fname = request.form['first_name']
                print(fname)
                lname = request.form['last_name']
                print(lname)
                instructor = Instructor(id, fname, lname)

                if instructor:
                    print("instructor created")
                    instructor_data = {}
                    result = []
                    instructor_data['first'] = fname
                    instructor_data['last'] = lname
                    instructor_data['id'] = id
                    result.append(instructor_data)
                    print(result)
                dbconnection = engine.connect()
                statement = f"INSERT INTO instructor(id, fname, lname) VALUES ({id}, '{fname}','{lname}');"
                print(statement)
                dbconnection.execute(statement)
                dbconnection.close()
                return redirect(url_for('get_instructors'))
        else:
            return redirect(url_for('get_instructors'))


# DELETE ONE INSTRUCTOR
@app.route('/instructors/<instructor_id>', methods=['DELETE', 'GET'])
@login_required
def delete_instructor(instructor_id):
    if request.method == 'DELETE':
        # check for existing instructor id first
        instructor = Instructor.query.get(instructor_id)
        if instructor:
            db.session.delete(instructor)
            db.session.commit()
            print("Instructor deleted " + instructor_id)
            return redirect(url_for('get_instructors'))
        else:
            print("Instructor not found. Cannot delete")
            return redirect(url_for('get_instructors'))
    else:
        return redirect(url_for('get_instructors'))


# STUDENT CLASS
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, student_id, fname, lname):
        self.fname = fname
        self.lname = lname
        self.stude_id = student_id


# GET ALL STUDENTS
@app.route('/students', methods=['GET'])
@login_required
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


# GET ONE STUDENT
@app.route('/students/<int:student_id>', methods=['GET'])
@login_required
def get_one_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return "Student not found"
    results = []
    student_data = {}
    student_data['student_id'] = student.student_id
    student_data['first_name'] = student.fname
    student_data['last name'] = student.lname
    results.append(student_data)

    return jsonify(results)


# UPDATE ONE STUDENT
@app.route('/students/<int:student_id>', methods=['GET', 'POST'])
@login_required
def update_student(student_id):
    if request.method == 'POST':
        try:
            # get course to update by ID save in var
            student = Student.query.get(student_id)

            # update existing course info based on form input
            student.fname = request.form['first_name']
            student.lname = request.form['last_name']

            # commit changes to db
            db.session.commit()
            flash('Student Updated!')
            # return redirect(url_for('home'))
            return redirect(url_for('get_all_students'))
        except:
            flash('Update failed!')
            return redirect(url_for('get_all_courses'))
    else:
        return redirect(url_for('get_all_students'))


# ADD NEW STUDENT
@app.route('/students', methods=['GET', 'POST'])
@login_required
def add_students():
    if request.method == 'POST':
        student = Student.query.get(request.form['student_id'])
        if student:
            print("student found")
            return redirect(url_for('get_all_students'))
        else:
            print("student not found -- add student")
            student_id = request.form['id']
            print(student_id)
            fname = request.form['first_name']
            print(fname)
            lname = request.form['last_name']
            print(lname)
            student = Student(student_id, fname, lname)

            if student:
                print("student created")
                student_data = {}
                result = []
                student_data['first'] = fname
                student_data['last'] = lname
                student_data['id'] = student_id
                result.append(student_data)
                print(result)
            print("work you stupid thing")
            dbconnection = engine.connect()
            statement = f"INSERT INTO student(student_id, fname, lname) VALUES ({student_id}, '{fname}','{lname}');"
            print(statement)
            dbconnection.execute(statement)
            dbconnection.close()
            return redirect(url_for('get_all_students'))


# DELETE ONE STUDENT
@app.route('/students/<int:student_id>', methods=['GET', 'DELETE'])
@login_required
def delete_students(student_id):
    if request.method == 'DELETE':
        try:
            student = Student.query.get(student_id)
            db.session.delete(student)
            db.session.commit()
            print("Student deleted" + student_id)
        except:
            print("Error:  Delete Unsuccessful")
        return redirect(url_for('get_all_students'))
    else:
        return redirect(url_for('get_all_students'))


# COURSE CLASS
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

    def get_id(self):
        return self.id


@app.route('/courses/', methods=['GET'])
# @login_required
def get_all_courses():
    if request.method == "GET":
        courses_group = []
        terms = []
        user = current_user
        uid = current_user.get_id()
        print(uid)
        year = []
        semesters_list = []

        if user.account_type == 'instructor':
            return redirect(url_for('home'))

        dbconnection = engine.connect()
        terms = dbconnection.execute("select distinct term, year from course")
        for term in terms:
            semester_data = {}
            courses_group = Course.query.filter_by(term=term[0], year=term[1]).all()
            print(courses_group)
            if courses_group:
                semester_data['term'] = term[0]
                semester_data['year'] = term[1]
                courses = []
                for course in courses_group:
                    course_data = {}
                    course_data['course_id'] = course.get_id()
                    course_data['department'] = course.department
                    course_data['course_number'] = course.course_number
                    course_data['section'] = course.section
                    course_data['year'] = course.year
                    course_data['course_name'] = course.course_name
                    course_data['instructor_id'] = course.instructor
                    courses.append(course_data)
                    sorted_courses = sorted(courses, key=lambda i:i['course_number'])
                    semester_data['course_list'] = sorted_courses
                    # print(courses)
            semesters_list.append(semester_data)
        dbconnection.close()
        print(semesters_list)
        return semesters_list


@app.route('/courses/edit', methods=['GET'])
# @login_required
def edit_courses():
    if request.method == "GET":
        all_courses = get_all_courses()
        instructors = get_instructors()
        print(all_courses)
        print(instructors)
        return render_template('edit_courses.html', courses = all_courses, semesters=all_courses, instructors=instructors)


@app.route('/courses/<int:course_id>', methods=['GET'])
@login_required
def get_one_course(course_id):
    user_id = Users.get_id(current_user)
    user = Users.query.get(user_id)
    course = Course.query.get(course_id)
    course_results = []
    course_info = {}
    if not course:
        return ("Course not found")
    course_info['course_name'] = course.course_name
    course_info['term'] = course.term
    course_info['year'] = course.year
    course_info['course_department'] = course.department
    course_info['course_number'] = course.course_number
    course_info['section'] = course.section
    course_info['instructor_id'] = course.instructor
    course_info['course_id'] = course.id
    course_results.append(course_info)

    swp_results = get_course_swps(course_id)
    student_results = get_course_results(course_id)  

    #print(course_results)
    #print(swp_results)
    #print(student_results)
    #return jsonify(student_results)

    if user.account_type == 'instructor':
        semesters_list = get_instructor_courses(user_id)
        print(semesters_list)
        return render_template('inst_courses.html', courses=course_results, students=student_results, swps=swp_results,
                               semesters=semesters_list)
    else:
        semesters_list = get_all_courses()
        return render_template('courses.html', courses=course_results, students=student_results, swps=swp_results,
                               semesters=semesters_list)


# gets all courses for specific instructor id
@app.route('/courses/inst/<int:instructor_id>', methods=['GET'])
@login_required
def get_instructor_courses(instructor_id):
    print('GET_INSTRUCTOR_COURSES')
    results = []
    user = current_user
    print(instructor_id)
    uid = current_user.get_id()

    # ATTEMPTING TO KEEP OTHER INSTRUCTORS FROM ACCESSING OTHER INST COURSES
    # WHILE ALLOWING ADMING TO SELECT COURSES SPECIFIC TO ONE INSTRUCTOR
    if uid != instructor_id:
        if user.account_type == 'admin':
            pass
        else:
            return redirect(url_for('home'))

    if request.method == "GET":
        courses_group = []
        terms = []
        print(uid)
        year = []
        semesters_list = []

        dbconnection = engine.connect()
        terms = dbconnection.execute("select distinct term, year from course")
        for term in terms:
            semester_data = {}
            courses_group = Course.query.filter_by(instructor=instructor_id, term=term[0], year=term[1]).all()
            # print(courses_group)
            if courses_group:
                semester_data['term'] = term[0]
                semester_data['year'] = term[1]
                courses = []
                for course in courses_group:
                    course_data = {}
                    course_data['course_id'] = course.get_id()
                    course_data['department'] = course.department
                    course_data['course_number'] = course.course_number
                    course_data['section'] = course.section
                    course_data['course_name'] = course.course_name
                    courses.append(course_data)
                    sorted_courses = sorted(courses, key=lambda i:i['course_number'])
                    semester_data['course_list'] = sorted_courses
                    # print(courses)
            else:
                continue
            semesters_list.append(semester_data)

        if not terms:
            dbconnection.close()
            semesters_list = None
            return semesters_list
        else:
            dbconnection.close()
            return semesters_list
    else:
        return render_template("inst_courses.html")


@app.route('/courses/<int:course_id>', methods=['GET', 'POST'])
# @login_required
def update_courses(course_id):
    if request.method == 'POST':
        # get course to update by ID save in var
        course = Course.query.get(course_id)
        if course:
            # update existing course info based on form input
            course.term = request.form['term']
            course.year = request.form['year']
            course.deparment = request.form['department']
            course.course_name = request.form['course_name']
            course.course_number = request.form['course_number']
            course.section = request.form['section']
            course.instructor = request.form['instructor_id']
            db.session.commit()
            print(course.instructor)
        else:
            return ("update course failed")
            # return render_template('/home')

        print('Course Updated!')
        #return redirect(url_for('get_all_courses'))
        # return redirect(url_for('home'))
        return redirect(url_for('edit_courses'))


@app.route('/courses', methods=['GET', 'POST'])
# @login_required
def add_courses():
    if request.method == 'POST':
        # instantiate new course info based on form input
        term = request.form['term']
        year = request.form['year']
        department = request.form['department']
        course_name = request.form['course_name']
        course_number = request.form['course_number']
        section = request.form['section']
        instructor_id = request.form['instructor_id']
        new_course = Course(course_name, term, year, department, course_number, section, instructor_id)

        # check database for existing course overlap
        existing_course = Course.query.filter_by(
            term=term,
            year=year,
            department=department,
            course_number=course_number,
            section=section).first()

        # return error if existing course returns true otherwise add course
        if existing_course:
             print("Error:  Course already exists in selected semester/year!")
             return redirect(url_for('edit_courses'))
        else:
            # commit changes to db
            print("ADD NEW COURSE TO DB")
            dbconnection = engine.connect()
            statement = f"INSERT INTO course(course_name, term, year, department, course_number, section, instructor)\
                    VALUES ('{new_course.course_name}','{new_course.term}', '{new_course.year}', \
                        '{new_course.department}','{new_course.course_number}','{new_course.section}', {new_course.instructor} );"
            print(statement)
            dbconnection.execute(statement)
            dbconnection.close()
            print("course added!")
            return redirect(url_for('edit_courses'))

    return ("course add failed")

#new branch cleanup
@app.route('/courses/<int:course_id>', methods=['GET', 'DELETE'])
# @login_required
def delete_course(course_id):
    if request.method == 'DELETE':
        course = Course.query.get(course_id)
        if course:
            db.session.delete(course)
            db.session.commit()
            return redirect(url_for('get_all_courses'))
            return ("course found")
        return ("please stop getting mad")


# OUTCOMES CLASS
class Outcomes(db.Model):
    so_id = db.Column("so_id", db.Integer, primary_key=True)
    so_name = db.Column(db.String(4))
    so_desc = db.Column(db.String(1000))

    def __init__(self, so_name, so_desc):
        self.so_name = so_name
        self.so_desc = so_desc


# GET ALL OUTCOMES
@app.route('/outcomes', methods=["GET"])
@login_required
def outcomes():
    user = current_user
    uid = current_user.get_id()

    semesters_list = []
    outcomes = Outcomes.query.all()
    outcomes_list = []
    courses = Course.query.all()
    for outcome in outcomes:
        outcome_data = {}
        outcome_data['so_name'] = outcome.so_name
        outcome_data['so_desc'] = outcome.so_desc
        outcomes_list.append(outcome_data)

    if user.account_type == 'instructor':
        semesters_list = get_instructor_courses(uid)
        return render_template('inst_outcomes.html', outcomes=outcomes_list, semesters=semesters_list)
    else:
        semesters_list = get_all_courses()
        return render_template('outcomes.html', outcomes=outcomes_list, semesters=semesters_list)


# ASSIGNMENTS (SWP) CLASS
class Assignments(db.Model):
    swp_id = db.Column("swp_id", db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    swp_name = db.Column(db.String(100))

    def __init__(self, course_id, swp_name):
        self.course_id = course_id
        self.swp_name = swp_name


# THIS GETS ALL WORK PRODUCTS IN THE DATABASE
@app.route('/swp', methods=["GET"])
@login_required
def get_all_swp():
    swps = Assignments.query.all()

    results = []

    for swp in swps:
        swp_data = {}
        course = Course.query.get(swp.course_id)
        attempts_list = get_swp_attempts(swp.swp_id)
        for attempt in attempts_list:
            swp_data['SO1'] = attempt['SO1']
            swp_data['SO2'] = attempt['SO2']
            swp_data['SO3'] = attempt['SO3']
            swp_data['SO4'] = attempt['SO4']
            swp_data['SO5'] = attempt['SO5']
            swp_data['SO6'] = attempt['SO6']
        swp_data['swp_id'] = swp.swp_id
        swp_data['swp_name'] = swp.swp_name
        swp_data['course_id'] = course.id
        swp_data['course name'] = course.course_name

        results.append(swp_data)

    return jsonify(results)


# GET ONE SWP
@app.route('/swp/<int:swp_id>', methods=["GET"])
@login_required
def get_one_swp(swp_id):
    swp = Assignments.query.get(swp_id)

    results = []
    swp_data = {}
    attempts_list = get_swp_attempts(swp.swp_id)
    for attempt in attempts_list:
        swp_data['SO1'] = attempt['SO1']
        swp_data['SO2'] = attempt['SO2']
        swp_data['SO3'] = attempt['SO3']
        swp_data['SO4'] = attempt['SO4']
        swp_data['SO5'] = attempt['SO5']
        swp_data['SO6'] = attempt['SO6']
    swp_data['swp_id'] = swp.swp_id
    swp_data['swp_name'] = swp.swp_name
    swp_data['course_id'] = swp.course_id
    course = Course.query.get(swp.course_id)
    swp_data['course name'] = course.course_name
    results.append(swp_data)

    return jsonify(results)


# THIS GETS WORK PRODUCT FOR SPECIFIC COURSE
@app.route('/swp/course/<int:course_id>', methods=["GET"])
# @login_required
def get_course_swps(course_id):
    swps = Assignments.query.filter_by(course_id=course_id).all()
    results = []

    for swp in swps:
        swp_data = {}
        course = Course.query.get(swp.course_id)
        attempts_list = get_swp_attempts(swp.swp_id)
        if len(attempts_list)==0:
            swp_data['SO1'] = 0
            swp_data['SO2'] = 0
            swp_data['SO3'] = 0
            swp_data['SO4'] = 0
            swp_data['SO5'] = 0
            swp_data['SO6'] = 0
        else:
            for attempt in attempts_list:
                swp_data['SO1'] = attempt['SO1']
                swp_data['SO2'] = attempt['SO2']
                swp_data['SO3'] = attempt['SO3']
                swp_data['SO4'] = attempt['SO4']
                swp_data['SO5'] = attempt['SO5']
                swp_data['SO6'] = attempt['SO6']
        swp_data['swp_id'] = swp.swp_id
        swp_data['swp_name'] = swp.swp_name
        swp_data['course_id'] = course.id
        swp_data['course name'] = course.course_name
        results.append(swp_data)

    sorted_results = sorted(results, key=lambda i:i['swp_id'])
    return jsonify(sorted_results)


# UPDATE ONE SWP
@app.route('/swp/<int:swp_id>', methods=['GET', 'POST'])
@login_required
def update_swp(swp_id):
    if request.method == 'POST':
        swp = Assignments.query.get(swp_id)
        print(swp)
        if swp:
            # swp.course_id = request.form('course_id')
            name = request.form['swp_name']
            name = name.upper()
            swp.swp_name = name
            db.session.commit()
            print("Student Work Product succesfully updated!")
            return redirect(url_for('get_one_course', course_id = swp.course_id))
            # return redirect(url_for('home'))
        else:
            return "Error:  Student Work Product not found"
            # return redirect(url_for('home'))

    return redirect(url_for('get_one_course', course_id = swp.course_id))


# ADD NEW SWP
@app.route('/swp', methods=['GET', 'POST'])
@login_required
def add_swp():
    if request.method == 'POST':
        # instantiate new work product info based on form input
        course_id = request.form['course_id']
        swp_name = request.form['swp_name']        
        so1 = request.form['SO1']
        so2 = request.form['SO2']
        so3 = request.form['SO3']
        so4 = request.form['SO4']
        so5 = request.form['SO5']
        so6 = request.form['so6']
        print(swp_name)
        print(course_id)
        swp_name = swp_name.upper()
        new_swp = Assignments(course_id, swp_name)
        # check database for existing  overlap
        existing_swp = Assignments.query.filter_by(swp_name=swp_name, course_id=course_id).all()

        # return error if existing info returns true -- otherwise add course
        if existing_swp:
            message = "Student Work Product already exists in current course.  Please pick a unique name"
        else:
            # commit changes to db
            add_attempts(swp_name,course_id, so1, so2, so3, so4, so5, so6)
            dbconnection = engine.connect()
            statement = f"INSERT INTO Assignments(course_id, swp_name)\
                    VALUES ({new_swp.course_id},'{new_swp.swp_name}');"
            print(statement)
            dbconnection.execute(statement)
            dbconnection.close()
            print("SWP added!")
            return redirect(url_for('get_one_course', course_id = course_id))

    else:
        return redirect(url_for('get_one_course', course_id = course_id))

    return redirect(url_for('get_one_course', course_id = course_id))


# DELETE SWP
@app.route('/swp/<int:swp_id>', methods=['GET', 'DELETE'])
@login_required
def delete_swp(swp_id):
    if request.method == 'DELETE':
        swp = Assignments.query.get(swp_id)
        delete_attempts(swp_id)
        db.session.delete(swp)
        db.session.commit()

        print("Work Product Deleted")

    return redirect(url_for('get_all_swp'))
    return redirect(url_for('home'))


# ATTEMPTS CLASS
class Attempts(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=False)
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    so1 = db.Column("SO1", db.Integer)
    so2 = db.Column("SO2", db.Integer)
    so3 = db.Column("SO3", db.Integer)
    so4 = db.Column("SO4", db.Integer)
    so5 = db.Column("SO5", db.Integer)
    so6 = db.Column("SO6", db.Integer)

    def __init__(self, swp_id, so1, so2, so3, so4, so5, so6):
        self.swp_id = swp_id
        self.so1 = so1
        self.so2 = so2
        self.so3 = so3
        self.so4 = so4
        self.so5 = so5
        self.so6 =so6


# GET ALL ATTEMPTS -- UNION OF SWP AND SO
@app.route('/attempts', methods=["GET"])
#@login_required
def get_all_attempts():
    attempts = Attempts.query.all()

    results = []

    for attempt in attempts:
        attempt_data = {}
        swp = Assignments.query.get(attempt.swp_id)
        course = Course.query.get(swp.course_id)

        attempt_data['attempt_id'] = attempt.id
        attempt_data['course_name'] = course.course_name
        attempt_data['swp'] = swp.swp_name
        attempt_data['SO1'] = attempt.so1
        attempt_data['SO2'] = attempt.so2
        attempt_data['SO3'] = attempt.so3
        attempt_data['SO4'] = attempt.so4
        attempt_data['SO5'] = attempt.so5
        attempt_data['SO6'] = attempt.so6
        results.append(attempt_data)

    return jsonify(results)


# GET SWP ATTEMPTS 
@app.route('/attempts/swp/<int:swp_id>', methods=["GET"])
# @login_required
def get_swp_attempts(swp_id):
    attempts = Attempts.query.filter_by(swp_id=swp_id).all()
    # print(attempts)
    results = []
    attempt_data = {}

    attempt_data = {}
    swp = Assignments.query.get(swp_id)
    course = Course.query.get(swp.course_id)

    for attempt in attempts:
        attempt_data['attempt_id'] = attempt.id
        attempt_data['course_name'] = course.course_name
        attempt_data['swp'] = swp.swp_name
        attempt_data['SO1'] = attempt.so1
        attempt_data['SO2'] = attempt.so2
        attempt_data['SO3'] = attempt.so3
        attempt_data['SO4'] = attempt.so4
        attempt_data['SO5'] = attempt.so5
        attempt_data['SO6'] = attempt.so6
        results.append(attempt_data)

    # print(results)
    return results


# UPDATE ONE ATTEMPT
@app.route('/attempts/<int:swp_id>', methods=['GET', 'POST'])
# @login_required
def update_attempts(swp_id):
    if request.method == 'POST':
        try:
            attempt = Attempts.query.get(swp_id)
            if not attempt:
                add_attempts()
            attempt.so1 = request.form['SO1']
            attempt.so2 = request.form['SO2']
            attempt.so3 = request.form['SO3']
            attempt.so4 = request.form['SO4']
            attempt.so5 = request.form['SO5']
            attempt.so6 = request.form['SO6']
            db.session.commit()
            print("Attempt record succesfully updated!")
            return redirect(url_for('get_all_attempts'))
        except:
            return ("ERROR OCCURED ON UPDATE")
    return redirect(url_for('get_all_attempts'))


# ADD NEW ATTEMPT
@app.route('/attempts', methods=['GET', 'POST'])
# @login_required
def add_attempts():
    if request.method == 'POST':
        try:
            # instantiate new  info based on form input
            swp_id = request.form['swp_id']
            so1 = request.form['SO1']
            so2 = request.form['SO2']
            so3 = request.form['SO3']
            so4 = request.form['SO4']
            so5 = request.form['SO5']
            so6 = request.form['SO6']
            # check database for existing course overlap
            existing_attempt = Attempts.query.filter_by(swp_id=swp_id).all()
            # return error if existing course returns true otherwise add course
            if existing_attempt:
                print('Info already exists!')
                update_attempts(swp_id)
            else:
                print('New SO/SWP combination FOUND!')
                dbconnection = engine.connect()
                statement = f"INSERT INTO attempts(swp_id, so1, so2, so3, so4, so5, so6) VALUES ({swp_id}, {so1}, {so2}, {so3}, {so4}, {so5}, {so6});"
                print(statement)
                dbconnection.execute(statement)
                dbconnection.close()
                return redirect(url_for('get_all_attempts'))
        # IF TRY FAILS -- RETURN FAILURE MESSAGE
        except:
            print('EXCEPTION: Add failed!')
            return redirect(url_for('get_all_attempts'))

def add_attempts(swp_name, course_id, so1, so2, so3, so4, so5, so6):
        swp = Assignments.query.filter_by(swp_name = swp_name, course_id=course_id).all()

        existing_attempt = Attempts.query.filter_by(swp_id=swp.swp_id).all()
            # return error if existing course returns true otherwise add course
        if existing_attempt:
            print('Info already exists!')
            #update_attempts(swp_id)
        else:
            print('New SO/SWP combination FOUND!')
            dbconnection = engine.connect()
            statement = f"INSERT INTO attempts(swp_id, so1, so2, so3, so4, so5, so6) VALUES ({swp.swp_id}, {so1}, {so2}, {so3}, {so4}, {so5}, {so6});"
            print(statement)
            dbconnection.execute(statement)
            dbconnection.close()
            return redirect(url_for('get_all_attempts'))
        # IF TRY FAILS -- RETURN FAILURE MESSAGE

    # return redirect(url_for('home'))


# DELETE ONE ATTEMPT
@app.route('/attempts/<int:swp_id>', methods=['GET', 'DELETE'])
# @login_required
def delete_attempts(swp_id):
    if request.method == 'DELETE':
        try:
            attempt = Attempts.query.filter_by(swp_id = swp_id)
            print(attempt)
            db.session.delete(attempt)
            db.session.commit()
            print(" Deleted")
        except:
            print("Error:  Delete Unsuccessful")

    return redirect(url_for('get_all_attempts'))


# ENROLLED CLASS
class Enrolled(db.Model):
    enrolled_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id


# GET ENROLLMENTS FOR A SPECIFIC COURSE
@app.route('/enrolled', methods=['GET'])
# @login_required
def get_all_enrolled():
    print("GET_ALL_ENROLLED_")
    enrolled = Enrolled.query.all()
    results_list = []
    swp_list = []
    user = current_user

    for enroll in enrolled:
        enrollment_data = {}
        student_id = enroll.student_id
        print(student_id)
        student = Student.query.get(student_id)
        print(student)
        results = Results.query.filter_by(student_id=student_id).all()
        # print(results)
        if student:
            enrollment_data['student_id'] = student.student_id
            enrollment_data['student_first'] = student.fname
            enrollment_data['student_last'] = student.lname

        enrollment_data['course_id'] = enroll.course_id
        results_list.append(enrollment_data)
    return jsonify(results_list)


# GET ENROLLMENTS FOR A SPECIFIC COURSE
@app.route('/enrolled/<int:course_id>', methods=['GET'])
# @login_required
def get_course_enrolled(course_id):
    print("GET_COURSE_ENROLLED")
    enrolled = Enrolled.query.filter_by(course_id=course_id)
    results_list = []
    swp_list = []
    user = current_user
   
    for enroll in enrolled:
        enrollment_data = {}
        student_id = enroll.student_id
        #print(student_id)
        student = Student.query.get(student_id)
        #print(student)
        if student:
            enrollment_data['student_id'] = student.student_id
            enrollment_data['student_first'] = student.fname
            enrollment_data['student_last'] = student.lname

        enrollment_data['course_id'] = enroll.course_id
        results_list.append(enrollment_data)

    sorted_results = sorted(results_list, key=lambda i: i['student_last'])
    return sorted_results



# TODO -- NOT SURE IF WE NEED THIS METHOD OR NOT
@app.route('/enrolled/<int:course_id>', methods=['GET', 'POST'])
# @login_required
def update_enrolled(course_id):
    return ""


# ENROLL STUDENT IN ONE COURSE
@app.route('/enrolled', methods=['GET', 'POST'])
# @login_required
def add_enrolled():
    if request.method == 'POST':
        print("ADD_NEW_ENROLLMENT")
        # instantiate new  info based on form input
        student_id = request.form['student_id']
        course_id = request.form['course_id']

        # IF emrollment EXISTS RETURN INVALID ENTRY
        new_enrollment = Enrolled(student_id, course_id)

        # check database for existing enrollment overlap
        existing_enrollment = Enrolled.query.filter_by(
            student_id=new_enrollment.student_id,
            course_id=new_enrollment.course_id).all()

        # return error if existing enrollment returns true -- otherwise add enrollment
        if existing_enrollment:
            return "Student already enrolled in this course!"
            # return redirect(url_for('home'))

        else:
            # commit changes to db
            dbconnection = engine.connect()
            statement = f"INSERT INTO enrolled(student_id, course_id) VALUES ({student_id}, {course_id});"
            print(statement)
            dbconnection.execute(statement)
            dbconnection.close()
            print("Student successfully enrolled in course!")
            return redirect(url_for('get_enrolled', course_id=course_id))


#           return redirect(url_for('home'))

#    return redirect(url_for('home'))


# DELETE STUDENT FROM ALL COURSES
@app.route('/enrolled/student/<int:student_id>', methods=['GET', 'DELETE'])
# @login_required
def delete_student_from_enrolled(student_id):
    if request.method == 'DELETE':
        print("delete student enrollments")
        try:
            enrollment = Enrolled.query.filter_by(student_id=student_id).all()
            for enroll in enrollment:
                db.session.delete(enroll)
                db.session.commit()
            print("Enrollment Deleted")
        except:
            print("Error:  Delete Unsuccessful")
    return redirect(url_for('get_all_enrolled'))
    # return redirect(url_for('home'))


# DELETE STUDENT FROM ONE COURSE
@app.route('/enrolled/<int:course_id>/<int:student_id>', methods=['GET', 'DELETE'])
# @login_required
def delete_student_from_course(course_id, student_id):
    if request.method == 'DELETE':
        print("DELETE STUDENT FROM ONE COURSE")
        enrollment = Enrolled.query.filter_by(student_id=student_id, course_id=course_id).first()
        print(enrollment)
        db.session.delete(enrollment)
        db.session.commit()

        print("Enrollment Deleted")
    return redirect(url_for('get_all_enrolled'))
    # return redirect(url_for('home'))


# RESULTS CLASS
class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'))
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    value = db.Column(db.Integer)

    def __init__(self, student_id, swp_id, value):
        self.student_id = student_id
        self.swp_id = swp_id
        self.value = value


@app.route('/results', methods=['GET'])
# @login_required
def get_all_results():
    results = Results.query.all()
    print(results)
    output = []

    for result in results:
        result_data = {}
        student = Student.query.get(result.student_id)
        swp = Assignments.query.get(result.swp_id)
        result_data['result id'] = result.id
        result_data['student first'] = student.fname
        result_data['student last'] = student.lname
        result_data['student_id'] = student.student_id
        result_data['swp name'] = swp.swp_name
        result_data['value'] = result.value
        output.append(result_data)
    print(output)
    return jsonify(output)


@app.route('/results/course/<int:course_id>', methods=['GET'])
# @login_required
def get_course_results(course_id):
    assignments = Assignments.query.filter_by(course_id=course_id).all()
    #print(assignments)
    output = []

    sorted_students = get_course_enrolled(course_id)
    #print(sorted_students)

    for student in sorted_students:
        #print("OUTER LOOP")
        result_data = {}
        student_id = student['student_id']
        result_data['student_id'] = student['student_id']
        result_data['student_first'] = student['student_first']
        result_data['student_last'] = student['student_last']
            
        assignments = get_course_swps(course_id)
        #print(assignments)
        scores_list = []
       
        for assignment in assignments:
            #FOR EACH ASSIGNMENT GET RESULTS BY STUDENT_ID                   
            student_scores = Results.query.filter_by(swp_id = assignment['swp_id'],student_id = student_id).first()
            scores_data = {}
            if student_scores == None:
                scores_data['swp_id'] = assignment['swp_id']
                scores_data['score'] = "-"
            else:
                scores_data['swp_id'] = assignment['swp_id']
                scores_data['score'] = student_scores.value
            
            scores_list.append(scores_data)
        
        sorted_scores = sorted(scores_list, key=lambda i:i['swp_id'])

        result_data['student_scores'] = scores_list
        output.append(result_data)

    for student in output:
        print(student['student_id'])
        print(student['student_first'])
        print(student['student_last'])
        print(student['student_scores'])
        scores = student['student_scores']
        for score in scores:
            print(score['score'])
        
    return output


@app.route('/results/student/<int:student_id>/<int:swp_id>', methods=['GET', 'POST'])
# @login_required
def update_student_result(student_id, swp_id):
    if request.method == "POST":
        results = Results.query.filter_by(student_id=student_id, swp_id=swp_id).all()
        if results:
            for result in results:
                result.value = request.form['score']
                db.session.commit()
        else:
            return ("no assignments found")
        # return url_for('get_course_results')
        return redirect(url_for('get_all_results'))

    return redirect(url_for('get_all_results'))


# TODO -- complete put results endpoint
@app.route('/results', methods=['POST', 'GET'])
# @login_required
def add_results():
    if request.method == "post":
        try:
            student_id = request.form['student_id']
            swp_id = request.form['swp_id']
            if Results.query.filter_by(swp_id=swp_id, student_id=student_id).all():
                return redirect(url_for('update_student_result', student_id=student_id, swp_id=swp_id, method='POST'))
            else:
                print("NEW RESULT FOUND -- INSERT INTO DB")
                value = request.form['score']
                dbconnection = engine.connect()
                statement = f"INSERT INTO Results(student_id, swp_id, value)\
                        VALUES ({student_id},{swp_id}, {value});"
                print(statement)
                dbconnection.execute(statement)
                dbconnection.close()
                print("RESULT added!")
                return redirect(url_for('get_all_results'))
        except:
            return "test failed"


@app.route('/results/<int:result_id>', methods=['DELETE', 'GET'])
# @login_required
def delete_one_result(result_id):
    if request.method == "DELETE":
        print("DELETE RESULT CALLED")
        result = Results.query.get(result_id)
        if not result:
            return ("could not find result id# " + str(result_id))
        else:
            db.session.delete(result)
            db.session.commit()
            print("Result Deleted")
            return redirect(url_for('get_all_results'))

    return redirect(url_for('get_all_results'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
