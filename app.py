#!/usr/bin/python3  
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


app.config['SECRET_KEY'] = 'capstonefall2020'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_DEFAULT_SENDER'] = 'atas.mail.response@gmail.com'
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

    def __init__(self, id, email, password, account_type, fname, lname, sec_question, answer):
        self.email = email
        self.password = password
        self.account_type = account_type
        self.fname = fname
        self.lname = lname
        self.id = id
        self.sec_question = sec_question
        self.answer = answer

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
            error = 'Invalid Username/Password!  Please try again.'
            return render_template('login.html', error=error)
        elif check_password_hash(pwhash=user.password, password=password_attempt):
            login_user(user)
            return redirect(url_for('home'))
    error = 'Invalid Username/Password!  Please try again.'
    return render_template('login.html', error=error)


# BASE ROUTES (INDEX/HOME/REGISTER)
@app.route("/", methods=["POST", "GET"])
def index():
    user = current_user.get_id()
    active = Users.query.filter_by(id=user).first()
    
    if not active:
        return render_template("login.html")
    else:
        return redirect(url_for('home'))


@app.route("/home", methods=["POST", "GET"])
@login_required
def home():
    user_id = current_user.get_id()
    user = Users.query.get(user_id)

    courses_group = []
    terms = []
    user = current_user
    uid = current_user.get_id()
    year = []
    semesters_list = []

    dbconnection = engine.connect()
    terms = dbconnection.execute("select distinct term, year from course")
    if user.account_type == 'instructor':
        for term in terms:
            semester_data={}
            courses_group  = Course.query.filter_by(instructor=uid, term = term[0], year=term[1]).all()
            #print(courses_group)
            if courses_group:            
                semester_data['term'] = term[0]
                semester_data['year'] = term[1]
                courses = []
                for course in courses_group:  
                    courses.append(course.get_id())
                    semester_data['course_list'] = courses  
                # print(courses)          
            else:
                continue
            semesters_list.append(semester_data)

        if not terms:
            dbconnection.close()
            return render_template("inst_home.html", current_user=user)
        else:
            dbconnection.close()
            return render_template("inst_home.html", current_user=user, semesters = semesters_list)

    else:
        for term in terms:
            semester_data={}
            courses_group  = Course.query.filter_by(term = term[0], year=term[1]).all()
            #print(courses_group)
            if courses_group:            
                semester_data['term'] = term[0]
                semester_data['year'] = term[1]
                courses = []  
                for course in courses_group:                          
                    courses.append(course.get_id())
                    semester_data['course_list'] = courses  
                    #print(courses)          
        
            semesters_list.append(semester_data)
            
        print(semesters_list) 
        dbconnection.close()
        return render_template("home.html", current_user=user, semesters=semesters_list) 


# this checks db for existing username before returning
@app.route("/register", methods=["POST", "GET"])
def register_user():
    error = None
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

        user = Users.query.filter_by(id=add_id).first()
        email = Users.query.filter_by(email=add_email).first()
        # this still needs fixing
        # cc_emails = Users.query(email).filter_by(account_type='admin' or 'root').all()
        if user:
            error = "Employee ID is already registered"
            return render_template('register.html', error=error)
            # will remove auto commit later. using for testing currently
        elif email:
            error = "This email is already registered.  Please try again."
            msg = Message('ATAS Registration Attempt', recipients=[add_email])
            msg.body = 'ATAS Registration Attempt'
            msg.html = '<p>There was an attempt to register a new account in ATAS using the email ' + \
                       add_email + ', if this was not you, make sure to secure your ATAS account'
            mail.send(msg)
            return render_template('register.html', error=error)
        else:
            if account_type == 'admin':
                # set admin when sent
                new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                new_user = Users(fname=first_name, lname=last_name, id=employee_id, email=add_email,
                                 password=new_password, account_type='admin', sec_question=question_1, answer=answer_1)
                msg = Message('ATAS Registration Sent', recipients=[add_email])
                msg.body = 'ATAS Registration Sent'
                msg.html = '<p>Thank you for registering a new account in ATAS using ' + \
                           add_email + '. We will notify you when your account is ready to use'
                mail.send(msg)
                db.session.add(new_user)
                db.session.commit()
                message = 'Registration sent'
                return render_template('login.html')
            else:
                # set admin to 0
                new_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                new_user = Users(fname=first_name, lname=last_name, id=employee_id, email=add_email,
                                 password=new_password, account_type='instructor', sec_question=question_1,
                                 answer=answer_1)
                new_instructor = Instructor(inst_id=employee_id, fname=first_name, lname=last_name)
                #msg = Message('ATAS Registration Sent', recipients=[add_email], cc=[cc_emails])
                msg = Message('ATAS Registration Sent', recipients=[add_email])
                msg.body = 'ATAS Registration Sent'
                msg.html = '<p>Thank you for registering a new account in ATAS using ' + \
                           add_email + '. We will notify you when your account is ready to use'
                mail.send(msg)
                message = 'Registration sent'
                db.session.add(new_user)
                db.session.add(new_instructor)
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


