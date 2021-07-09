# coding: utf-8
from flask import Flask
from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123@127.0.0.1:3306/project"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

Base = declarative_base()
metadata = Base.metadata


class Person(db.Model):
    __tablename__ = 'person'

    name = Column(VARCHAR(30), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(VARCHAR(30), nullable=False)
    uid = Column(Integer, primary_key=True)


class Alarm(db.Model):
    __tablename__ = 'alarm'

    current_time = Column(DATETIME(fsp=6), nullable=False)
    alarm_time = Column(DATETIME(fsp=6), nullable=False)
    time_range = Column(Integer, nullable=False)
    snooze_time = Column(Integer, nullable=False)
    current_date = Column(DATETIME(fsp=6), nullable=False)
    aid = Column(Integer, primary_key=True)
    auid = Column(ForeignKey('person.uid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    person = relationship('Person')


class Collection(db.Model):
    __tablename__ = 'collection'

    gx = Column(Float(32, True))
    gy = Column(Float(32, True))
    gz = Column(Float(32, True))
    ax = Column(Float(32, True))
    ay = Column(Float(32, True))
    az = Column(Float(32, True))
    cid = Column(Integer, primary_key=True)
    caid = Column(ForeignKey('alarm.aid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    alarm = relationship('Alarm')


if __name__ == '__main__':
    db.drop_all()

    db.create_all()

    us1 = Person(name="wang", age=32, gender="male")
    us2 = Person(name="zhang", age=1, gender="female")
    us3 = Person(name="chen", age=22, gender="IDK")
    us4 = Person(name="zhou", age=24, gender="futa")
    db.session.add_all([us1, us2, us3, us4])
    db.session.commit()

    app.run(debug=True)
