import logging
import os
import datetime

from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from flask_wtf import CsrfProtect
from flask_wtf.csrf import CSRFError, CSRFProtect
#
# from data import db_session, news_resources, users_resources
# from data.comments import Comments
# from data.news import News, Category
# from data.users import Users, UsersTypes
# from forms.category import CategoryForm
# from forms.comment import CommentForm
# from forms.news import NewsForm
# from forms.user import RegisterForm, LoginForm, UserForm

from flask_restful import reqparse, abort, Api, Resource

from waitress import serve
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from flask import Flask, render_template, redirect, make_response, jsonify, request, abort
from sqlalchemy.orm.collections import collection



app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# защита форм

# защита форм
csrf = CSRFProtect(app)

# # csrf отключено для API
# api = Api(app, decorators=[csrf.exempt])
# # для списка объектов
# api.add_resource(news_resources.NewsListResource, '/api/v2/news')
# api.add_resource(users_resources.UsersListResource, '/api/v2/users')
#
# # для одного объекта
# api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')
# api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')



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

@app.route("/<int:category_id>", methods=['GET', 'POST'])
def index(category_id: int = 0):
    form = CommentForm()
    db_sess = db_session.create_session()
    if category_id != 0:
        news = db_sess.query(News).filter(News.category_id == category_id).order_by(News.created_date.desc()).all()
    else:
        news = db_sess.query(News).order_by(News.created_date.desc()).all()

    categories = db_sess.query(Category).all()
    if not category_id:
        title = "Последние новости"
    else:
        title,  = [i.name for i in categories if i.id == category_id]
    if form.validate_on_submit():
        comment = Comments(content=form.content.data,
                           users_id=current_user.id,
                           news_id=int(form.news_id.data))
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f"/{category_id}")
    return render_template("index.html",
                           news=news,
                           form=form,
                           category=categories,
                           title=title)


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

        if db_sess.query(Users).filter(Users.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким логином уже есть")
        user = Users(
            name=form.name.data,
            login=form.login.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")




@app.route('/news/<int:id_>', methods=['GET', 'POST'])
@login_required
def edit_news(id_):
    form = NewsForm()
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
    return render_template('news.html',
                           title='Редактирование новости',
                           category=categories,
                           form=form)


@app.route('/news_delete/<int:id_>', methods=['GET', 'POST'])
@login_required
def news_delete(id_):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id_).first()
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
    category = db_sess.query(Category).all()
    return render_template('contacts.html',
                           title='Контактная информация',
                           category=category)


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
    # db_session.global_init("db/base.db")
    # db_sess = db_session.create_session()

    port = int(os.environ.get('PORT', 5000))
    # с дефаултными значениями будет не более 4 потоков
    app.run()

    serve(app, port=port, host="127.0.0.1")


if __name__ == '__main__':
    main()