# INSTRUCTORS CLASS
class Instructor(db.Model):
    inst_id = db.Column("id", db.Integer, primary_key=True, autoincrement=False)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, inst_id, fname, lname):
        self.inst_id = inst_id
        self.fname = fname
        self.lname = lname


@app.route('/instructors', methods=['GET'])
#@login_required
def get_instructors():
    instructors = Instructor.query.all()
    results = []

    for instructor in instructors:
        instructor_data = {}
        instructor_data['instructor_id'] = instructor.inst_id
        instructor_data['first_name'] = instructor.fname
        instructor_data['last_name'] = instructor.lname
        results.append(instructor_data)

    return jsonify(results)


@app.route('/instructors/<int:instructor_id>', methods=['GET'])
#@login_required
def get_one_instructor(instructor_id):
    instructor = Instructor.query.get(instructor_id)
    results = []
    instructor_data = {}
    instructor_data['instructor_id'] = instructor.inst_id
    instructor_data['first_name'] = instructor.fname
    instructor_data['last_name'] = instructor.lname
    results.append(instructor_data)

    return jsonify(results)


@app.route('/instructors/<instructor_id>', methods=['POST', 'GET'])
#@login_required
def update_instructors(instructor_id):
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


@app.route('/instructors', methods=['PUT', 'GET'])
#@login_required
def add_instructor():
    if request.method == 'PUT':
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
                instructor_data={}
                result =[]
                instructor_data['first'] = fname
                instructor_data['last'] = lname
                instructor_data['id'] = id
                result.append(instructor_data)
                print (result)
            dbconnection = engine.connect()                
            statement = f"INSERT INTO instructor(id, fname, lname) VALUES ({id}, '{fname}','{lname}');"
            print (statement)
            dbconnection.execute(statement)
            dbconnection.close()
            return redirect(url_for('get_instructors')) 


@app.route('/instructors/<instructor_id>', methods=['DELETE', 'GET'])
#@login_required
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


# STUDENT CLASS
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def __init__(self, student_id, fname, lname):
        self.fname = fname
        self.lname = lname
        self.stude_id = student_id


@app.route('/students', methods=['GET'])
#@login_required
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


@app.route('/students/<int:student_id>', methods=['GET'])
#@login_required
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


@app.route('/students/<student_id>', methods=['GET', 'POST'])
#@login_required
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
            #return redirect(url_for('home'))
            return redirect(url_for('get_all_students'))
        except:
            flash('Update failed!')
            return redirect(url_for('get_all_courses'))

    #return render_template('/home')

    return redirect(url_for('get_all_students'))


@app.route('/students', methods=['GET', 'PUT'])
#@login_required
def add_students():
    if request.method == 'PUT':
        try:
            # get course to update by ID save in var
            student = Student.query.get(request.form['id'])
        except:
            print("EXCEPTION ERROR")
            return redirect(url_for('get_all_students'))
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
                student_data={}
                result =[]
                student_data['first'] = fname
                student_data['last'] = lname
                student_data['id'] = student_id
                result.append(student_data)
                print (result)
            print("work you stupid thing")
            dbconnection = engine.connect()                
            statement = f"INSERT INTO student(student_id, fname, lname) VALUES ({student_id}, '{fname}','{lname}');"
            print (statement)
            dbconnection.execute(statement)
            dbconnection.close()
            return redirect(url_for('get_all_students'))
      


