import logging
import os
import datetime

from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from flask_wtf import CsrfProtect
from flask_wtf.csrf import CSRFError, CSRFProtect

from data import db_session
# from data.comments import Comments
from data.tours import Tours, Category
from data.users import Users, UsersTypes

from flask_restful import reqparse, abort, Api, Resource

from waitress import serve
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from flask import Flask, render_template, redirect, make_response, jsonify, request, abort
from sqlalchemy.orm.collections import collection

from forms.loginform import LoginForm
from forms.registerform import RegisterForm
from forms.toursforms import ToursForm
from forms.userforms import UserForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# защита форм

# защита форм
csrf = CSRFProtect(app)



# Затем сразу после создания приложения flask инициализируем LoginManager
login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    """
    функция для получения пользователя, украшенная декоратором login_manager.user_loader
    """
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
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже есть")

        user = Users(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")




@app.route('/tours/admin_red', methods=['GET', 'POST'])
@login_required
def edit_tous(id_):
    form = ToursForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in db_sess.query(Category).all()]
    if request.method == "GET":

        news = db_sess.query(News).filter(News.id == id_,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_published.data = news.is_published
            form.category.data = news.category_id
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id_).first()
        if news and current_user.user_type_id == 1:
            news.title = form.title.data
            news.content = form.content.data
            news.is_published = form.is_published.data
            news.category_id = form.category.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('tours_red.html',
                           title='Редактирование новости',
                           category=categories,
                           form=form)

@app.route('/tours/admin_publ', methods=['GET', 'POST'])
@login_required
def publ_tous(id_):
    form = ToursForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    form.category.choices = [(i.id, i.name) for i in db_sess.query(Category).all()]
    if request.method == "GET":

        news = db_sess.query(News).filter(News.id == id_,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_published.data = news.is_published
            form.category.data = news.category_id
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id_).first()
        if news and current_user.user_type_id == 1:
            news.title = form.title.data
            news.content = form.content.data
            news.is_published = form.is_published.data
            news.category_id = form.category.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('tours_public.html',
                           title='Редактирование новости',
                           category=categories,
                           form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/news_delete/<int:id_>', methods=['GET', 'POST'])
@login_required
def tours_delete(id_):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(Tours.id == id_).first()
    if news and current_user.user_type_id == 1:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/category',  methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    if form.validate_on_submit():
        category = Category()
        category.name = form.name.data
        db_sess.add(category)
        db_sess.commit()
        return redirect('/')
    return render_template('category.html',
                           title='Добавление Категории',
                           category=categories,
                           form=form)


@app.route('/category/<int:id_>', methods=['GET', 'POST'])
@login_required
def category_edit(id_: int):
    form = CategoryForm()
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    if request.method == "GET":
        category = db_sess.query(Category).filter(Category.id == id_).first()
        if category and current_user.user_type_id == 1:
            form.category_id.data = category.id
            form.name.data = category.name
        else:
            abort(404)
    if form.validate_on_submit():
        category = db_sess.query(Category).filter(Category.id == id_).first()
        if category and current_user.user_type_id == 1:
            category.name = form.name.data
            db_sess.commit()
            return redirect('/categories')
        else:
            abort(404)
    return render_template('category.html',
                           title='Редактирование категорий',
                           category=categories,
                           form=form)


@app.route('/category_delete/<int:id_>', methods=['GET', 'POST'])
@login_required
def category_delete(id_: int):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.id == id_).first()
    if category and current_user.user_type_id == 1:
        db_sess.delete(category)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/categories')


@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories_all():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    return render_template('categories.html',
                           title='Просмотр категорий',
                           category=categories)


@app.route('/users', methods=['GET', 'POST'])
@login_required
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(Users).all()
    categories = db_sess.query(Category).all()
    return render_template('users.html',
                           title='Просмотр пользователей',
                           category=categories,
                           users=users)


@app.route('/user_delete/<int:id_>', methods=['GET', 'POST'])
@login_required
def user_delete(id_: int):
    db_sess = db_session.create_session()
    user = db_sess.query(Users).filter(Users.id == id_).first()
    if user == current_user:
        abort(403)
    elif user and current_user.user_type_id == 1:
        if user.user_type_id == 1 and len(db_sess.query(Users).filter(Users.user_type_id == 1).all()) < 2:
            abort(403)
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/users')


@app.route('/user/<int:id_>', methods=['GET', 'POST'])
@login_required
def user_edit(id_: int):
    form = UserForm()
    db_sess = db_session.create_session()
    users_type = [(i.id, i.users_type) for i in db_sess.query(UsersTypes).all()]
    form.user_type_id.choices = users_type
    if request.method == "GET":
        user = db_sess.query(Users).filter(Users.id == id_).first()
        if user and current_user.user_type_id == 1:
            form.name.data = user.name
            form.login.data = user.login
            form.email.data = user.email
            form.user_type_id.data = user.user_type_id
        else:
            abort(404)
    if form.validate_on_submit():
        user = db_sess.query(Users).filter(Users.id == id_).first()
        if user and current_user.user_type_id == 1:
            if form.password.data and form.password.data != form.password_again.data:
                return render_template("user.html",
                                       title="Редактирование пользователя",
                                       form=form,
                                       message="Пароли не совпадают")
            elif form.password.data:
                user.set_password(form.password.data)
            user.name = form.name.data
            user.login = form.login.data
            user.email = form.email.data
            # Админ не может себя понизить
            if current_user == user:
                pass
            else:
                user.user_type_id = form.user_type_id.data
            db_sess.commit()
            return redirect('/users')
        else:
            abort(404)
    return render_template('user.html',
                           title='Редактирование пользователя',
                           form=form)


@app.route('/contacts')
def contacts():
    db_sess = db_session.create_session()
    return render_template('contacts.html',
                           title='Контактная информация')


@app.route('/about')
def about():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).all()
    return render_template('about.html',
                           title='О проекте',
                           category=category)


@app.errorhandler(CSRFError)
def csrf_error(reason):
    return render_template('error.html', reason=reason)


@app.errorhandler(404)
def error_404(error):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).all()
    return render_template('error.html',
                           title='ОШИБКА 404',
                           category=category,
                           reason='НЕНАЙДЕНО')


@app.errorhandler(403)
def error_403(error):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).all()
    return render_template('error.html',
                           title='ОШИБКА 403',
                           category=category,
                           reason='ЭТО НЕВОЗМОЖНО')


@app.login_manager.unauthorized_handler
def unauth_handler():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).all()
    return render_template('error.html',
                           title='Доступ запрещен',
                           category=category,
                           reason='Авторизуйтесь чтоб получить доступ.')


def main():
    db_session.global_init("db/base.db")
    # db_sess = db_session.create_session()
    port = int(os.environ.get('PORT', 5000))
    app.run()

    serve(app, port=port, host="127.0.0.1")


if __name__ == '__main__':
    main()
