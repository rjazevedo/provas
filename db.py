#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Modelo de dados do SGA"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import os
import sys

fileName = os.path.join(os.path.dirname(sys.argv[0]), 'dbpass.txt')
if not os.path.isfile(fileName):
    print('Não encontrato:', fileName)
    sys.exit(1)

dbpass = open(fileName).readlines()[0][:-1]
# print(dbpass)
engine = create_engine(dbpass, pool_size=10, max_overflow=20)
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

    user = relationship('Users', uselist = False)
    activity_records = relationship('ActivityRecords')

    def __repr__(self):
        return str(self.academic_register) + ' - ' + self.user.name

    def Historico(self):
        for activity in self.activity_records:
            print(activity)

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

    activity_offers = relationship('ActivityOffers')

    def __repr__(self):
        return self.code + ' - ' + self.name

# Anexos
class Attachments(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key = True)
    attach_reference_id = Column(Integer) # activity_record_submissions.id quando anexo é folha de resposta
    attach_reference_type = Column(String)
    attach_path = Column(String)
    attach_type = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    sheets_data = Column(JSON)

    def __repr__(self):
        return str(self.id) + ' - ' + self.attach_reference_type + ' - ' + self.attach_type

# Registro de Disciplinas
class ActivityRecords(Base):
    __tablename__ = 'activity_records'

    # 0 = matriculado
    # 1 = aguardando nota (caiu em desuso nesse 1º semestre/2019)
    # 2 = nota recebida (em desuso)
    # 3 = aprovado
    # 4 = reprovado
    # 5 = trancado
    # 6 = aproveitamento de estudo
    # 7 = exame de proficiência (basicamente, Aproveitamento de Estudo para disciplinas de Inglês)

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
    activity_offer_id = Column(Integer, ForeignKey('activity_offers.id'))
    lms_submissions_data = Column(JSON)

    curricular_activity = relationship('CurricularActivities', uselist = False)
    student = relationship('Students', uselist = False)
    activity_offer = relationship('ActivityOffers', uselist = False)

    def __repr__(self):
        return str(self.curricular_activity.code) + ' - ' + self.curricular_activity.name + ' - ' + str(self.grade_total) + ' - ' + str(self.status)

# Submissões de Provas
class ActivityRecordSubmissions(Base):
    __tablename__ = 'activity_record_submissions'

    id = Column(Integer, primary_key = True)
    activity_record_id = Column(Integer, ForeignKey('activity_records.id'))
    submission_type = Column(String)
    grade = Column(Float)
    link_document = Column(String)
    absent = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    template = Column(String)
    complementary_data = Column(JSON)
    annulled = Column(Boolean)
    activity_test_id = Column(Integer, ForeignKey('activity_tests.id'))

    activity_record = relationship('ActivityRecords', uselist = False)
    activity_test = relationship('ActivityTests', uselist = False)
    corrections = relationship('ActivityRecordSubmissionCorrections', back_populates='activity_record_submission')
    correctors = relationship('ActivityRecordSubmissionCorrectors', back_populates='activity_record_submission')

    def __repr__(self):
        return self.submission_type + ' - ' + str(self.grade)

