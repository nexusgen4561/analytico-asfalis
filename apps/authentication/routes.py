

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users

from apps.authentication.util import verify_pass

class Employees(db.Model):
    __tablename__ = 'Employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, unique=True)
    employee_name = db.Column(db.String(100), unique=True)
    employee_email = db.Column(db.String(256), unique=True)

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

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        employee_id = request.form['employee_id']
        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        empId = Employees.query.filter_by(employee_id=employee_id).first()

        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        if empId == None :
            return render_template('accounts/register.html',
                                   msg='Employee ID not found! Please contact your administrator',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        employee_email = Employees.query.filter_by(employee_email=email).first()

        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        if employee_email == None:
            return render_template('accounts/register.html',
                                   msg='Employee Email not found! Please contact your administrator',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login')) 

# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
