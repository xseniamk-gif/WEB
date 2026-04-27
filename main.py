import os
from datetime import datetime

from flask import jsonify
from flask import Flask, render_template, redirect, request, abort, url_for, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

from data import db_session
from data.tours import Tours, Category
from data.users import Users, UsersTypes, CartItem
from forms.editprofile import UsersForm

from forms.loginform import LoginForm
from forms.registerform import RegisterForm
from forms.toursforms import ToursForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# ДОБАВЬТЕ ЭТИ НАСТРОЙКИ
UPLOAD_FOLDER = os.path.join('static', 'img')  # Папка для загрузки фото
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Создаём папку если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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


@app.route("/tours/bus_tour")
def bus_tour():
    return render_template("bus_tours.html",
                           title="Главная страница", active_bus=True)


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
                           title='Контактная информация', active_cont=True)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UsersForm()
    db_sess = db_session.create_session()

    if form.validate_on_submit():
        user = db_sess.query(Users).filter(Users.id == current_user.id).first()
        if user:
            user.name = form.name.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.number = form.number.data
            user.about = form.about.data
            db_sess.commit()
            return redirect('/profile')

    form.name.data = current_user.name
    form.surname.data = current_user.surname
    form.email.data = current_user.email
    form.number.data = current_user.number
    form.about.data = current_user.about

    cart_items = db_sess.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    tours_in_cart = []
    for item in cart_items:
        tour = db_sess.query(Tours).filter(Tours.id == item.tour_id).first()
        if tour:
            tours_in_cart.append(tour)

    return render_template('profile.html',
                           title='Профиль пользователя',
                           form=form,
                           user=current_user,
                           tours_in_cart=tours_in_cart)


@app.route('/tour/inf/<int:id_>', methods=['GET', 'POST'])
def tours_detail(id_):
    db_sess = db_session.create_session()
    tour = db_sess.query(Tours).filter(Tours.id == id_).first()

    # Получаем информацию о корзине текущего пользователя
    cart_quantity = 0
    tours_in_cart_ids = []

    if current_user.is_authenticated:
        cart_items = db_sess.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        tours_in_cart_ids = [item.tour_id for item in cart_items]

        # Находим количество конкретного тура в корзине
        for item in cart_items:
            if item.tour_id == id_:
                cart_quantity = item.quantity
                break

    return render_template('tours_wor.html',
                           title='Детали тура',
                           tour=tour,
                           tours_in_cart_ids=tours_in_cart_ids,
                           cart_quantity=cart_quantity
                           )


@app.route('/add_to_cart/<int:tour_id>', methods=['POST'])
@login_required
def add_to_cart(tour_id):
    db_sess = db_session.create_session()

    tour = db_sess.query(Tours).filter(Tours.id == tour_id).first()
    if not tour:
        return redirect(request.referrer or url_for('all_tour'))

    cart_item = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.tour_id == tour_id
    ).first()

    current_quantity = cart_item.quantity if cart_item else 0

    if tour.free_pl > current_quantity:
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                tour_id=tour_id,
                quantity=1
            )
            db_sess.add(cart_item)
        db_sess.commit()

    return redirect(request.referrer or url_for('all_tour'))


@app.route('/remove_from_cart/<int:tour_id>', methods=['POST'])
@login_required
def remove_from_cart(tour_id):
    """Удаление конкретного тура из корзины"""
    db_sess = db_session.create_session()

    cart_item = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.tour_id == tour_id
    ).first()

    if cart_item:
        db_sess.delete(cart_item)
        db_sess.commit()

    return redirect(request.referrer or url_for('profile'))


@app.route('/decrease_cart/<int:tour_id>', methods=['POST'])
@login_required
def decrease_cart(tour_id):
    db_sess = db_session.create_session()

    cart_item = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.tour_id == tour_id
    ).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            db_sess.delete(cart_item)
        db_sess.commit()

    return redirect(request.referrer or url_for('all_tour'))


