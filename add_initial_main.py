from data import db_session
from data.tours import Tours, Category
from data.users import Users, UsersTypes


def add_users_types(db_sess):
    """
    Создаем типы пользователей
    :param db_sess:
    :return:
    """
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


def add_user(db_sess):
    """
    для теста создаем юзеров
    :param db_sess:
    :return:
    """
    user1 = Users(name="Редактор",
                  login="admin",
                  email="email@adm.ru",
                  user_type_id=1,
                  hashed_password='1111'
                  )
    user2 = Users(name="Обычный пользователь",
                  login="user",
                  email="email1@nps.ru",
                  user_type_id=2,
                  hashed_password='111'
                  )
    user3 = Users(name="Прохожий",
                  login="user2",
                  email="email2@email.ru",
                  user_type_id=2,
                  hashed_password='111'
                  )
    user1.set_password(user1.hashed_password)
    user2.set_password(user2.hashed_password)
    user3.set_password(user3.hashed_password)
    db_sess.add(user1)
    db_sess.add(user2)
    db_sess.add(user3)
    db_sess.commit()


def add_category(db_sess):
    """
    для теста создаем категории
    :param db_sess:
    :return:
    Главное
    """
    raw = [
           'Походы',
        'Велопрогулки',
        'Сплавы'
           ]
    for n, name in enumerate(raw, 1):
        category = Category(name=name,
                            id=n)
        db_sess.add(category)

    db_sess.commit()


def add_tours(db_sess):
    """
    для теста создаем Новости
    :param db_sess:
    :return:
    """
    raw = [("Паломнический тур в Дивеево",
"""
<h2>О туре</h2>
<p>Дивеево — одно из самых почитаемых православных мест России. Здесь находится Свято-Троицкий Серафимо-Дивеевский монастырь, где покоятся мощи преподобного Серафима Саровского.</p>

<img alt="Свято-Троицкий Серафимо-Дивеевский монастырь" style="max-width: 620px; width: 100%; height: auto;" src="https://icdn.lenta.ru/images/2021/04/29/21/20210429211001209/pic_25688440a48a61637c4b3108521a0f5a.jpg">

<h2>Программа</h2>
<p><strong>День 1:</strong> Отправление из Чебоксар. Прибытие в Дивеево. Размещение. Экскурсия по монастырю. Прогулка по Святой Канавке.</p>
<p><strong>День 2:</strong> Посещение святых источников. Купание в купальне. Экскурсия в музей.</p>
<p><strong>День 3:</strong> Литургия. Сбор вещей. Экскурсия в Арзамас. Возвращение.</p>

<h2>Стоимость</h2>
<p>12 500 рублей с человека. Включено: трансфер, проживание, 3-разовое питание, экскурсии.</p>

<h2>Важно знать</h2>
<p>При себе иметь удобную закрытую обувь. Женщинам — платок и юбка. Для купания — длинная рубашка.</p>
""",
3)

    ]

    for line in raw:
        tours = Tours(content=line[1],
                    category_id=line[2],
                    title=line[0],
                    is_published=True,
                    user_id=1)
        db_sess.add(tours)
    db_sess.commit()


def main():
    db_session.global_init("db/base.db")
    db_sess = db_session.create_session()
    add_users_types(db_sess)
    add_user(db_sess)
    add_category(db_sess)
    add_tours(db_sess)


if __name__ == '__main__':
    main()
