import traceback

import sqlalchemy
import json
import sqlalchemy.orm
import telemodels
import configparser


# Функция, которая создаёт сессию для подключения к БД
def configurate_session():
    config = configparser.ConfigParser()
    config.read("settings1.ini")
    login = config['Db']['login']
    dbname = config['Db']['dbname']
    password = config['Db']['password']

    DSN = f"postgresql://{login}:{password}@localhost:5432/{dbname}"
    engine = sqlalchemy.create_engine(DSN)

    telemodels.drop_tables(engine)
    telemodels.create_tables(engine)

    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    return session

#Функция для создания базового набор слов и добавления их в таблицу Telewords
def add_common_data():
    common_words = {'Peace': 'Мир', 'One': 'Один',
                    'Session': 'Сессия', 'Query': 'Запрос',
                    'Database': 'База данных', 'Morning': 'Утро',
                    'India': 'Индия', 'Code': 'Код',
                    'Dew': 'Роса', 'Grass': 'Трава'}
    for eng, rus in common_words.items():
        stroka = telemodels.Telewords(rusname=rus, engname=eng)
        session.add(stroka)
    session.commit()

#Функция для передачи базового набора слов для конкретного пользователя
def insert_common_data(chat_id):
    common = session.query(telemodels.Telewords.engname,telemodels.Telewords.rusname)
    q = session.query(telemodels.Teleusers.id).filter(telemodels.Teleusers.userid == chat_id)
    userid = int(q.all()[0][0])
    for r in common.all():
        data = telemodels.Userwords(engname = r.engname,rusname = r.rusname, userid = userid)
        session.add(data)
        session.commit()

#Функция по получению списка доступных слов для изучения
def get_data():
    q = session.query(telemodels.Userwords.id,telemodels.Userwords.rusname,telemodels.Userwords.engname)
    values = {}
    for rt in q.all():
        values[rt.engname] = rt.rusname
    return values

#Функция по добавлению ID пользователя в таблицу Teleusers
def add_user(chat_id,):
    try:
        session.add(telemodels.Teleusers(userid = chat_id))
        session.commit()
    except:
        session.rollback()

#Функция по добавлению нового слова для пользователя
def add_word(chat_id, engname, rusname):

    q = session.query(telemodels.Teleusers.id).filter(telemodels.Teleusers.userid == chat_id)
    userid = int(q.all()[0][0])
    newword = telemodels.Userwords(userid = userid, rusname = rusname, engname = engname)
    session.add(newword)
    session.commit()

#Функция по удалению слова для пользователя
def delete_word(chat_id, rusname):
    q2 = session.query(telemodels.Teleusers.id).filter(telemodels.Teleusers.userid == chat_id)
    userid = int(q2.all()[0][0])
    q = session.query(telemodels.Userwords).filter(telemodels.Userwords.userid == userid,telemodels.Userwords.rusname == rusname )
    q.delete()
    session.commit()


session = configurate_session()