@app.route('/update_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart(cart_item_id):
    """Обновление количества товара в корзине"""
    db_sess = db_session.create_session()

    cart_item = db_sess.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()

    if cart_item:
        quantity = request.form.get('quantity', type=int)
        if quantity and quantity > 0:
            cart_item.quantity = quantity
        else:
            db_sess.delete(cart_item)
        db_sess.commit()

    return redirect('/cart')


@app.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    """Очистка всей корзины"""
    db_sess = db_session.create_session()

    # Находим все товары пользователя
    cart_items = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()

    # Удаляем каждый товар
    for item in cart_items:
        db_sess.delete(item)

    db_sess.commit()

    return redirect(request.referrer or url_for('profile'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    db_sess = db_session.create_session()
    tours_names = []
    total_price = 0
    error = None  # Добавьте переменную error

    cart_items = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()

    if not cart_items:
        return redirect('/cart')

    if request.method == 'POST':
        for item in cart_items:
            tour = db_sess.query(Tours).filter(Tours.id == item.tour_id).first()
            if tour:
                if tour.free_pl >= item.quantity:
                    tour.free_pl -= item.quantity
                else:
                    error = f"Недостаточно мест на тур '{tour.title}'. Доступно: {tour.free_pl}"
                    return render_template('checkout.html',
                                           title='Оформление заказа',
                                           cart_items=cart_items,
                                           total_price=total_price,
                                           user=current_user,
                                           tours_names=tours_names,
                                           error=error)

        for item in cart_items:
            db_sess.delete(item)
        db_sess.commit()

        return render_template('checkout_success.html',
                               title='Заказ оформлен')

    for item in cart_items:
        tour = db_sess.query(Tours).filter(Tours.id == item.tour_id).first()
        if tour:
            total_price += tour.price * item.quantity
            tours_names.append([tour.title, tour.price, item.quantity, tour.free_pl])  # Добавили free_pl

    return render_template('checkout.html',
                           title='Оформление заказа',
                           cart_items=cart_items,
                           total_price=total_price,
                           user=current_user,
                           tours_names=tours_names,
                           error=error)


@app.route('/tours/active')
@app.route('/all_tour')
def all_tour():
    db_sess = db_session.create_session()
    tours = db_sess.query(Tours).all()

    # Получаем товары в корзине для авторизованного пользователя
    tours_in_cart_ids = []
    if current_user.is_authenticated:
        cart_items = db_sess.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).all()
        tours_in_cart_ids = [item.tour_id for item in cart_items]

    return render_template('all_tour.html',
                           title='Список всех туров',
                           tours=tours,
                           active=True,
                           tours_in_cart_ids=tours_in_cart_ids)


@app.route('/tours/active/hiking')
def active_hiking():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.name == 'Походы').first()
    if category:
        tours = db_sess.query(Tours).filter(Tours.category_id == category.id).all()
    else:
        tours = []
    return render_template('all_tour.html',
                           title='Походы',
                           tours=tours,
                           current_category='Походы', active=True)


@app.route('/tours/active/biking')
def active_biking():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.name == 'Велопрогулки').first()
    if category:
        tours = db_sess.query(Tours).filter(Tours.category_id == category.id).all()
    else:
        tours = []
    return render_template('all_tour.html',
                           title='Велопрогулки',
                           tours=tours,
                           current_category='Велопрогулки', active=True)


@app.route('/tours/active/rafting')
def active_rafting():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.name == 'Сплавы').first()
    if category:
        tours = db_sess.query(Tours).filter(Tours.category_id == category.id).all()
    else:
        tours = []
    return render_template('all_tour.html',
                           title='Сплавы',
                           tours=tours,
                           current_category='Сплавы', active=True)


@app.route('/tours/active/pilgrimage')
def active_pilgrimage():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.name == 'Паломничество').first()
    if category:
        tours = db_sess.query(Tours).filter(Tours.category_id == category.id).all()
    else:
        tours = []
    return render_template('all_tour.html',
                           title='Паломничество',
                           tours=tours,
                           current_category='Паломничество', active=True)


