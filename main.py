import logging
import os
import datetime

from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFError, CSRFProtect

from data import db_session
from data.tours import Tours, Category
from data.users import Users, UsersTypes

from forms.loginform import LoginForm
from forms.registerform import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# защита форм
csrf = CSRFProtect(app)

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """функция для получения пользователя"""
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def main_first():
    return render_template("main_first.html",
                           title="Главная страница")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()

        # Проверка на существующую почту
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже есть")

        # Проверка на существующий логин
        if db_sess.query(Users).filter(Users.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким логином уже есть")

        user = Users(
            login=form.login.data,
            name=form.name.data,
            surname=form.surname.data,
            number=form.number.data,
            about=form.about.data,
            email=form.email.data,
            user_type_id=2  # Обычный пользователь
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        # Автоматический вход после регистрации
        login_user(user, remember=True)

        return redirect('/')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html',
                           title='Контактная информация')

@app.route('/all_tour')
@app.route('/tours/active')
def all_tour():
    db_sess = db_session.create_session()
    tours = db_sess.query(Tours).all()
    return render_template('all_tour.html',
                           title='Список всех туров', tours=tours)
# Если нужно больше маршрутов для конкретных категорий
@app.route('/tours/active/hiking')
def active_hiking():
    return render_template('all_tour.html', category='Походы')

@app.route('/tours/active/biking')
def active_biking():
    return render_template('all_tour.html', category='Велопрогулки')

@app.route('/tours/active/rafting')
def active_rafting():
    return render_template('all_tour.html', category='Сплавы')

@app.route('/tours/active/pilgrimage')
def active_pilgrimage():
    return render_template('all_tour.html', category='Паломничество')

@app.route('/tours/active/excursions')
def active_excursions():
    return render_template('all_tour.html', category='Экскурсии')

@app.route('/tours/bus_tour')
def bus_tour():
    return render_template('bus_tour.html')

@app.route('/about')
def about():
    return render_template('about.html',
                           title='О проекте')

#
# @app.errorhandler(CSRFError)
# def csrf_error(reason):
#     return render_template('error.html', reason=reason)
#
#
# @app.errorhandler(404)
# def error_404(error):
#     return render_template('error.html',
#                            title='ОШИБКА 404',
#                            reason='Страница не найдена')
#
#
# @app.errorhandler(403)
# def error_403(error):
#     return render_template('error.html',
#                            title='ОШИБКА 403',
#                            reason='Доступ запрещен')
#
#
# @login_manager.unauthorized_handler
# def unauth_handler():
#     return render_template('error.html',
#                            title='Доступ запрещен',
#                            reason='Авторизуйтесь чтобы получить доступ.')


def main():
    db_session.global_init("db/base.db")
    app.run(debug=True, port=5000)


if __name__ == '__main__':
    main()