# Correções das questões
class ActivityRecordSubmissionCorrections(Base):
    __tablename__ = 'activity_record_submission_corrections'

    id = Column(Integer, primary_key = True)
    grade = Column(String)
    corrector_data = Column(JSON)
    activity_record_submission_id = Column(Integer, ForeignKey('activity_record_submissions.id'))
    activity_test_question_id = Column(Integer, ForeignKey('activity_test_questions.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    activity_record_submission = relationship('ActivityRecordSubmissions', back_populates='corrections', uselist = False)
    activity_test_question = relationship('ActivityTestQuestions', uselist = False)
    
    def __repr__(self):
        return '{0} - {1} - {2} - Q{3}'.format(self.activity_record_submission.activity_record.curricular_activity.code, 
                                        self.activity_record_submission.activity_record.student.academic_register, 
                                        self.activity_test_question.activity_test.code,
                                        self.activity_test_question.number)

    
# Corretores das provas
class ActivityRecordSubmissionCorrectors(Base):
    __tablename__ = 'activity_record_submission_correctors'

    id = Column(Integer, primary_key = True)
    activity_record_submission_id = Column(Integer, ForeignKey('activity_record_submissions.id'))
    internal_user_id = Column(Integer, ForeignKey('internal_users.id'))
    role = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    activity_record_submission = relationship('ActivityRecordSubmissions', back_populates='correctors', uselist = False)
    internal_user = relationship('InternalUsers', uselist = False)

    def __repr__(self):
        return '{0} - {1} - {2}'.format(self.activity_record_submission.activity_record.curricular_activity.code, 
                                        self.activity_record_submission.activity_record.student.academic_register,
                                        self.internal_user.email)

# Oferta de Disciplina
class ActivityOffers(Base):
    __tablename__ = 'activity_offers'

    id = Column(Integer, primary_key = True)
    ava_id = Column(Integer)
    ava_sis = Column(String)
    offer_date = Column(String)
    offer_type = Column(Integer)
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Integer)
    calendar_id = Column(Integer)
    status_date = Column(DateTime)

    curricular_activity = relationship('CurricularActivities', uselist = False)
    activity_records = relationship('ActivityRecords')

    def __repr__(self):
        return self.offer_date + ' - ' + str(self.curricular_activity)

# Questões das Provas
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

    activity_test = relationship('ActivityTests', back_populates = 'questions')

    def __repr__(self):
        return str(self.number) + ' - ' + self.question_type

# Provas
class ActivityTests(Base):
    __tablename__ = 'activity_tests'

    id = Column(Integer, primary_key = True)
    code = Column(String)
    total_pages = Column(Integer)
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    curricular_activity = relationship('CurricularActivities', uselist = False)
    questions = relationship('ActivityTestQuestions', back_populates='activity_test')

    def __repr__(self):
        return '{0} - {1} - {2} ({3})'.format(self.curricular_activity.code, 
                                              self.curricular_activity.name,
                                              self.code,
                                              str(self.total_pages))

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

class InternalUsers(Base):
    __tablename__ = 'internal_users'

    id = Column(Integer, primary_key = True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(String)
    role = Column(String)

    # Correções a fazer -> Apontando para ActivityRecordSubmissionCorrectors
    tasks = relationship('ActivityRecordSubmissionCorrectors', back_populates='internal_user')

    def __repr__(self):
        return self.email + ' - ' + self.role

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

    catalogs = relationship('CourseCatalogs')

    def __repr__(self):
        return self.code + ' - ' + self.name

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

    curriculums = relationship('CourseCurriculums', back_populates = 'course_catalog')
    activities = relationship('CourseActivities', back_populates = 'course_catalog')
    course = relationship('Courses', uselist = False)

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

    course_catalog = relationship('CourseCatalogs', back_populates = 'curriculums')
    curricular_activity = relationship('CurricularActivities', uselist = False)

    def __repr__(self):
        return str(self.curricular_activity) + ' - ' + str(self.semester) + ' - ' + str(self.period)
 
class CourseActivities(Base):
    __tablename__ = 'course_activities'

    id = Column(Integer, primary_key = True)
    activity_type = Column(String)
    course_catalog_id = Column(Integer, ForeignKey('course_catalogs.id'))
    curricular_activity_id = Column(Integer, ForeignKey('curricular_activities.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    course_catalog = relationship('CourseCatalogs', back_populates = 'activities')
    curricular_activity = relationship('CurricularActivities')

    def __repr__(self):
        return self.course_catalog.code

class AcademicRecords(Base):
    __tablename__ = 'academic_records'
    
    id = Column(Integer, primary_key=True)
    date_begin = Column(DateTime)
    date_conclusion = Column(DateTime)
    date_graduation = Column(DateTime)
    date_complete_withdrawal = Column(DateTime)
    entrance_exam_grade = Column(Float)
    entrance_exam_classification = Column(Integer)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_catalog_id = Column(Integer, ForeignKey('course_catalogs.id'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    course_id = Column(Integer, ForeignKey('courses.id'))
    date_deregistration = Column(DateTime)
    ingress_type = Column(String)
    class_period = Column(String)
    location_id = Column(Integer, ForeignKey('locations.id'))
    entrance_location_id = Column(Integer)
    parent_id = Column(Integer)
    calendar_id = Column(Integer)
    academic_register = Column(Integer)
    date_shipping = Column(DateTime)

    location = relationship('Locations', uselist=False)
    student = relationship('Students', uselist=False)
    course_catalog = relationship('CourseCatalogs', uselist=False)
    course = relationship('Courses', uselist=False)

    def __repr__(self):
        return str(self.course_catalog.code) + ' - ' + str(self.student.academic_register)

class Locations(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    institution = Column(String)
    address_street = Column(String)
    address_number = Column(String)
    address_complement = Column(String)
    address_neighborhood = Column(String)
    address_zip = Column(String)
    address_city = Column(String)
    email_main = Column(String)
    email_second = Column(String)
    email_third = Column(String)
    phone = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    lat = Column(Float)
    lng = Column(Float)
    address_state = Column(String)
    secretary_id = Column(Integer)
    email = Column(String)


class Calendar(Base):
    __tablename__ = 'calendars'

    id = Column(Integer, primary_key = True)
    year = Column(Integer)
    semester = Column(Integer)
    period = Column(Integer)
    date_begin = Column(DateTime)
    date_conclusion = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_entrance_period = Column(Boolean)
    calendar_type = Column(String)
    alias = Column(String)

    def __repr__(self):
        return str(self.year) + 's' + str(self.semester) + '.' + str(self.period)

# Query sobre as provas
# select *
# from activity_record_submissions ars /* submissões de prova (regular, DP, exame etc.) */
# join activity_records ar /* registros de disciplina */
# on ars.activity_record_id = ar.id
# join activity_offers ao /* ofertas de disciplina */
# on ar.activity_offer_id = ao.id
# join activity_tests at /* provas */
# on ars.activity_test_id = at.id
# join activity_test_questions atq /* questões de prova */
# on atq.activity_test_id = at.id
# join activity_record_submission_corrections arsc /* correções de questões de provas */
# on arsc.activity_record_submission_id = ars.id

