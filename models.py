from flask import flask
from flask_sqlalchemy import SQLAlchemy

class Instructor(db.model){
    id = db.column(db.Integer, primary_key=true)
    fname = db.column(db.String(255))
    lname = db.column(db.String(255))
    
    
}


class Student(db.model){
    id = db.column(db.Integer, primary_key=True)
    fname = db.column(db.String(255))
    lname = db.column(db.String(255))

}


class Course(db.model){
    course_id = db.column(db.Integer, primary_key=true)
    course_name = db.column(db.String(255))
    term = db.column(db.String(11))
    year = db.column(db.String(4))
    department = db.column(db.String(5))
    course_number = db.column(db.Integer)
    section = db.column(db.String(5))
    instructor = db.column(db.Integer, db.ForeignKey('instructor.id'))

}


class SO(db.model){
    so_id = db.column(db.Integer, primary_key=true)
    so_name = db.column(db.String(4))
    so_desc = db.column(db.String(256))

}


class SWP(db.model){
    swp_id = db.column(db.Integer,primary_key=true)
    course_id  = db.column(db.Integer, db.ForeignKey('course.course_id'))
    swp_name = db.column(db.String(255))

}


class Attempts(db.model){
    attempt_id = db.column(db.Integer, primary_key=true)
    swp_id = db.column(db.Integer, db.ForeignKey('swp.swp_id'))
    so_id = db.column(db.Integer, db.ForeignKey('so.so_id'))

}


class Enrolled(db.model){
    id = db.column(db.Integer, primary_key=true)
    student_id= db.column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.column(db.Integer, db.ForeignKey('course.course_id'))

}


class Results(db.model){
    id = db.column(db.Integer, primary_key=true)
    student_id = db.column(db.Integer, db.ForeignKey('student.id'))
    attempt_id = db.column(db.Integer, db.ForeignKey('attempts.attempt_id'))

}