@app.route('/students/<int:student_id>', methods=['GET', 'DELETE'])
#@login_required
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


@app.route('/courses', methods=['GET'])
#@login_required
def get_all_courses():
    #user_id = Users.get_id(current_user)
    #user = Users.query.get(user_id)
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
        course_info['course_id'] = course.id
        results.append(course_info)

   # if user.account_type == 'instructor':
      # return redirect(url_for('get_instructor_courses', instructor_id = user_id))
    
    print(results)
    return jsonify(results)
    return render_template('courses.html', courses=results)


@app.route('/courses/<int:course_id>', methods=['GET'])
#@login_required
def get_one_course(course_id):
    #user_id = Users.get_id(current_user)
    #user = Users.query.get(user_id)
    course = Course.query.get(course_id)
    results = []
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
    results.append(course_info)

   # if user.account_type == 'instructor':
      # return redirect(url_for('get_instructor_courses', instructor_id = user_id))
    
    print(results)
    return jsonify(results)
    return render_template('courses.html', courses=results)


# gets all courses for specific instructor id
@app.route('/courses/inst/<int:instructor_id>', methods=['GET'])
#@login_required
def get_instructor_courses(instructor_id):
    print('GET_INSTRUCTOR_COURSES')
    courses = Course.query.filter_by(instructor=instructor_id).all()
    print(courses)
    results = []

    if request.method == "GET":
        if not courses:
            print('no courses hit')
            results = "No courses assigned"
        else:
            for course in courses:
                course_info = {}
                course_info['course_id'] = course.id
                course_info['course_name'] = course.course_name
                course_info['term'] = course.term
                course_info['year'] = course.year
                course_info['course_department'] = course.department
                course_info['course_number'] = course.course_number
                course_info['section'] = course.section
                results.append(course_info)

        return jsonify(results)
        return render_template("inst_courses.html", semesters=results)

    else:
        return render_template("inst_courses.html")


@app.route('/courses/<int:course_id>', methods=['GET', 'POST'])
#@login_required
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
            #return render_template('/home')
        
        print('Course Updated!')
        return redirect(url_for('get_all_courses'))
        #return redirect(url_for('home'))


@app.route('/courses', methods=['GET', 'PUT'])
#@login_required
def add_courses():
    if request.method == 'PUT':
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
            print('Course already exists in selected semester/year!')
            return redirect(url_for('home'))

        else:
            # commit changes to db
            print("ADD NEW COURSE TO DB")
            dbconnection = engine.connect()                
            statement = f"INSERT INTO course(course_name, term, year, department, course_number, section, instructor)\
                    VALUES ('{new_course.course_name}','{new_course.term}', '{new_course.year}', \
                        '{new_course.department}','{new_course.course_number}','{new_course.section}', {new_course.instructor} );"
            print (statement)
            dbconnection.execute(statement)
            dbconnection.close()
            print("course added!")
            return redirect(url_for('get_all_courses'))
            #return redirect(url_for('home'))

    return ("course add failed")


@app.route('/courses/<int:course_id>', methods=['GET', 'DELETE'])
#@login_required
def delete_courses(course_id):
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


