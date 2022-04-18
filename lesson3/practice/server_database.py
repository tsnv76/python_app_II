from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, \
    ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import SERVER_DATABASE
import datetime


# Серверная база данных
class ServerStorage:
    # Таблица всех пользователей
    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

    # Таблица активных пользователей
    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # Таблица истории входов
    class LoginHistory:
        def __init__(self, name, date, ip_address, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip_address = ip_address
            self.port = port

    def __init__(self):
        # Создаем движок базы
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)

        # Создаем объект MetaData
        self.metadata = MetaData()

        # Создаем таблицу пользователей
        users_table = Table('Users', self.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('name', String, unique=True),
                           Column('last_login', DateTime)
                           )

        # Создаем таблицу активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # Создает таблицу истории входов
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip_address', String),
                                   Column('port', Integer)
                                   )

        # Создание таблиц
        self.metadata.create_all(self.database_engine)

        # Связываем классы с таблицами
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        # Создание сессии
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Очищаем таблицу активных пользователей после установки соединения
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Функция записи входа пользователя в базу
    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)

        # Проверяем в базе пользователя с таким именем
        res = self.session.query(self.AllUsers).filter_by(name=username)

        # Если имя пользователя уже есть - обновляем время входа,
        # если нет - создаем нового пользователя
        if res.count():
            user = res.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        # Создаем запись в таблицу активных пользователей о факте входа пользователя
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # Добавляем запись в историю входа пользователя
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохраняем все изменения
        self.session.commit()

    # Функция записи выхода пользователя
    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        # Удаляем его из таблицы активных пользователей.
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        # Применяем изменения
        self.session.commit()

    # Функция возвращает всех пользователей со временем последнего входа
    def users_list(self):
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login)
        return query.all()

    # Функция возвращает всех активных пользователей
    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
            ).join(self.AllUsers)
        return query.all()

    # Функция возвращает историю входа всех пользователей или одного пользователя
    def login_history(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip_address,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('user1', '192.168.1.10', 1111)
    test_db.user_login('user2', '192.168.1.20', 2222)
    test_db.user_login('user3', '192.168.1.30', 3333)
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя
    test_db.user_logout('user2')
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # запрашиваем историю входов по пользователю
    test_db.login_history('user3')
    # выводим список известных пользователей
    print(test_db.users_list())

