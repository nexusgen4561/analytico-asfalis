import os

import pandas as pd
import matplotlib
matplotlib.use('Agg')

from textwrap import wrap
import psycopg2
import psycopg2.extras

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask_restx import Resource, Api
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit
from email.policy import Policy
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required
from sqlalchemy import func
from werkzeug.utils import secure_filename

from apps.config import config_dict
from apps import create_app, db
from apps.home import blueprint

import cohort


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS_CSV = {'csv'}


# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )


ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:analytico@localhost/asfalisdb'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "max_overflow": 15,
    "pool_pre_ping": True,
    "pool_recycle": 60 * 60,
    "pool_size": 30,
    }
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mbvjwnkuqiwgpe:805a5e28197a2e61c2851574da8212c857e5016a2750af0bbb79710466a08e7e@ec2-35-173-91-114.compute-1.amazonaws.com:5432/dm8nvu4mj2uq0'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
sql = SQLAlchemy(app)

class Branches(sql.Model):
    __tablename__ = 'Branches'
    id = sql.Column(sql.Integer, primary_key=True)
    branch = sql.Column(sql.String(100))

    def __init__(self, branch):
        self.branch = branch

    def to_dict(self):
        return {
            'branch' : self.branch,
        }

class PCategory(sql.Model):
    __tablename__ = 'PCategories'
    id = sql.Column(sql.Integer, primary_key=True)
    pcategory = sql.Column(sql.String(100))

    def __init__(self, pcategory):
        self.pcategory = pcategory

    def to_dict(self):
        return {
            'pcategory' : self.pcategory,
        }

class PType(sql.Model):
    __tablename__ = 'PType'
    id = sql.Column(sql.Integer, primary_key=True)
    ptype = sql.Column(sql.String(100))

    def __init__(self, ptype):
        self.ptype = ptype

    def to_dict(self):
        return {
            'ptype' : self.ptype,
        }

class VehicleUse(sql.Model):
    __tablename__ = 'VUse'
    id = sql.Column(sql.Integer, primary_key=True)
    vuse = sql.Column(sql.String(100))

    def __init__(self, vuse):
        self.vuse = vuse

    def to_dict(self):
        return {
            'vuse' : self.vuse,
        }

class VehicleTransmission(sql.Model):
    __tablename__ = 'VTransmission'
    id = sql.Column(sql.Integer, primary_key=True)
    transmission = sql.Column(sql.String(100))

    transmission = sql.Column(sql.String(100))

    def __init__(self, transmission):
        self.transmission = transmission

    def to_dict(self):
        return {
            'transmission' : self.transmission,
        }
        
class VehicleFuel(sql.Model):
    __tablename__ = 'VFuel'
    id = sql.Column(sql.Integer, primary_key=True)
    fuel = sql.Column(sql.String(100))

    def __init__(self, fuel):
        self.fuel = fuel

    def to_dict(self):
        return {
            'fuel' : self.fuel,
        }





class Policyholders(sql.Model):
    __tablename__ = 'Policyholders'
    id = sql.Column(sql.Integer, primary_key=True)
    endate = sql.Column(sql.Date)
    agcode1 = sql.Column(sql.String(100),unique=True)
    line = sql.Column(sql.String(100))
    branch = sql.Column(sql.String(100))
    idate = sql.Column(sql.Date)
    edate = sql.Column(sql.Date)
    pcategory = sql.Column(sql.String(100))
    ptype = sql.Column(sql.String(100))
    vuse = sql.Column(sql.String(100))
    model = sql.Column(sql.String(100))
    brand = sql.Column(sql.String(100))
    body = sql.Column(sql.String(100))
    color = sql.Column(sql.String(100))
    transmission = sql.Column(sql.String(100))
    fuel = sql.Column(sql.String(100))
    prem = sql.Column(sql.Float)
    status = sql.Column(sql.String(100))


    def __init__(self,endate, agcode1, line, branch, idate, edate, pcategory, ptype, vuse, model, brand, body, color, transmission, fuel, prem, status):
        self.endate = endate  
        self.agcode1 = agcode1
        self.line = line
        self.branch = branch            
        self.idate = idate
        self.edate = edate
        self.pcategory = pcategory
        self.ptype = ptype
        self.vuse = vuse
        self.model = model
        self.brand = brand
        self.body = body
        self.color = color
        self.transmission = transmission
        self.fuel = fuel
        self.prem = prem
        self.status = status


    def to_dict(self):
        return{
            'endate' : self.endate,   
            'agcode1' : self.agcode1,
            'line' : self.line,
            'branch' : self.branch,
            'idate' : self.idate,
            'edate' : self.edate,
            'pcategory' : self.pcategory,
            'ptype' : self.ptype,
            'vuse' : self.vuse,
            'model' : self.model,
            'body' : self.body,
            'color' : self.color,
            'transmission' : self.transmission,
            'fuel' : self.fuel,
            'prem' : self.prem,
            'status' : self.status
        }

