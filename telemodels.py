import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


# Таблица для хранения информации о пользователях
class Teleusers(Base):
    __tablename__ = "teleusers"

    id = sq.Column(sq.Integer, primary_key=True)
    userid = sq.Column(sq.String, unique=True)
    userwords = relationship("Userwords", back_populates="users")


# Таблица для базового списка слов
class Telewords(Base):
    __tablename__ = "telewords"

    id = sq.Column(sq.Integer, primary_key=True)
    rusname = sq.Column(sq.String(length=255), nullable=False)
    engname = sq.Column(sq.String(length=255), nullable=False)


# Таблица для списка слов для каждого пользователя
class Userwords(Base):
    __tablename__ = "userwords"

    id = sq.Column(sq.Integer, primary_key=True)
    userid = sq.Column(sq.Integer, sq.ForeignKey("teleusers.id"), nullable=False)
    rusname = sq.Column(sq.String(length=255), nullable=False)
    engname = sq.Column(sq.String(length=255), nullable=False)
    users = relationship("Teleusers", back_populates="userwords")


# Функция для создания таблиц
def create_tables(engine):
    Base.metadata.create_all(engine)


# Функция для удаления таблиц
def drop_tables(engine):
    Base.metadata.drop_all(engine)