@app.route('/tours/active/excursions')
def active_excursions():
    db_sess = db_session.create_session()
    category = db_sess.query(Category).filter(Category.name == 'Экскурсии').first()
    if category:
        tours = db_sess.query(Tours).filter(Tours.category_id == category.id).all()
    else:
        tours = []
    return render_template('all_tour.html',
                           title='Экскурсии',
                           tours=tours,
                           current_category='Экскурсии')


@app.route('/tour/<int:id_>', methods=['GET', 'POST'])
def tours_edit(id_):
    form = ToursForm()
    db_sess = db_session.create_session()

    # Заполняем choices для категорий
    categories = db_sess.query(Category).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "GET":
        tour = db_sess.query(Tours).filter(Tours.id == id_).first()
        if tour:
            form.title.data = tour.title
            form.price.data = tour.price
            form.duration.data = tour.duration
            form.content.data = tour.content
            form.free_pl.data = tour.free_pl
            form.category.data = tour.category_id
            form.is_published.data = tour.is_published
        else:
            abort(404)

    if form.validate_on_submit():
        tour = db_sess.query(Tours).filter(Tours.id == id_).first()
        if tour and current_user.user_type_id == 1:  # Только админ может редактировать
            tour.title = form.title.data
            tour.price = form.price.data
            tour.duration = form.duration.data
            tour.content = form.content.data
            tour.free_pl = form.free_pl.data
            tour.category_id = form.category.data
            tour.is_published = form.is_published.data

            # ПРАВИЛЬНАЯ ОБРАБОТКА ФАЙЛА
            if form.img.data and form.img.data.filename:  # Проверяем, что файл выбран
                file = form.img.data
                if allowed_file(file.filename):
                    # Удаляем старое фото если оно не default.jpg
                    if tour.img and tour.img != 'default.jpg':
                        old_file = os.path.join(app.config['UPLOAD_FOLDER'], tour.img)
                        if os.path.exists(old_file):
                            os.remove(old_file)

                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_filename = f"{name}_{timestamp}{ext}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    file.save(file_path)
                    tour.img = new_filename
                    print(f"Фото сохранено: {new_filename}")

            db_sess.commit()
            return redirect('/all_tour')
        else:
            abort(404)

    return render_template('tours_red.html',
                           title='Редактирование тура', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/tour', methods=['GET', 'POST'])
@login_required
def tours_add():
    form = ToursForm()
    db_sess = db_session.create_session()

    # Заполняем choices для категорий
    categories = db_sess.query(Category).all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            tour = Tours()
            tour.title = form.title.data
            tour.price = form.price.data
            tour.duration = form.duration.data
            tour.content = form.content.data
            tour.free_pl = form.free_pl.data
            tour.category_id = form.category.data
            tour.is_published = form.is_published.data

            tour.user_id = current_user.id  # ВАЖНО: добавляем user_id
            if form.img.data and allowed_file(form.img.data.filename):
                file = form.img.data
                filename = secure_filename(file.filename)
                # Добавляем timestamp для уникальности
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{name}_{timestamp}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                tour.img = filename
            else:
                tour.img = 'default.jpg'
            db_sess.add(tour)
            db_sess.commit()

            print(f"Тур успешно добавлен: {tour.title}")
            return redirect('/all_tour')

        except Exception as e:
            print(f"Ошибка при добавлении тура: {e}")
            db_sess.rollback()
            return render_template('tours_red.html',
                                   title='Добавление тура',
                                   form=form,
                                   message=f"Ошибка: {str(e)}")

    # Для GET запроса или если форма не прошла валидацию
    return render_template('tours_red.html', title='Добавление тура', form=form)


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





@app.route('/api/tours')
def api_tours():
    db_sess = db_session.create_session()
    tours = db_sess.query(Tours).all()
    data = [{'id': t.id, 'title': t.title, 'price': t.price} for t in tours]
    return jsonify(data)


@app.route('/api/tours/<int:tour_id>')
def api_tour(tour_id):
    db_sess = db_session.create_session()
    tour = db_sess.query(Tours).get(tour_id)
    if not tour:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'id': tour.id, 'title': tour.title, 'price': tour.price})


def main():
    db_session.global_init("db/base.db")
    app.run(debug=True, port=5000, host='0.0.0.0')


if __name__ == '__main__':
    main()