class Employees(sql.Model):
    __tablename__ = 'Employees'
    id = sql.Column(sql.Integer, primary_key=True)
    employee_id = sql.Column(sql.Integer, unique=True)
    employee_name = sql.Column(sql.String(100), unique=True)
    employee_email = sql.Column(sql.String(256), unique=True)

    def __init__(self, employee_id, employee_name, employee_email):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.employee_email = employee_email
    

    def to_dict(self):
        return {
            'employee_id' : self.employee_id,
            'employee_name' : self.employee_name,
            'employee_email' : self.employee_email
        }

class Policies(sql.Model):
    __tablename__ = 'Policies'
    id = sql.Column(sql.Integer, primary_key=True)
    date = sql.Column(sql.Date)
    code = sql.Column(sql.String(100),unique=True)
    name = sql.Column(sql.String(100),unique=True)
    cost = sql.Column(sql.Float(10,2))
    document = sql.Column(sql.String(100))

    def __init__(self, date, code, name, cost, duration, status, document):
        self.date = date
        self.code = code
        self.name = name
        self.cost = cost
        self.duration = duration
        self.status = status
        self.document = document

    def to_dict(self):
        return {
            'date' : self.date,
            'code' : self.code,
            'name' : self.name,
            'cost' : self.cost,
            'duration' : self.duration,
            'status' : self.status,
            'document' : self.document

        }

class Retention(sql.Model):
    __tablename__ = 'Retention'
    id = sql.Column(sql.Integer, primary_key=True)
    path = sql.Column(sql.String(100))
    retention = sql.Column(sql.Numeric)

    def __init__(self, path, retention):
        self.path = path
        self.retention = retention

    def to_dict(self):
        return {
            'path' : self.path,
            'retention' : self.retention,
        }

class Predictions(sql.Model):
    __tablename__ = 'Predictions'
    id = sql.Column(sql.Integer, primary_key=True)
    endate = sql.Column(sql.Date)
    agcode1 = sql.Column(sql.String(100),unique=True)
    line = sql.Column(sql.String(100))
    branch = sql.Column(sql.String(100))
    idate = sql.Column(sql.Date)
    edate = sql.Column(sql.Date)
    pcategory = sql.Column(sql.String(100))
    ptype = sql.Column(sql.String(100))
    vuse = sql.Column(sql.String(100))
    model = sql.Column(sql.String(100))
    brand = sql.Column(sql.String(100))
    body = sql.Column(sql.String(100))
    color = sql.Column(sql.String(100))
    transmission = sql.Column(sql.String(100))
    fuel = sql.Column(sql.String(100))
    prem = sql.Column(sql.Float)
    churn = sql.Column(sql.String(50))
    proba = sql.Column(sql.Float(10,2))

    def __init__(self,endate, agcode1, line, branch, idate, edate, pcategory, ptype, vuse, model, brand, body, color, transmission, fuel, prem, churn, proba):
        self.endate = endate  
        self.agcode1 = agcode1
        self.line = line
        self.branch = branch            
        self.idate = idate
        self.edate = edate
        self.pcategory = pcategory
        self.ptype = ptype
        self.vuse = vuse
        self.model = model
        self.brand = brand
        self.body = body
        self.color = color
        self.transmission = transmission
        self.fuel = fuel
        self.prem = prem
        self.churn = churn
        self.proba = proba

    def to_dict(self):
        return{
            'endate' : self.endate,   
            'agcode1' : self.agcode1,
            'line' : self.line,
            'branch' : self.branch,
            'idate' : self.idate,
            'edate' : self.edate,
            'pcategory' : self.pcategory,
            'ptype' : self.ptype,
            'vuse' : self.vuse,
            'model' : self.model,
            'body' : self.body,
            'color' : self.color,
            'transmission' : self.transmission,
            'fuel' : self.fuel,
            'prem' : self.prem,
            'churn' : self.churn,
            'proba' : self.proba
        }

