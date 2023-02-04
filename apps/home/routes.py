# -*- encoding: utf-8 -*-
import os

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import psycopg2
import psycopg2.extras
import sqlalchemy

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 
from sklearn import metrics
from flask import Flask, request, render_template
import pickle
import json
import plotly
import plotly.express as px
import cohort, churn

from apps.authentication.util import hash_pass
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import login_required
from werkzeug.utils import secure_filename
from apps.config import config_dict
from apps import create_app, db
from apps.home import blueprint
from flask import render_template, request, redirect
from flask_login import login_required
from flask_bcrypt import bcrypt
from jinja2 import TemplateNotFound
from datetime import datetime
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from apps.authentication.models import Users

# import churn

UPLOAD_FOLDER = 'apps/static/assets/uploads/'
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
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mbvjwnkuqiwgpe:805a5e28197a2e61c2851574da8212c857e5016a2750af0bbb79710466a08e7e@ec2-35-173-91-114.compute-1.amazonaws.com:5432/dm8nvu4mj2uq0'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
sql = SQLAlchemy(app)

# engine = sqlalchemy.create_engine('postgresql://mbvjwnkuqiwgpe:805a5e28197a2e61c2851574da8212c857e5016a2750af0bbb79710466a08e7e@ec2-35-173-91-114.compute-1.amazonaws.com:5432/dm8nvu4mj2uq0')

engine = sqlalchemy.create_engine('postgresql://postgres:analytico@localhost/asfalisdb')


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

class PCategories(sql.Model):
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