# THIS IS STATIC -- CANNOT BE UPDATED WITHOUT ACCESS DIRECTLY TO DB
@app.route("/outcomes", methods=["GET"])
@login_required
def outcomes():
    courses_group = []
    terms = []
    user = current_user
    uid = current_user.get_id()
    year = []
    semesters_list = []
    outcomes = Outcomes.query.all()

    results = []
    courses = Course.query.all()
    for outcome in outcomes:
        outcome_data = {}
        outcome_data['so_name'] = outcome.so_name
        outcome_data['so_desc'] = outcome.so_desc
        results.append(outcome_data)
    
    dbconnection = engine.connect()
    terms = dbconnection.execute("select distinct term, year from course")

    if user.account_type =='instructor':
        for term in terms:
            semester_data={}
            courses_group  = Course.query.filter_by(instructor=uid, term = term[0], year=term[1]).all()
            if courses_group:            
                semester_data['term'] = term[0]
                semester_data['year'] = term[1]
                courses = []     
                for course in courses_group:                       
                    courses.append(course.get_id())
                    semester_data['course_list'] = courses  
                # print(courses)          
            else:
                continue      
            semesters_list.append(semester_data)
            print(semesters_list)       
        dbconnection.close()
        return render_template('inst_outcomes.html', outcomes=results, semesters=semesters_list)
    else:
        for term in terms:
            semester_data={}
            courses_group  = Course.query.filter_by(term = term[0], year=term[1]).all()
            print(courses_group)
            if courses_group:            
                semester_data['term'] = term[0]
                semester_data['year'] = term[1]
                courses = []
                for course in courses_group:                            
                    courses.append(course.get_id())
                    semester_data['course_list'] = courses  
                # print(courses)          
            else:
                continue
        
            semesters_list.append(semester_data)
            print(semesters_list) 

        dbconnection.close()
        return render_template('outcomes.html', outcomes=results, semesters = semesters_list)


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
#@login_required
def get_all_swp():
    swps = Assignments.query.all()

    results = []

    for swp in swps:
        swp_data = {}
        course = Course.query.get(swp.course_id)
        swp_data['swp_id'] = swp.swp_id
        swp_data['swp_name'] = swp.swp_name
        swp_data['course_id'] = course.id
        swp_data['course name'] = course.course_name
        results.append(swp_data)

    return jsonify(results)


@app.route('/swp/<int:swp_id>', methods=["GET"])
#@login_required
def get_one_swp(swp_id):
    swp = Assignments.query.get(swp_id)

    results = []
    swp_data = {}
    swp_data['swp_id'] = swp.swp_id
    swp_data['swp_name'] = swp.swp_name
    swp_data['course_id'] = swp.course_id
    course = Course.query.get(swp.course_id)
    swp_data['course name'] = course.course_name
    results.append(swp_data)

    return jsonify(results)


# THIS GETS WORK PRODUCT FOR SPECIFIC COURSE
@app.route('/swp/course/<int:course_id>', methods=["GET"])
#@login_required
def get_course_swps(course_id):
    swps = Assignments.query.filter_by(course_id=course_id).all()

    results = []

    for swp in swps:
        swp_data = {}
        course = Course.query.get(swp.course_id)
        swp_data['swp_id'] = swp.swp_id
        swp_data['swp_name'] = swp.swp_name
        swp_data['course_id'] = course.id
        swp_data['course name'] = course.course_name
        results.append(swp_data)

    return jsonify(results)


@app.route('/swp/<int:swp_id>', methods=['GET', 'POST'])
#@login_required
def update_swp(swp_id):
    if request.method == 'POST':
        swp = Assignments.query.get(swp_id)
        print(swp)
        if swp:
            #swp.course_id = request.form('course_id')            
            course_id = request.form['course_id']
            name = request.form['swp_name']
            name = name.upper()
            swp.swp_name = name
            db.session.commit()
            print("Student Work Product succesfully updated!")
            return redirect(url_for('get_all_swp'))
            #return redirect(url_for('home'))
        else:
            return "Error:  Student Work Product not found"
            #return redirect(url_for('home'))
    return redirect(url_for('get_all_swp'))


@app.route('/swp', methods=['GET', 'PUT'])
#@login_required
def add_swp():
    if request.method == 'PUT':
        # instantiate new work product info based on form input
        course_id = request.form['course_id']
        swp_name = request.form['swp_name']
        print(swp_name)
        print(course_id)
        swp_name = swp_name.upper()
        new_swp = Assignments(course_id, swp_name)
        # check database for existing  overlap
        existing_swp = Assignments.query.filter_by(swp_name=swp_name,course_id=course_id).all()

        # return error if existing info returns true -- otherwise add course
        if existing_swp:
            return("Student Work Product already exists in current course.  Please pick a unique name")
            return redirect(url_for('home'))
        else:
            # commit changes to db
            dbconnection = engine.connect()                
            statement = f"INSERT INTO Assignments(course_id, swp_name)\
                    VALUES ({new_swp.course_id},'{new_swp.swp_name}');"
            print (statement)
            dbconnection.execute(statement)
            dbconnection.close()
            print("SWP added!")
            return redirect(url_for('get_all_swp'))

    else:
        return render_template('/home')

    return redirect(url_for('home'))