class FeedbackQuestions(sql.Model):
    __tablename__ = 'FBQuestions'

    id = sql.Column(sql.Integer, primary_key=True)
    question = sql.Column(sql.String(1024))
    category = sql.Column(sql.String(256))
    status = sql.Column(sql.String(256))

    def __init__(self, question, category, status):
        self.question = question
        self.category = category
        self.status = status

    def to_dict(self):
        return {
            'question' : self.question,
            'category' : self.category,
            'status' : self.status
        }
    

class User(sql.Model):
    __tablename__ = 'Users'

    id = sql.Column(sql.Integer, primary_key=True)
    employee_id = sql.Column(sql.String(100), unique=True)
    username = sql.Column(sql.String(64), unique=True)
    email = sql.Column(sql.String(64), unique=True)
    password = sql.Column(sql.LargeBinary)

    def __init__(self, employee_id, username, email, password):
        self.employee_id = employee_id
        self.username = username
        self.email = email
        self.password = password


    def to_dict(self):
        return {
            'employee_id' : self.employee_id,
            'username' : self.username,
            'email' : self.email,
            'password' : self.password

        }

class Feedback(sql.Model):
    __tablename__ = 'feedback'
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(200), unique=True)
    gender = sql.Column(sql.String(200))
    age = sql.Column(sql.Integer)
    email = sql.Column(sql.String(200))
    prev_sub = sql.Column(sql.String(200))
    q1 = sql.Column(sql.Integer)
    q2 = sql.Column(sql.Integer)
    q3 = sql.Column(sql.Integer)
    q4 = sql.Column(sql.Integer)
    q5 = sql.Column(sql.Integer)
    q6 = sql.Column(sql.Integer)
    q7 = sql.Column(sql.Integer)
    q8 = sql.Column(sql.Integer)
    q9 = sql.Column(sql.Integer)
    q10 = sql.Column(sql.Integer)
    q11 = sql.Column(sql.Integer)
    q12 = sql.Column(sql.Integer)
    reason = sql.Column(sql.String(200))
    comments = sql.Column(sql.Text())

    def __init__(self, name, gender, age, email, prev_sub, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, reason, comments):
        self.name = name
        self.gender = gender
        self.age = age
        self.email = email
        self.prev_sub = prev_sub
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4
        self.q5 = q5
        self.q6 = q6
        self.q7 = q7
        self.q8 = q8
        self.q9 = q9
        self.q10 = q10
        self.q11 = q11
        self.q12 = q12
        self.reason = reason
        self.comments = comments
        
    def to_dict(self):
        return {
            'name' : self.name,
            'gender' : self.gender,
            'age' : self.age,
            'email' : self.email,
            'prev_sub' : self.prev_sub,
            'q1' : self.q1,
            'q2' : self.q2,
            'q3' : self.q3,
            'q4' : self.q4,
            'q5' : self.q5,
            'q6' : self.q6,
            'q7' : self.q7,
            'q8' : self.q8,
            'q9' : self.q9,
            'q10' : self.q10,
            'q11' : self.q11,
            'q12' : self.q12,
            'reason' : self.reason,
            'comment' : self.comment
        }

class Products(sql.Model):
    __tablename__ = 'Products'
    id = sql.Column(sql.Integer, primary_key=True)
    product = sql.Column(sql.String(100))

    def __init__(self, product):
        self.product = product

    def to_dict(self):
        return {
            'product' : self.product,
        }

class Reasons(sql.Model):
    __tablename__ = 'Reasons'
    id = sql.Column(sql.Integer, primary_key=True)
    reasons = sql.Column(sql.String(100))

    def __init__(self, reasons):
        self.reasons = reasons

    def to_dict(self):
        return {
            'reasons' : self.reasons,
        }
        
def allowed_file_csv(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CSV
        

def connection():
    DB_HOST = "localhost"
    DB_NAME = "asfalisdb"
    DB_USER = "postgres"
    DB_PASS = "analytico"
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn

# def connection():
#     DB_HOST = "ec2-35-173-91-114.compute-1.amazonaws.com"
#     DB_NAME = "dm8nvu4mj2uq0"
#     DB_USER = "mbvjwnkuqiwgpe"
#     DB_PASS = "805a5e28197a2e61c2851574da8212c857e5016a2750af0bbb79710466a08e7e"
#     conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
#     return conn


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
    
if __name__ == "__main__":
    app.run()
