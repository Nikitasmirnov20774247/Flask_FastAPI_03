from flask import Flask, render_template, request, redirect, url_for, session
from secrets import token_hex
from flask_wtf.csrf import CSRFProtect
from project.models import db, User
from project.forms import RegistrationForm, LoginForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ds3.db'
app.config['SECRET_KEY'] = token_hex()
csrf = CSRFProtect(app)
db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.cli.command('init_db')
def init_db():
    db.create_all()
    print('OK')


@app.route('/registration/', methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = form.password.data
        if not User.query.filter_by(email=email).first():
            user = User(name=name, surname=surname, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session['user'] = f'{user}'
            return redirect(url_for('index'))
        else:
            msg = ''
            if User.query.filter_by(email=email).first():
                msg = 'Данная почта уже используется!'
            return render_template('registration.html', form=form, msg=msg)
    return render_template('registration.html', form=form)


@app.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(password):
                session['user'] = str(user)
                return redirect(url_for('index'))
            else:
                msg = 'Неверный пароль!'
                return render_template('registration.html', form=form, msg=msg)
        else:
            msg = 'Логин не найден!'
            return render_template('registration.html', form=form, msg=msg)
    return render_template('registration.html', form=form)


@app.route('/logout/')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