@app.route('/swp/<swp_id>', methods=['GET', 'DELETE'])
#@login_required
def delete_swp(swp_id):
    if request.method == 'DELETE':
        swp = Assignments.query.get(swp_id)
        db.session.delete(swp)
        db.session.commit()

        print("Work Product Deleted")

    return redirect(url_for('get_all_swp'))
    return redirect(url_for('home'))


# ATTEMPTS CLASS
class Attempts(db.Model):
    attempt_id = db.Column("id", db.Integer, primary_key=True)
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    so_id = db.Column(db.Integer, db.ForeignKey('outcomes.so_id'))

    def __init__(self, swp_id, so_id):
        self.swp_id = swp_id
        self.so_id = so_id


# GET ALL ATTEMPTS -- UNION OF SWP AND SO
@app.route('/attempts', methods=["GET"])
@login_required
def get_all_attempts():
    attempts = Attempts.query.all()

    results = []

    for attempt in attempts:
        attempt_data = {}
        swp = Assignments.query.get(attempt.swp_id)
        so = Outcomes.query.get(attempt.so_id)
        course = Course.query.get(swp.course_id)

        attempt_data['attempt_id'] = attempt.attempt_id
        attempt_data['course_name'] = course.course_name
        attempt_data['swp'] = swp.swp_name
        attempt_data['so'] = so.so_name
        results.append(attempt_data)

    return jsonify(results)


@app.route('/attempts', methods=['GET', 'POST'])
@login_required
def update_attempts():
    if request.method == 'POST':
        try:
            attempt = Attempts.query.get(request.form('attempt_id'))
            attempt.swp_id = request.form('swp_id')
            attempt.so_id = request.form('so_id')
            db.session.commit()
            flash("Attempt record succesfully updated!")
            return redirect(url_for('home'))
        except:
            flash("Error:  Values not found")
            return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/attempts', methods=['GET', 'PUT'])
@login_required
def add_attempts():
    if request.method == 'PUT':
        try:
            # IF attempt EXISTS RETURN INVALID ENTRY
            new_attempt = Attempts()

            # instantiate new  info based on form input
            new_attempt.swp_id = request.form['swp_id']
            new_attempt.so_id = request.form['so_id']

            # check database for existing course overlap
            existing_attempt = Attempts.query.filter_by(
                swp_id=new_attempt.swp_id,
                so_id=new_attempt.so_id)

            # return error if existing course returns true otherwise add course
            if existing_attempt:
                flash('Info already exists!')
                return redirect(url_for('home'))

            else:
                # commit changes to db
                session.add(new_attempt)
                db.session.commit()
                flash('New SO/SWP combination Added!')
                return redirect(url_for('home'))
        # IF TRY FAILS -- RETURN FAILURE MESSAGE
        except:
            flash('Add failed!')
            return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/attempts/<attempt_id>', methods=['GET', 'DELETE'])
@login_required
def delete_attempts(attempt_id):
    if request.method == 'DELETE':
        try:
            attempt = Attempts.query.get(attempt_id)
            db.session.delete(attempt)
            db.commit()

            flash(" Deleted")
        except:
            flash("Error:  Delete Unsuccessful")

    return redirect(url_for('home'))


# ENROLLED CLASS
class Enrolled(db.Model):
    enrolled_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id


