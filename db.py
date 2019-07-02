#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Modelo de dados das provas"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import os
import sys

fileName = 'dbpass.txt'
if not os.path.isfile(fileName):
    print('Não encontrato:', fileName)
    sys.exit(1)

dbpass = open(fileName).readlines()[0][:-1]
engine = create_engine(dbpass) 
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key = True)
    email = Column(String)
    project_group = Column(String)
    academic_register = Column(Integer)
    student_type = Column(String)
    current_status = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    mediator_class_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    type_field = Column('type', String)
    date_entrance_exam = Column(DateTime)
    date_conclusion = Column(DateTime)
    student_card_photo_updated_at = Column(DateTime)
    holder_data = Column(JSON)
    internship_data = Column(JSON)

    user = relationship('Users', backref='users')

    activities = relationship('ActivityRecords')

    def __repr__(self):
        return str(self.academic_register) + ' - ' + self.user.name

class CurricularActivities(Base):
    __tablename__ = 'curricular_activities'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    code = Column(String)
    objective = Column(String)
    syllabus = Column(String)
    credits_lecture = Column(Integer)
    credits_practical = Column(Integer)
    credits_self_study = Column(Integer)
    workload = Column(Integer)
    duration_months = Column(Integer)
    educational_institution = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    activity_type = Column(String)
    comments = Column(String)
    link_document = Column(String)
    in_lms = Column(Boolean)
    in_academic_record = Column(Boolean)
    hide_grades_and_attendances = Column(Boolean)
    bibliography = Column(String)
    programmatic_content = Column(String)
    prerequisite = Column(String)
    evaluation_criteria = Column(String)
    responsible_teacher = Column(String)
    parent_id = Column(Integer)
    responsible_teachers = Column(JSON)

    def __repr__(self):
        return self.code + ' - ' + self.name


class ActivityRecords(Base):
    __tablename__ = 'activity_records'

    id = Column(Integer, primary_key = True)
    date_begin = Column(DateTime)
    date_conclusion = Column(DateTime)
    date_deregistration = Column(DateTime)
    grade_total = Column(Float)
    grade_portfolio = Column(Float)
    grade_project = Column(Float)
    grade_test = Column(Float)
    grade_modified_by = Column(String)
    grade_modified_by_ip = Column(String)
    grade_modified_when = Column(DateTime)
    attendance_total = Column(Float)
    attendance_ava = Column(Float)
    attendance_terf = Column(Float)
    attendance_lecture = Column(Float)
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Integer)
    validated = Column(Boolean)
    activity_offer_id = Column(Integer)
    lms_submissions_data = Column(JSON)

    curricular_activity = relationship('CurricularActivities', backref = 'curricular_activities')
    student = relationship('Students', backref = 'students')


    def __repr__(self):
        return str(self.student_id) + ' - ' + self.curricular_activity.name

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    personal_email = Column(String)
    rg = Column(String)
    issuing_entity = Column(String)
    birth_date = Column(DateTime)
    citizenship = Column(String)
    place_of_birth = Column(String)
    phone = Column(String)
    mobile = Column(String)
    gender = Column(String)
    cpf = Column(String)
    marital_status = Column(String)
    address_street = Column(String)
    address_number = Column(String)
    address_complement = Column(String)
    address_neighborhood = Column(String)
    address_city = Column(String)
    address_state = Column(String)
    address_zip = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    race_ethnicity = Column(String)
    disability = Column(Boolean)
    disability_details = Column(String)
    organ_donor = Column(Boolean)
    blood_type = Column(String)
    military_certificate = Column(String)
    military_certificate_issuing_entity = Column(String)
    voter_registration = Column(String)
    voter_section = Column(String)
    voter_zone = Column(String)
    father_name = Column(String)
    mother_name = Column(String)
    high_school_name = Column(String)
    high_school_city = Column(String)
    high_school_state = Column(String)
    high_school_year_conclusion = Column(String)
    place_of_birth_state = Column(String)
    issuing_date = Column(DateTime)
    blood_type_rh = Column(String)
    military_certificate_issuing_date = Column(DateTime)
    avatar_url = Column(String)
    lms_id = Column(Integer)
    place_of_birth_country = Column(String)
    passport_rne = Column(String)
    vacancies_reservation = Column(String)
    birth_name = Column(String)
    ru = Column(Integer)
    secondary_emails_data = Column(JSON)
    secondary_phones_data = Column(JSON)
    scholar_data = Column(JSON)
    bank_data = Column(JSON)
    documents_data = Column(JSON)

    def __repr__(self):
        return self.name

class Courses(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    code = Column(String)
    duration_semesters = Column(Integer)
    course_type = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    parent_id = Column(Integer)
    level = Column(String)

    def __repr__(self):
        return self.name


class CourseCatalogs(Base):
    __tablename__ = 'course_catalogs'

    id = Column(Integer, primary_key = True)
    code = Column(String)
    workload_compulsory = Column(Integer)
    workload_optional = Column(Integer)
    optional_groups = Column(String)
    course_id = Column(Integer, ForeignKey('courses.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    duration_semesters = Column(Integer)
    regulation = Column(String)

    def __repr__(self):
        return self.code


class CourseCurriculums(Base):
    __tablename__ = 'course_curriculums'

    id = Column(Integer, primary_key = True)
    course_catalog_id = Column(Integer, ForeignKey('course_catalogs.id'))
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    semester = Column(Integer)
    period = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    course_catalog = relationship('CourseCatalogs', backref = 'course_catalogs')
    curricular_activity = relationship('CurricularActivities', backref = 'curricular_activities')

    def __repr__(self):
        return self.course_catalog.code


class CourseActivities(Base):
    __tablename__ = 'course_activities'

    id = Column(Integer, primary_key = True)
    activity_type = Column(String)
    course_catalog_id = Column(Integer, ForeignKey('course_catalogs.id'))
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    course_catalog = relationship('CourseCatalogs', backref = 'course_catalogs')
    curricular_activity = relationship('CurricularActivities', backref = 'curricular_activities')

    def __repr__(self):
        return self.course_catalog.code


class ActivityTestQuestions(Base):
    __tablename__ = 'activity_test_questions'

    id = Column(Integer, primary_key = True)
    question_type = Column(String)
    number = Column(Integer)
    weight = Column(Float)
    activity_test_id = Column(Integer, ForeignKey('activity_tests.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    annulled = Column(Boolean)

    activity_test = relationship('ActivityTests', backref = 'activity_tests')

    def __repr__(self):
        return str(self.number) + ' - ' + self.question_type


class ActivityTests(Base):
    __tablename__ = 'activity_tests'

    id = Column(Integer, primary_key = True)
    code = Column(String)
    total_pages = Column(Integer)
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    curricular_activity = relationship('CurricularActivities', backref='curricular_activities')

    def __repr__(self):
        return self.curricular_activity.code + ' - ' + self.curricular_activity.name + ' - ' + self.code + '(' + str(self.total_pages) + ')'



print('**Students')
last = None
for instance in session.query(Students)[0:10]:
    print(instance)
    last = instance

for activity in instance.activities:
    print(activity.curricular_activity)

# print('**ActivityRecords')
# for instance in session.query(ActivityRecords)[0:10]:
#     print(instance)

print('**CurricularActivities')
for instance in session.query(CurricularActivities)[0:10]:
    print(instance)

# print('**Users')
# for instance in session.query(Users)[0:10]:
#     print(instance)

# print('**Courses')
# for instance in session.query(Courses)[0:10]:
#     print(instance)

top10 = [CourseCatalogs, CourseCurriculums, ]