class Policies(sql.Model):
    __tablename__ = 'Policies'
    id = sql.Column(sql.Integer, primary_key=True)
    date = sql.Column(sql.Date)
    code = sql.Column(sql.String(100),unique=True)
    name = sql.Column(sql.String(100),unique=True)
    cost = sql.Column(sql.Float(10,2))
    document = sql.Column(sql.String(100))

    def __init__(self, date, code, name, cost, document):
        self.date = date
        self.code = code
        self.name = name
        self.cost = cost
        self.document = document

    def to_dict(self):
        return {
            'date' : self.date,
            'code' : self.code,
            'name' : self.name,
            'cost' : self.cost,
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

class FeedbackQuestions(sql.Model):
    __tablename__ = 'FBQuestions'

    id = sql.Column(sql.Integer, primary_key=True)
    question = sql.Column(sql.String(1024))
    category = sql.Column(sql.String(256))
    status = sql.Column(sql.String(56))

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
# class User(sql.Model):
#     __tablename__ = 'Users'

#     id = sql.Column(db.Integer, primary_key=True)
#     username = sql.Column(db.String(64), unique=True)
#     email = sql.Column(db.String(64), unique=True)
#     password = sql.Column(db.LargeBinary)

#     def __init__(self, username, email, password):
#         self.username = username
#         self.email = email
#         self.password = password


#     def to_dict(self):
#         return {
#             'username' : self.username,
#             'email' : self.email,
#             'password' : self.password

#         }


def allowed_file_csv(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CSV
        

# def connection():
#     DB_HOST = "ec2-35-173-91-114.compute-1.amazonaws.com"
#     DB_NAME = "dm8nvu4mj2uq0"
#     DB_USER = "mbvjwnkuqiwgpe"
#     DB_PASS = "805a5e28197a2e61c2851574da8212c857e5016a2750af0bbb79710466a08e7e"
#     conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
#     return conn

def connection():
    DB_HOST = "localhost"
    DB_NAME = "asfalisdb"
    DB_USER = "postgres"
    DB_PASS = "analytico"
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    return conn


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None




# DASHBOARD
@blueprint.route('/index.html')
@login_required
def index():


    assured = Policyholders.query.count()
    fbCount = Feedback.query.count()
    date = f"{datetime.now():%Y-%m-%d}"

    insuredAmount = Policyholders.query.with_entities(func.sum(Policyholders.prem).label('total')).first().total

    if insuredAmount:
        insuredAmount = round(insuredAmount, 2)


    branchData = sql.session.query(sql.func.count(Policyholders.branch), Policyholders.branch).group_by(Policyholders.branch)

    branchLabels = [row[1] for row in branchData]
    branchValues = [row[0] for row in branchData]

    pcatData = sql.session.query(sql.func.count(Policyholders.pcategory), Policyholders.pcategory).group_by(Policyholders.pcategory)

    pcatLabels = [row[1] for row in pcatData]
    pcatValues = [row[0] for row in pcatData]

    brandData = sql.session.query(sql.func.count(Policyholders.brand), Policyholders.brand).group_by(Policyholders.brand)

    vmakerLabels = [row[1] for row in brandData]
    vmakerValues = [row[0] for row in brandData]

    bodyData = sql.session.query(sql.func.count(Policyholders.body), Policyholders.body).group_by(Policyholders.body)

    vtypeLabels = [row[1] for row in bodyData]
    vtypeValues = [row[0] for row in bodyData]

    modelData = sql.session.query(sql.func.count(Policyholders.model), Policyholders.model).group_by(Policyholders.model)

    modelLabels = [row[1] for row in modelData]
    modelValues = [row[0] for row in modelData]

    colorData = sql.session.query(sql.func.count(Policyholders.color), Policyholders.color).group_by(Policyholders.color)

    vcolorLabels = [row[1] for row in colorData]
    vcolorValues = [row[0] for row in colorData]


    assuredPercentage = (assured/1000) * 100


    return render_template('home/index.html', segment='index', assured = assured, date = date, branchLabels=branchLabels,branchValues=branchValues,pcatLabels=pcatLabels, pcatValues=pcatValues,vmakerLabels=vmakerLabels,vmakerValues=vmakerValues,vtypeLabels=vtypeLabels,vtypeValues=vtypeValues,modelLabels=modelLabels,modelValues=modelValues, vcolorLabels=vcolorLabels,vcolorValues=vcolorValues,insAmount=insuredAmount,assuredPercentage=assuredPercentage,fbCount=fbCount)


# COHORT ANALYSIS
@blueprint.route("/cohort_analysis.html", methods=['GET', 'POST'])
@login_required
def cohort_analysis():
    retained = 0
    if request.method == 'POST':
        if request.form.get('sample_cohort') == 'Load & Analyze':
            cohort.visualize()
            default = cohort.defaultAve()
            return render_template("/home/cohort_analysis.html",retained=default)
        elif request.form.get('sample_cohort') == 'Analyze':

                if request.method == 'POST':
                    file = request.files['excelfile']
                    # check if the post request has the file part
                    if 'excelfile' not in request.files:
                        error = "No file Part present"
                
                    # If the user does not select a file, the browser submits an
                    # empty file without a filename.
                    elif file.filename == '':
                        error = "No File Selected"


                    if file:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        success = "File Uploaded Successfully!"
                        path = "apps/static/assets/uploads/"+file.filename
                        cohort.loadVis(path)
                        default = cohort.calc_Average(path)
                        retentionRate = default
                        return render_template("/home/cohort_analysis.html",retained=default)
        else:
            return render_template('/home/cohort_analysis.html')


    return render_template("/home/cohort_analysis.html",retained=retained)




@blueprint.route("/upload_excel", methods=['GET','POST'])
@login_required
def upload_excel():
    error=None
    success = None
    allDetails = []
    allErrors = []

    if request.method == 'POST':
        file = request.files['excelfile']
        # check if the post request has the file part
        if 'excelfile' not in request.files:
            error = "No file Part present"
    
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        elif file.filename == '':
            error = "No File Selected"


        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = "File Uploaded Successfully!"
            path = "apps/static/assets/uploads/"+file.filename
            df = pd.read_csv(path, encoding='latin1')
            if 'idate' in df:
                path = "apps/static/assets/uploads/"+file.filename
                cohort.actualCohort(path)
                retained = cohort.calc_Actual(path)
                cohort.compreCohort(path)
                compreRetained = cohort.calc_Compre(path)
                cohort.ctplCohort(path)
                ctplRetained = cohort.calc_CTPL(path)
                cohort.basicCohort(path)
                basicRetained = cohort.calc_Basic(path)
                cohort.premiumCohort(path)
                premiumRetained = cohort.calc_Premium(path)
                return render_template('home/cohort_analysis.html', error = error, success = success, datas = allDetails, allErrors= allErrors, retained=retained, compreRetained=compreRetained,ctplRetained=ctplRetained,basicRetained=basicRetained,premiumRetained=premiumRetained,segment="cohort analysis")
            else:
                error = "You have uploaded a csv file with an incorrect format!"
                return render_template('home/cohort_analysis.html',error=error)

    return render_template('home/cohort_analysis.html', error = error, success = success, datas = allDetails, allErrors= allErrors, segment="cohort analysis") 


churnDataset = "apps/static/assets/uploads/churn_dataset.csv"
df_1=pd.read_csv(churnDataset)
df_1.drop(columns=['endate','agcode1','line','idate','edate'],axis=1,inplace=True)
# CHURN ANALYSIS - IN PROGRESS

@blueprint.route("/churn_analysis.html")
@login_required
def churn_analysis():
    allDetails = Predictions.query.all()
    return render_template("home/churn_analysis.html", datas = allDetails)

@blueprint.route('/verify', methods=['POST'])
@login_required
def verify():
    error=None
    success = None
    allDetails = []
    allErrors = []

    if request.method == 'POST':
        agcode1 = request.form['agcode1']

    query_details = Policyholders.query.filter_by(agcode1=agcode1).first()
    prediction_details = Predictions.query.filter_by(agcode1=agcode1).first()

    if query_details == None:
        error = "Assured ID does not exist in the database! Please check your Assured ID."
    elif prediction_details:
        error = "You have already predicted this Assured ID! Please select another Assured ID"
    else:
        #print("Error in entry!  ", name, "  ", query_pic.pic)
        policyholders = Policyholders.query.filter_by(agcode1 = agcode1).first()
        return render_template('home/predictfromdb.html',assuredID=agcode1, datas=policyholders)
                
    allDetails = Predictions.query.all()

    return render_template('home/churn_analysis.html', error = error, success = success, datas = allDetails, allErrors= allErrors)
    
@blueprint.route("/predictchurn", methods=['GET', 'POST'])
@login_required
def predictchurn():
    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT cost FROM public."Policies" ORDER BY cost ASC')
    premiumCost = cur.fetchall()

    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2.execute('SELECT id, cost FROM public."Policies" ORDER BY id ASC')
    autoPremium = cur2.fetchall()

    cur3 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur3.execute('SELECT branch FROM "Branches" ORDER BY branch ASC')
    branches = cur3.fetchall()

    cur4 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur4.execute('SELECT ID, ptype FROM "PType" ORDER BY ID ASC')
    ptype = cur4.fetchall()

    cur5 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur5.execute('SELECT ID, pcategory FROM "PCategories" ORDER BY ID ASC')
    pcategory = cur5.fetchall()

    cur6 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur6.execute('SELECT ID, vuse FROM "VUse" ORDER BY ID ASC')
    vuse = cur6.fetchall()

    cur7 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur7.execute('SELECT ID, transmission FROM "VTransmission" ORDER BY ID ASC')
    transmission = cur7.fetchall()

    cur8 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur8.execute('SELECT ID, fuel FROM "VFuel" ORDER BY ID ASC')
    fuel = cur8.fetchall()

    return render_template("home/predict.html",premiumCost=premiumCost,autoPremium=autoPremium, branches=branches, ptype=ptype,pcategory=pcategory,vuse=vuse,transmission=transmission,fuel=fuel)

@blueprint.route("/predictfromdb.html", methods=['GET', 'POST'])
@login_required
def predictfromdb():

    if request.method == 'POST':
        agcode1 = request.form['agcode1']
        assuredID = agcode1
        return render_template("home/predictfromdb.html",assuredID=assuredID)

    return render_template("home/predictfromdb.html")

@blueprint.route("/predict.html", methods=['GET', 'POST'])
@login_required
def predict():

    success=None

    '''
    endate           object
    agcode1          object
    line             object
    branch           object
    idate            object
    edate            object
    pcategory        object
    ptype            object
    vuse             object
    brand            object
    body             object
    model             int64
    color            object
    transmission     object
    fuel             object
    prem            float64
    churn            object
    '''

    # Get data from form
    endate = request.form['endate']
    agcode1 = request.form['agcode1']
    line = request.form['line']
    branch = request.form['branch']
    idate = request.form['idate']
    edate = request.form['edate']
    pcategory = request.form['pcategory']
    ptype = request.form['ptype']
    vuse = request.form['vuse']
    brand = request.form['brand']
    body = request.form['body']
    model = request.form['model']
    color = request.form['color']
    transmission = request.form['transmission']
    fuel = request.form['fuel']
    prem = request.form['prem']



    # Load Churn Predictive Model
    pmodel = pickle.load(open("model.sav", "rb"))


    # Store values to data list
    data = [[branch, pcategory, ptype, vuse, brand, body, model, color, transmission, fuel, prem]]
    
    # Create new data frame
    new_df = pd.DataFrame(data, columns = ['branch', 'pcategory', 'ptype', 'vuse', 'brand', 'body', 'model', 'color', 'transmission', 'fuel', 'prem'])

    # Concatenate original data frame to the new data  frame
    df_2 = pd.concat([df_1, new_df], ignore_index = True) 
    
    # Remove non dummy columns
    non_dummy_cols = ['model','prem']
    dummy_cols = list(set(df_2.columns) - set(non_dummy_cols))
    new_df__dummies = pd.get_dummies(df_2, columns=dummy_cols)

    # Load dataset to the predictive model
    single = pmodel.predict(new_df__dummies.tail(1)) 
    probability = pmodel.predict_proba(new_df__dummies.tail(1))[:,1]

    # Output generation
    if single==1:
        churn = "Yes"
        proba = probability[0].round(4)*100
        predictions = Predictions(endate = endate, agcode1 = agcode1, line = line, branch = branch, idate = idate, edate = edate, pcategory = pcategory, ptype = ptype, vuse = vuse, brand = brand, body = body, model = model, color = color, transmission = transmission, fuel = fuel, prem = prem, churn = churn, proba = proba)
        sql.session.add(predictions)
        sql.session.commit()
        flash('Prediction Complete', 'success')
        o1 = "This customer is likely to churn!"
        o2 = "Confidence: {}".format(probability.round(4)*100)
    else:
        churn = "No"
        proba = probability[0].round(4)*100
        predictions = Predictions(endate = endate, agcode1 = agcode1, line = line, branch = branch, idate = idate, edate = edate, pcategory = pcategory, ptype = ptype, vuse = vuse, brand = brand, body = body, model = model, color = color, transmission = transmission, fuel = fuel, prem = prem, churn = churn, proba = proba)
        sql.session.add(predictions)
        sql.session.commit()
        flash('Prediction Complete', 'success')
        o1 = "This customer is likely to continue!"
        o2 = "Confidence: {}".format(probability.round(4)*100)

    percentage = probability[0].round(4)*100
    print(percentage)

    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT cost FROM public."Policies" ORDER BY cost ASC')
    premiumCost = cur.fetchall()

    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2.execute('SELECT id, cost FROM public."Policies" ORDER BY id ASC')
    autoPremium = cur2.fetchall()

    cur3 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur3.execute('SELECT branch FROM "Branches" ORDER BY branch ASC')
    Branches = cur3.fetchall()

    cur4 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur4.execute('SELECT ID, ptype FROM "PType" ORDER BY ID ASC')
    Ptype = cur4.fetchall()

    cur5 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur5.execute('SELECT ID, pcategory FROM "PCategories" ORDER BY ID ASC')
    Pcategory = cur5.fetchall()

    cur6 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur6.execute('SELECT ID, vuse FROM "VUse" ORDER BY ID ASC')
    Vuse = cur6.fetchall()

    cur7 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur7.execute('SELECT ID, transmission FROM "VTransmission" ORDER BY ID ASC')
    Transmission = cur7.fetchall()

    cur8 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur8.execute('SELECT ID, fuel FROM "VFuel" ORDER BY ID ASC')
    Fuel = cur8.fetchall()

    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()

    return render_template("/home/predict.html", success = success,prediction = o1, probability = o2, percentage = percentage,premiumCost=premiumCost,branches=Branches,ptype=Ptype,pcategory=Pcategory,vuse=Vuse,transmission=Transmission,Fuel=fuel)

@blueprint.route("/delete_prediction/<uid>", methods=['GET'])
@login_required
def delete_prediction(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "Predictions" where ID=%s', (uid,))
    conn.commit()
    flash('Prediction Deleted', 'danger')
    return redirect(url_for("home_blueprint.churn_analysis"))



# CUSTOMER INFORMATION MANAGEMENT - DONE
@blueprint.route("/policyholders.html")
@login_required
def custindex():
    allDetails = Policyholders.query.all()
    return render_template('/home/policyholders.html',datas=allDetails)


@blueprint.route("/upload_csv", methods=['GET', 'POST'])
@login_required
def upload_csv():
    error=None
    success = None
    allDetails = []
    allErrors = []

    if request.method == 'POST':
        file = request.files['csvfile']
        # check if the post request has the file part
        if 'csvfile' not in request.files:
            error = "No file Part present"
    
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        elif file.filename == '':
            error = "No File Selected"

        elif allowed_file_csv(file.filename) != True:
            error = "Please upload a csv file"

        if file and allowed_file_csv(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = "File Uploaded Successfully!"
            path = "apps/static/assets/uploads/"+file.filename
            all_details = pd.read_csv(path)

            for index, row in all_details.iterrows():
                endate = row['endate']
                agcode1 = row['agcode1']
                line = row['line']
                branch = row['branch']
                idate = row['idate']
                edate = row['edate']
                pcategory = row['pcategory']
                ptype = row['ptype']
                vuse = row['vuse']
                brand = row['brand']
                body = row['body']
                model = row['model']
                color = row['color']
                transmission = row['transmission']
                fuel = row['fuel']
                prem = row['prem']
                status = row['status']
                policyholders = Policyholders(endate = endate, agcode1 = agcode1, line = line, branch = branch, idate = idate, edate = edate, pcategory = pcategory, ptype = ptype, vuse = vuse, brand = brand, body = body, model = model, color = color, transmission = transmission, fuel = fuel, prem = prem, status = status)
                query_details = Policyholders.query.filter_by(agcode1=agcode1).first()
                
                if query_details == None:
                    sql.session.add(policyholders)
                    sql.session.commit()
                else:
                    #print("Error in entry!  ", name, "  ", query_pic.pic)
                    success = None
                    error = "Entries with the following name(s) not uploaded as ones with the same name already exist in the database:"
                    allErrors.append(agcode1)
                
    allDetails = Policyholders.query.all()

    return render_template('home/policyholders.html', error = error, success = success, datas = allDetails, allErrors= allErrors, segment="policyholders")

@blueprint.route("/delete/<agcode1>")
@login_required
def delete(agcode1):
    details = Policyholders.query.filter_by(agcode1 = agcode1).first()
    sql.session.delete(details)
    sql.session.commit()
    flash('Policyholder Deleted', 'danger')
    return redirect("/policyholders.html")

@blueprint.route("/deleteCust",methods=['GET','POST'])
def deleteCust(): 
    if request.method == 'POST':
        for getid in request.form.getlist('mycheckbox'):
            print(getid)
            details = Policyholders.query.filter_by(agcode1=getid).first()
            sql.session.delete(details)
            sql.session.commit()
            flash('Successfully Deleted', 'danger')
            return redirect("/policyholders.html")
    flash('Select policyholder/s to delete first!', 'danger')
    return redirect('/policyholders.html')

@blueprint.route("/addnew" , methods=['GET', 'POST'])
@login_required
def addnew():
    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT cost FROM public."Policies" ORDER BY cost ASC')
    premiumCost = cur.fetchall()

    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2.execute('SELECT id, cost FROM public."Policies" ORDER BY id ASC')
    autoPremium = cur2.fetchall()

    cur3 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur3.execute('SELECT branch FROM "Branches" ORDER BY branch ASC')
    branches = cur3.fetchall()

    cur4 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur4.execute('SELECT ID, ptype FROM "PType" ORDER BY ID ASC')
    ptype = cur4.fetchall()

    cur5 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur5.execute('SELECT ID, pcategory FROM "PCategories" ORDER BY ID ASC')
    pcategory = cur5.fetchall()

    cur6 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur6.execute('SELECT ID, vuse FROM "VUse" ORDER BY ID ASC')
    vuse = cur6.fetchall()

    cur7 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur7.execute('SELECT ID, transmission FROM "VTransmission" ORDER BY ID ASC')
    transmission = cur7.fetchall()

    cur8 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur8.execute('SELECT ID, fuel FROM "VFuel" ORDER BY ID ASC')
    fuel = cur8.fetchall()

    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()

    return render_template('home/add_policyholder.html', premiumCost=premiumCost,autoPremium=autoPremium, branches=branches, ptype=ptype,pcategory=pcategory,vuse=vuse,transmission=transmission,fuel=fuel)

@blueprint.route("/policyholders.html/addnewentry", methods=['GET','POST'])
@login_required
def addnewentry():
    if request.method == 'POST':
        endate = request.form['endate']
        agcode1 = request.form['agcode1']
        line = request.form['line']
        branch = request.form['branch']
        idate = request.form['idate']
        edate = request.form['edate']
        pcategory = request.form['pcategory']
        ptype = request.form['ptype']
        vuse = request.form['vuse']
        brand = request.form['brand']
        body = request.form['body']
        model = request.form['model']
        color = request.form['color']
        transmission = request.form['transmission']
        fuel = request.form['fuel']
        prem = request.form['prem']
        status = request.form['status']

        if isinstance(agcode1, str):
            agcode1 = agcode1.strip()
        if pd.isna(agcode1) or agcode1 == None or agcode1 == '':
            error ="Assured ID cannot be null!"
            return render_template('home/add_policyholder.html', error = error)
        if brand.isnumeric():
            error ="Invalid Input! Brand cannot be numeric!"
            return render_template('home/add_policyholder.html', error = error)
        if color.isnumeric():
            error ="Invalid Input! Color cannot be numeric!"
            return render_template('home/add_policyholder.html', error = error)
        if model.isnumeric() == False:
            error ="Invalid Input! Model year cannot be a text!"
            return render_template('home/add_policyholder.html', error = error)
        policyholders = Policyholders(endate = endate, agcode1 = agcode1, line = line, branch = branch, idate = idate, edate = edate, pcategory = pcategory, ptype = ptype, vuse = vuse, brand = brand, body = body, model = model, color = color, transmission = transmission, fuel = fuel, prem = prem, status = status)
        query_details = Policyholders.query.filter_by(agcode1=agcode1).first()
        if query_details == None:
            sql.session.add(policyholders)
            sql.session.commit()
            flash('Policyholder Added', 'success')
            return redirect('/policyholders.html')
        else:
            success = None
            error = "An entry with the same Assured ID already exists in the database!!"
            return render_template('home/add_policyholder.html', error = error)
    return render_template('home/add_policyholder.html')


@blueprint.route("/edit_fbquestion/<uid>", methods=['GET','POST'])
@login_required
def edit_fbquestion(uid):
    success = None
    error = None
    if request.method == 'POST':
        question = request.form['question']
        category = request.form['category']
        status = request.form['status']

        conn = connection()
        cur = conn.cursor()
        cur.execute('UPDATE "FBQuestions" SET question=%s, category=%s, status=%s where id=%s',(question, category, status, uid))
        conn.commit()
        flash('Feedback Question Updated', 'success')
        return redirect(url_for("home_blueprint.feedback"))
    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM "FBQuestions" WHERE id=%s',(uid,))
    data = cur.fetchall()
    cur.close()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    print(data[0])
    return render_template("/home/edit_fbquestion.html", datas=data[0],success=success, error=error)



@blueprint.route("/update/<string:agcode1>", methods=['POST', 'GET'])
@login_required
def update(agcode1):
    policyholders = Policyholders.query.filter_by(agcode1 = agcode1).first()
    if request.method=='POST':
        error = None
        endate = request.form['endate']
        agcode1 = request.form['agcode1']
        line = request.form['line']
        branch = request.form['branch']
        idate = request.form['idate']
        edate = request.form['edate']
        pcategory = request.form['pcategory']
        ptype = request.form['ptype']
        vuse = request.form['vuse']
        brand = request.form['brand']
        body = request.form['body']
        model = request.form['model']
        color = request.form['color']
        transmission = request.form['transmission']
        fuel = request.form['fuel']
        prem = request.form['prem']
        status = request.form['status']

        policyholders = Policyholders.query.filter_by(agcode1=agcode1).first()
        policyholders.endate = endate
        policyholders.line = line
        policyholders.branch = branch
        policyholders.idate = idate
        policyholders.edate = edate
        policyholders.pcategory = pcategory
        policyholders.ptype = ptype
        policyholders.vuse = vuse
        policyholders.brand = brand
        policyholders.body = body
        policyholders.model = model
        policyholders.color = color
        policyholders.transmission = transmission
        policyholders.fuel = fuel
        policyholders.prem = prem
        policyholders.status = status

        sql.session.add(policyholders)
        sql.session.commit()
        flash('Policyholder Updated', 'success')
        return redirect("/policyholders.html")

    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT cost FROM public."Policies" ORDER BY id ASC')
    premiumCost = cur.fetchall()

    cur3 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur3.execute('SELECT branch FROM "Branches" ORDER BY branch ASC')
    branches = cur3.fetchall()

    cur4 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur4.execute('SELECT ID, ptype FROM "PType" ORDER BY ID ASC')
    ptype = cur4.fetchall()

    cur5 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur5.execute('SELECT ID, pcategory FROM "PCategories" ORDER BY ID ASC')
    pcategory = cur5.fetchall()

    cur6 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur6.execute('SELECT ID, vuse FROM "VUse" ORDER BY ID ASC')
    vuse = cur6.fetchall()

    cur7 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur7.execute('SELECT ID, transmission FROM "VTransmission" ORDER BY ID ASC')
    transmission = cur7.fetchall()

    cur8 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur8.execute('SELECT ID, fuel FROM "VFuel" ORDER BY ID ASC')
    fuel = cur8.fetchall()

    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()

    return render_template('/home/update.html', datas = policyholders,premiumCost=premiumCost,branches=branches,ptype=ptype,pcategory=pcategory,vuse=vuse,transmission=transmission,fuel=fuel)


@blueprint.route("/predictionreports.html")
@login_required
def predRepindex():
    allDetails = Predictions.query.all()

    df = pd.read_sql_table("Predictions",engine)
    insurance_data = df.copy()
    insurance_data.drop(columns=['id','endate','agcode1','line','idate','edate','proba'],axis=1,inplace=True)

    branchdf = df.groupby(by=["branch","churn"]).size().reset_index(name="counts")

    fig1 = px.bar(data_frame=branchdf, x="branch", y="counts", color="churn", barmode="group",title="<b>Churn Counts per Branch</b>",color_discrete_map={ # replaces default color mapping by value
                "Yes": "#faa273", "No": "#265138"
            })

    pcatdf = df.groupby(by=["pcategory","churn"]).size().reset_index(name="counts")

    fig2 = px.bar(data_frame=pcatdf, x="pcategory", y="counts", color="churn", barmode="group",title="<b>Churn Counts per Policy Category</b>",color_discrete_map={ # replaces default color mapping by value
                "Yes": "#faa273", "No": "#265138"
            })

    branddf = df.groupby(by=["brand","churn"]).size().reset_index(name="counts")

    fig3 = px.bar(data_frame=branddf, x="brand", y="counts", color="churn", barmode="group",title="<b>Churn Counts per Vehicle Brand</b>",color_discrete_map={ # replaces default color mapping by value
                "Yes": "#faa273", "No": "#265138"
            })

    modeldf = df.groupby(by=["model","churn"]).size().reset_index(name="counts")

    fig4 = px.bar(data_frame=modeldf, x="model", y="counts", color="churn", barmode="group",title="<b>Churn Counts per Vehicle Model Year</b>",color_discrete_map={ # replaces default color mapping by value
                "Yes": "#faa273", "No": "#265138"
            })

    bodydf = df.groupby(by=["body","churn"]).size().reset_index(name="counts")

    fig5 = px.bar(data_frame=bodydf, x="body", y="counts", color="churn", barmode="group",title="<b>Churn Counts per Vehicle Body Type</b>",color_discrete_map={ # replaces default color mapping by value
                "Yes": "#faa273", "No": "#265138"
            })

    churndf = df.groupby(by=["churn"]).size().reset_index(name="counts")

    fig6 = px.bar(data_frame=churndf, x="churn", y="counts", color="churn",title="<b>Churn Count Ratio</b>",color_discrete_map={ # replaces default color mapping by value
                "Yes": "#faa273", "No": "#265138"
            })
    



    fig1.update_layout(
        xaxis_title="Branches", 
        yaxis_title="Churn Count",
        font_family="Inter",
        font_color="#265138",
        title_font_family="Inter",
        title_font_color="#265138",
        legend_title_font_color="#265138",
        legend_title_font_family="Inter"
    )

    fig2.update_layout(
        xaxis_title="Policy Category", 
        yaxis_title="Churn Count",
        font_family="Inter",
        font_color="#265138",
        title_font_family="Inter",
        title_font_color="#265138",
        legend_title_font_color="#265138",
        legend_title_font_family="Inter"
    )

    fig3.update_layout(
        xaxis_title="Vehicle Brand", 
        yaxis_title="Churn Count",
        font_family="Inter",
        font_color="#265138",
        title_font_family="Inter",
        title_font_color="#265138",
        legend_title_font_color="#265138",
        legend_title_font_family="Inter"
    )

    fig4.update_layout(
        xaxis_title="Vehicle Model Year", 
        yaxis_title="Churn Count",
        font_family="Inter",
        font_color="#265138",
        title_font_family="Inter",
        title_font_color="#265138",
        legend_title_font_color="#265138",
        legend_title_font_family="Inter"
    )

    fig5.update_layout(
        xaxis_title="Vehicle Body Type", 
        yaxis_title="Churn Count",
        font_family="Inter",
        font_color="#265138",
        title_font_family="Inter",
        title_font_color="#265138",
        legend_title_font_color="#265138",
        legend_title_font_family="Inter"
    )

    fig6.update_layout(
        xaxis_title="Churn", 
        yaxis_title="Count",
        font_family="Inter",
        font_color="#265138",
        title_font_family="Inter",
        title_font_color="#265138",
        legend_title_font_color="#265138",
        legend_title_font_family="Inter"
    )



    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    graph4JSON = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    graph5JSON = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    graph6JSON = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
    mean = df['proba'].mean()
    mean

    notChurn = df.loc[df.churn == 'No', 'churn'].count()
    Churn = df.loc[df.churn == 'Yes', 'churn'].count()
    total = df['churn'].count()

    churnRate = Churn/total * 100
    churnRate

    churn_data = insurance_data.copy()
    churn_data['churn'] = np.where(churn_data.churn == 'Yes',1,0)
    churn_data_dummies = pd.get_dummies(churn_data)
    plt.figure(figsize=(20,8))
    ax = churn_data_dummies.corr()['churn'].sort_values(ascending = False).plot(kind='bar')
    fig = ax.get_figure()
    fig.savefig("./apps/static/assets/images/cohort/churnFactors.png")


    churnFactors = churn_data_dummies.corr()['churn'].sort_values(ascending=False)
    churnFactors = churnFactors.round(3)*100
    churnFactors = round(churnFactors,2)
    churnFactors = churnFactors.iloc[1:11]
    churnFactors = churnFactors.to_dict()
    
    
    leastFactors = churn_data_dummies.corr()['churn'].sort_values(ascending=True)
    leastFactors = leastFactors.round(3)*100
    leastFactors = round(leastFactors, 2)
    leastFactors = leastFactors.head(10).to_dict()
    
    return render_template('home/predictionreports.html',datas=allDetails,graph1JSON=graph1JSON,graph2JSON=graph2JSON,graph3JSON=graph3JSON,graph4JSON=graph4JSON,graph5JSON=graph5JSON,graph6JSON=graph6JSON,churnrate=mean,ratio=churnRate,churnFactors=churnFactors,leastFactors=leastFactors)


@blueprint.route("/churnfb.html")
@login_required
def feedbackindex():
    allDetails = Feedback.query.all()

    reasonData = sql.session.query(sql.func.count(Feedback.reason), Feedback.reason).group_by(Feedback.reason)

    reasonLabels = [row[1] for row in reasonData]
    reasonValues = [row[0] for row in reasonData]

    prevData = sql.session.query(sql.func.count(Feedback.prev_sub), Feedback.prev_sub).group_by(Feedback.prev_sub)

    prevLabels = [row[1] for row in prevData]
    prevValues = [row[0] for row in prevData]

    q1Data = sql.session.query(sql.func.count(Feedback.q1), Feedback.q1).group_by(Feedback.q1)
    q1Labels = [row[1] for row in q1Data]
    q1Values = [row[0] for row in q1Data]

    q2Data = sql.session.query(sql.func.count(Feedback.q2), Feedback.q2).group_by(Feedback.q2)
    q2Labels = [row[1] for row in q2Data]
    q2Values = [row[0] for row in q2Data]

    q3Data = sql.session.query(sql.func.count(Feedback.q3), Feedback.q3).group_by(Feedback.q3)
    q3Labels = [row[1] for row in q3Data]
    q3Values = [row[0] for row in q3Data]

    q4Data = sql.session.query(sql.func.count(Feedback.q4), Feedback.q4).group_by(Feedback.q4)
    q4Labels = [row[1] for row in q4Data]
    q4Values = [row[0] for row in q4Data]

    q5Data = sql.session.query(sql.func.count(Feedback.q5), Feedback.q5).group_by(Feedback.q5)
    q5Labels = [row[1] for row in q5Data]
    q5Values = [row[0] for row in q5Data]

    q6Data = sql.session.query(sql.func.count(Feedback.q6), Feedback.q6).group_by(Feedback.q6)
    q6Labels = [row[1] for row in q6Data]
    q6Values = [row[0] for row in q6Data]

    q7Data = sql.session.query(sql.func.count(Feedback.q7), Feedback.q7).group_by(Feedback.q7)
    q7Labels = [row[1] for row in q7Data]
    q7Values = [row[0] for row in q7Data]

    q8Data = sql.session.query(sql.func.count(Feedback.q8), Feedback.q8).group_by(Feedback.q8)
    q8Labels = [row[1] for row in q8Data]
    q8Values = [row[0] for row in q8Data]

    q9Data = sql.session.query(sql.func.count(Feedback.q9), Feedback.q9).group_by(Feedback.q9)
    q9Labels = [row[1] for row in q9Data]
    q9Values = [row[0] for row in q9Data]

    q10Data = sql.session.query(sql.func.count(Feedback.q10), Feedback.q10).group_by(Feedback.q10)
    q10Labels = [row[1] for row in q10Data]
    q10Values = [row[0] for row in q10Data]

    q11Data = sql.session.query(sql.func.count(Feedback.q11), Feedback.q11).group_by(Feedback.q11)
    q11Labels = [row[1] for row in q11Data]
    q11Values = [row[0] for row in q11Data]

    q12Data = sql.session.query(sql.func.count(Feedback.q12), Feedback.q12).group_by(Feedback.q12)
    q12Labels = [row[1] for row in q12Data]
    q12Values = [row[0] for row in q12Data]

    date = f"{datetime.now():%Y-%m-%d}"

    return render_template('home/churnfb.html', date=date, data=allDetails, segment='churnfb', reasonLabels=reasonLabels,reasonValues=reasonValues,prevLabels=prevLabels,prevValues=prevValues,q1Labels=q1Labels,q1Values=q1Values, q2Labels= q2Labels,q2Values=q2Values,q3Labels=q3Labels,q3Values=q3Values,q4Values=q4Values,q4Labels=q4Labels,q5Labels=q5Labels,q5Values=q5Values,q6Labels=q6Labels,q6Values=q6Values,q7Labels=q7Labels,q7Values=q7Values,q8Labels=q8Labels,q8Values=q8Values,q9Labels=q9Labels,q9Values=q9Values,q10Labels=q10Labels,q10Values=q10Values,q11Labels=q11Labels,q11Values=q11Values,q12Labels=q12Labels,q12Values=q12Values)

@blueprint.route("/add_product", methods=['POST', 'GET'])
@login_required
def add_product():
    error=None
    success=None
    if request.method == 'POST':
        product = request.form['product']
        query_details = Products.query.filter_by(product=product).first()
        if query_details == None:
            data=Products(product)
            sql.session.add(data)
            sql.session.commit()
            flash('Product Added', 'success')
            return redirect(url_for("home_blueprint.feedback"))
        else:
            success = None
            error = "Product already exists! Please enter another branch"
            return render_template('home/feedback.html', error = error)

    return render_template("/home/feedback.html",success=success,error=error)


@blueprint.route("/delete_product/<uid>", methods=['GET'])
@login_required
def delete_product(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "Products" where ID=%s', (uid,))
    conn.commit()

    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Product Deleted', 'danger')
    return redirect(url_for("home_blueprint.feedback"))

@blueprint.route("/add_reason", methods=['POST', 'GET'])
@login_required
def add_reason():
    error=None
    success=None
    if request.method == 'POST':
        reason = request.form['reason']
        query_details = Reasons.query.filter_by(reasons=reason).first()
        if query_details == None:
            data=Reasons(reason)
            sql.session.add(data)
            sql.session.commit()
            flash('Churn Factor Added', 'success')
            return redirect(url_for("home_blueprint.feedback"))
        else:
            success = None
            error = "Reason already exists! Please enter another branch"
            return render_template('home/feedback.html', error = error)

    return render_template("/home/feedback.html",success=success,error=error)


@blueprint.route("/delete_reason/<uid>", methods=['GET'])
@login_required
def delete_reason(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "Reasons" where ID=%s', (uid,))
    conn.commit()

    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Chrun Factor Deleted', 'danger')
    return redirect(url_for("home_blueprint.feedback"))


# POLICIES MANAGEMENT - Upload Policy Document
@blueprint.route("/policies.html")
@login_required
def policiesindex():
    
    allDetails = Policies.query.all()
    conn = connection()
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT ID, branch FROM "Branches" ORDER BY ID ASC')
    branches = cur.fetchall()

    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2.execute('SELECT ID, ptype FROM "PType" ORDER BY ID ASC')
    ptype = cur2.fetchall()

    cur3 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur3.execute('SELECT ID, pcategory FROM "PCategories" ORDER BY ID ASC')
    pcategory = cur3.fetchall()

    cur4 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur4.execute('SELECT ID, vuse FROM "VUse" ORDER BY ID ASC')
    vuse = cur4.fetchall()

    cur5 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur5.execute('SELECT ID, transmission FROM "VTransmission" ORDER BY ID ASC')
    transmission = cur5.fetchall()

    cur6 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur6.execute('SELECT ID, fuel FROM "VFuel" ORDER BY ID ASC')
    fuel = cur6.fetchall()

    return render_template('home/policies.html',datas=allDetails,segment="policies",branches=branches,ptype=ptype,pcategory=pcategory,vuse=vuse,transmission=transmission,fuel=fuel)


@blueprint.route("/add_branch", methods=['POST', 'GET'])
@login_required
def add_branch():
    error=None
    success=None
    if request.method == 'POST':
        branch = request.form['branch']
        query_details = Branches.query.filter_by(branch=branch).first()
        if query_details == None:
            data=Branches(branch)
            sql.session.add(data)
            sql.session.commit()
            flash('Branch Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Branch already exists! Please enter another branch"
            return render_template('home/policies.html', error = error)

    return render_template("/home/policies.html",success=success,error=error)


@blueprint.route("/delete_branch/<uid>", methods=['GET'])
@login_required
def delete_branch(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "Branches" where ID=%s', (uid,))
    conn.commit()

    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Branch Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))

@blueprint.route("/add_ptype", methods=['POST', 'GET'])
@login_required
def add_ptype():
    error=None
    success=None
    if request.method == 'POST':
        ptype = request.form['ptype']
        query_details = PType.query.filter_by(ptype=ptype).first()
        if query_details == None:
            data=PType(ptype)
            sql.session.add(data)
            sql.session.commit()
            flash('Policy Type Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Policy Type already exists! Please enter another policy type"
            return render_template('home/policies.html', error = error)
    return render_template("/home/policies.html",success=success,error=error)

@blueprint.route("/delete_ptype/<uid>", methods=['GET'])
@login_required
def delete_ptype(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "PType" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Policy Type Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))

@blueprint.route("/add_pcategory", methods=['POST', 'GET'])
@login_required
def add_pcategory():
    error=None
    success=None
    if request.method == 'POST':
        pcategory = request.form['pcategory']
        query_details = PCategories.query.filter_by(pcategory=pcategory).first()
        if query_details == None:
            data=PCategories(pcategory)
            sql.session.add(data)
            sql.session.commit()
            flash('Policy Category Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Policy Category already exists! Please enter another policy category"
            return render_template('home/policies.html', error = error)
    return render_template("/home/policies.html",success=success,error=error)

@blueprint.route("/delete_pcategory/<uid>", methods=['GET'])
@login_required
def delete_pcategory(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "PCategories" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Policy Category Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))

@blueprint.route("/add_vuse", methods=['POST', 'GET'])
@login_required
def add_vuse():
    error=None
    success=None
    if request.method == 'POST':
        vuse = request.form['vuse']
        query_details = VehicleUse.query.filter_by(vuse=vuse).first()
        if query_details == None:
            data=VehicleUse(vuse)
            sql.session.add(data)
            sql.session.commit()
            flash('Vehicle Use Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Vehicle Use already exists! Please enter another vehicle use"
            return render_template('home/policies.html', error = error)
    return render_template("/home/policies.html",success=success,error=error)

@blueprint.route("/delete_vuse/<uid>", methods=['GET'])
@login_required
def delete_vuse(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "VUse" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Vehicle Use Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))

@blueprint.route("/add_transmission", methods=['POST', 'GET'])
@login_required
def add_transmission():
    error=None
    success=None
    if request.method == 'POST':
        transmission = request.form['transmission']
        query_details = VehicleTransmission.query.filter_by(transmission=transmission).first()
        if query_details == None:
            data=VehicleTransmission(transmission)
            sql.session.add(data)
            sql.session.commit()
            flash('Vehicle Transmission Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Vehicle Transmission already exists! Please enter another vehicle use"
            return render_template('home/policies.html', error = error)
    return render_template("/home/policies.html",success=success,error=error)

@blueprint.route("/delete_transmission/<uid>", methods=['GET'])
@login_required
def delete_transmission(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "VTransmission" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Vehicle Transmission Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))

@blueprint.route("/add_fuel", methods=['POST', 'GET'])
@login_required
def add_fuel():
    error=None
    success=None
    if request.method == 'POST':
        fuel = request.form['fuel']
        query_details = VehicleFuel.query.filter_by(fuel=fuel).first()
        if query_details == None:
            data=VehicleFuel(fuel)
            sql.session.add(data)
            sql.session.commit()
            flash('Vehicle Fuel Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Vehicle Fuel already exists! Please enter another vehicle use"
            return render_template('home/policies.html', error = error)
    return render_template("/home/policies.html",success=success,error=error)

@blueprint.route("/delete_fuel/<uid>", methods=['GET'])
@login_required
def delete_fuel(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "VFuel" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Vehicle Fuel Type Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))


@blueprint.route("/add_policy", methods=['POST', 'GET'])
@login_required
def add_policy():
    error=None
    success=None
    if request.method == 'POST':

        date = request.form['date']
        code = request.form['code']
        name = request.form['name']
        cost = request.form['cost']
        document = request.files['document']
        # check if the post request has the file part
        if 'document' not in request.files:
            error = "No file Part present"
    
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        elif document.filename == '':
            error = "No File Selected"


        query_details = Policies.query.filter_by(name=name).first()
        code_details = Policies.query.filter_by(code=code).first()
        if query_details == None & code_details ==None:
            if document:
                filename = secure_filename(document.filename)
                document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                success = "File Uploaded Successfully!"
                path = "apps/static/assets/uploads/"+document.filename

            document = filename
            data=Policies(date, code, name, cost, document)
            sql.session.add(data)
            sql.session.commit()
            flash('Policy Added', 'success')
            return redirect(url_for("home_blueprint.policiesindex"))
        else:
            success = None
            error = "Policy Name or Code already exists! Please enter another policy name or code"
            return render_template('home/policies.html', error = error)
    return render_template("/home/add_policy.html",success=success,error=error)


@blueprint.route("/file-viewer/<uid>", methods=['POST', 'GET'])
@login_required
def fileviewer(uid):
    pdfFile = Policies.query.get_or_404(uid)
    return render_template('home/file-viewer.html',pdfFile=pdfFile)    


@blueprint.route("/edit_policy/<uid>", methods=['POST', 'GET'])
@login_required
def edit_policy(uid):
    success = None
    error = None
    if request.method == 'POST':
        date = request.form['date']
        code = request.form['code']
        name = request.form['name']
        cost = request.form['cost']
        document = request.files['document']
        # check if the post request has the file part
        if 'document' not in request.files:
            error = "No file Part present"
    
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        elif document.filename == '':
            error = "No File Selected"


        if document:
            filename = secure_filename(document.filename)
            document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = "File Uploaded Successfully!"
            path = "apps/static/assets/uploads/"+document.filename

        document = filename
        conn = connection()
        cur = conn.cursor()
        cur.execute('UPDATE "Policies" SET date=%s,code=%s,name=%s,cost=%s,document=%s where id=%s',(date, code, name, cost, document, uid))
        conn.commit()
        flash('Policy Updated', 'success')
        return redirect(url_for("home_blueprint.policiesindex"))
    conn = connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM "Policies" WHERE ID=%s',(uid,))
    data = cur.fetchall()
    cur.close()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    print(data[0])
    return render_template("/home/edit_policy.html", datas=data[0],success=success, error=error)


@blueprint.route("/delete_policy/<uid>", methods=['GET'])
@login_required
def delete_policy(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "Policies" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Policy Deleted', 'danger')
    return redirect(url_for("home_blueprint.policiesindex"))

@blueprint.route("/delete_response/<uid>", methods=['GET'])
@login_required
def delete_response(uid):
    conn = connection()
    cur = conn.cursor()
    cur.execute('delete from "feedback" where ID=%s', (uid,))
    conn.commit()
    curs=conn.cursor()
    curs.execute("ROLLBACK")
    conn.commit()
    flash('Feedback Response Deleted', 'danger')
    return redirect(url_for("home_blueprint.feedbackindex"))



# CUSTOMER FEEDBACK - In Progress

@blueprint.route('/feedback.html')
@login_required
def feedback():

    conn = connection()
    fbCount = Feedback.query.count()
    date = f"{datetime.now():%Y-%m-%d}"
    allDetails = FeedbackQuestions.query.all()

    cur1 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur1.execute('SELECT id, product FROM "Products" ORDER BY ID ASC')
    products = cur1.fetchall()

    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2.execute('SELECT id, reasons FROM "Reasons" ORDER BY ID ASC')
    reasons = cur2.fetchall()

    
    return render_template('home/feedback.html', segment="feedback",fbCount=fbCount,date=date, datas=allDetails,products=products,reasons=reasons)

# USER PROFILE
@blueprint.route("/editprofile",methods=['GET','POST'])
@login_required
def editprofile():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form['email']
        password = request.form['password']

        users = Users.query.filter_by(username=username).first()
        if users:
            hash_password=hash_pass(password)
            Users.query.filter_by(username=username).update(dict(password=hash_password,username=username, email=email))
            db.session.commit()
            flash ('User Updated Successfully', 'success')
            return redirect("/editprofile")
        else:
            flash('User not found!', 'danger')
            return redirect("/editprofile")

    return render_template("home/profile.html")


@blueprint.route('/churnfb')
@login_required
def churnfb():
    return redirect("https://sentry.io/", code=302)






