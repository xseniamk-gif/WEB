from data import db_session
from data.tours import Tours, Category
from data.users import Users, UsersTypes

def add_users_types(db_sess):
    """
    Создаем типы пользователей
    """
    # Очищаем таблицу перед добавлением
    db_sess.query(UsersTypes).delete()

    types1 = UsersTypes(id=1,
                        users_type="Администраторы")
    types2 = UsersTypes(id=2,
                        users_type="Обычные пользователи")
    types3 = UsersTypes(id=3,
                        users_type="Пользователи только для чтения")
    db_sess.add(types1)
    db_sess.add(types2)
    db_sess.add(types3)
    db_sess.commit()

    print("Добавлены типы пользователей")


def add_user(db_sess):
    """
    для теста создаем юзеров
    """
    user1 = Users(name="Администратор",
                  login="admin",
                  surname="",
                  number="",
                  about="Главный администратор",
                  email="admin@example.ru",
                  user_type_id=1,
                  hashed_password='admin123'
                  )
    user2 = Users(name="Обычный",
                  login="user",
                  surname="Пользователь",
                  number="+7 (123) 456-78-90",
                  about="Обычный пользователь",
                  email="user@example.ru",
                  user_type_id=2,
                  hashed_password='user123'
                  )

    user1.set_password(user1.hashed_password)
    user2.set_password(user2.hashed_password)

    db_sess.add(user1)
    db_sess.add(user2)
    db_sess.commit()

    print("Добавлены пользователи")


def add_category(db_sess):
    """
    для теста создаем категории
    """
    # Очищаем таблицу перед добавлением
    db_sess.query(Category).delete()

    raw = ['Походы', 'Велопрогулки', 'Сплавы', 'Паломничество', 'Экскурсии']
    for n, name in enumerate(raw, 1):
        category = Category(name=name, id=n)
        db_sess.add(category)
    db_sess.commit()

    print("Добавлены категории")


def add_tours(db_sess):
    """
    для теста создаем туры
    """
    # Очищаем таблицу перед добавлением
    db_sess.query(Tours).delete()

    raw = [
        (3, "Паломнический тур в Дивеево",
         """
<h2>О туре</h2>
<p>Дивеево — одно из самых почитаемых православных мест России. Здесь находится Свято-Троицкий Серафимо-Дивеевский монастырь, где покоятся мощи преподобного Серафима Саровского.</p>
<h2>Программа</h2>
<p><strong>День 1:</strong> Отправление из Чебоксар. Прибытие в Дивеево. Размещение. Экскурсия по монастырю. Прогулка по Святой Канавке.</p>
<p><strong>День 2:</strong> Посещение святых источников. Купание в купальне. Экскурсия в музей.</p>
<p><strong>День 3:</strong> Литургия. Сбор вещей. Экскурсия в Арзамас. Возвращение.</p>
<h2>Стоимость</h2>
<p>12 500 рублей с человека.</p>
""",
         True,
         35,
         3,  # duration
         12500,  # price
         'дивеево.jpg'
         ),
        (0,  # Походы,
         "Горный Алтай",
         """
<h2>О туре</h2>
<p>Путешествие по живописным горам Алтая. Вас ждут невероятные пейзажи, горные озера и чистый воздух.</p>
<h2>Программа</h2>
<p><strong>День 1:</strong> Прибытие в Горно-Алтайск. Трансфер на базу.</p>
<p><strong>День 2-6:</strong> Ежедневные радиальные выходы в горы, посещение перевалов и озер.</p>
<p><strong>День 7:</strong> Отъезд.</p>
<h2>Стоимость</h2>
<p>45 000 рублей с человека.</p>
""",
         True,
         30,
         7,  # duration
         45000,
         'алтай.jpg'
         ),
    ]

    for line in raw:
        tour = Tours(
            title=line[1],
            content=line[2],
            category_id=line[0],
            duration=line[5],
            price=line[6],
            is_published=line[3],
            free_pl=line[4],
            user_id=1,
            img=line[7]# Администратор
        )
        db_sess.add(tour)
    db_sess.commit()

    print("Добавлены туры")


def main():
    db_session.global_init("db/base.db")
    db_sess = db_session.create_session()

    add_users_types(db_sess)
    add_user(db_sess)
    add_category(db_sess)
    add_tours(db_sess)

    print("\nБаза данных успешно заполнена!")


if __name__ == '__main__':
    main()