# GET ENROLLMENTS FOR A SPECIFIC COURSE
@app.route('/enrolled/<int:course_id>', methods=['GET'])
@login_required
def get_enrolled(course_id):
    enrolled = Enrolled.query.filter_by(course_id=course_id)
    results_list = []
    swp_list = []
    user = current_user
    swps = Assignments.query.filter_by(course_id=course_id).all()
    for swp in swps:
        swp_data = {}
        swp_name = swp.swp_name
        swp_data['swp_name']= swp_name
        swp_data['swp_id'] = swp.swp_id
        swp_list.append(swp_data)              

    for enroll in enrolled:
        enrollment_data = {} 
        student_id = enroll.student_id
        student = Student.query.get(student_id)
        results = Results.query.filter_by(student_id = student_id).all()
        #print(results)
        if not results:
            enrollment_data['swp_id'] = None
            enrollment_data['swp_name'] = 'Test'
            enrollment_data['score'] = None
        else:
            enrollment_data['swp_id'] = results.swp_id
            swp = Assignments.query.filter_by(swp_id = results.swp_id).first()
            enrollment_data['swp_name'] = swp.swp_name
            enrollment_data['score'] = results.value
        if student:
            enrollment_data['student_id'] = student.student_id
            enrollment_data['student_first'] = student.fname
            enrollment_data['student_last'] = student.lname

        enrollment_data['course_id'] = enroll.course_id
        results_list.append(enrollment_data)
    
    sorted_results = sorted(results_list, key=lambda i:i['student_last'])
    user_id = current_user.get_id()
    user = Users.query.get(user_id)
    if user.account_type == 'instructor':
        courses = Course.query.filter_by(instructor=user.id).all()
        return render_template('inst_courses.html', enrolled=sorted_results, courses=courses, swps=swp_list)
    else:
        courses = Course.query.all()
        return render_template('courses.html', enrolled=sorted_results, courses=courses)


# TODO -- UPDATE ENROLLMENTS
@app.route('/enrolled', methods=['GET', 'POST'])
@login_required
def update_enrolled():
    return ""


@app.route('/enrolled', methods=['GET', 'PUT'])
@login_required
def add_enrolled():
    if request.method == 'PUT':
        try:
            # IF emrollment EXISTS RETURN INVALID ENTRY
            new_enrollment = Enrolled()

            # instantiate new  info based on form input
            new_enrollment.student_id = request.form['student_id']
            new_enrollment.course_id = request.form['course_id']

            # check database for existing enrollment overlap
            existing_enrollment = Enrolled.query.filter_by(
                student_id=new_enrollment.student_id,
                course_id=new_enrollment.course_id)

            # return error if existing enrollment returns true -- otherwise add enrollment
            if existing_enrollment:
                flash('Student already enrolled in this course!')
                return redirect(url_for('home'))

            else:
                # commit changes to db
                session.add(new_enrollment)
                db.session.commit()
                flash('Student successfully enrolled in course!')
                return redirect(url_for('home'))
        # IF TRY FAILS -- RETURN FAILURE MESSAGE
        except:
            flash('Enrollment failed!')
            return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/enrolled/<enrolled_id>', methods=['GET', 'DELETE'])
@login_required
def delete_enrolled(enrolled_id):
    if request.method == 'DELETE':
        try:
            enrollment = Enrolled.query.get(enrolled_id)
            db.session.delete(enrollment)
            db.commit()

            flash("Enrollment Deleted")
        except:
            flash("Error:  Delete Unsuccessful")

    return redirect(url_for('home'))


# RESULTS CLASS
class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    swp_id = db.Column(db.Integer, db.ForeignKey('assignments.swp_id'))
    value = db.Column(db.Integer)

    def __init__(self, student_id, swp_id, value):
        self.student_id = student_id
        self.swp_id = swp_id
        self.value = value


@app.route('/results', methods=['GET'])
@login_required
def get_results():
    results = Results.query.all()
    output = []

    for result in results:
        result_data = {}
        student = Student.query.get(result.student_id)
        swp = Assignments.query.get(results.swp_id)

        result_data['result id'] = result.id
        result_data['student first'] = student.fname
        result_data['student last'] = student.lname
        result_data['swp name'] = swp.swp_name
        result_data['value'] = results.value

        output.append(result_data)
    print(output)
    return jsonify(output)


# TODO  -- complete endpoint
@app.route('/results', methods=['GET', 'POST'])
@login_required
def update_results():
    if request.method == "POST":
        return ""

    return ""


# TODO -- complete put results endpoint
@app.route('/results', methods=['PUT'])
@login_required
def add_results():
    return ""


@app.route('/results/<result_id>)', methods=['GET', 'DELETE'])
@login_required
def delete_results(result_id):
    if request.method == "DELETE":
        try:
            result = Results.query.get(result_id)
            db.session.delete(result)
            db.commit()

            flash("Result Deleted")
        except:
            flash("Error:  Delete Unsuccessful")

    return redirect(url_for('home'))





if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
