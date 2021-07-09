# coding: utf-8
from flask import Flask
from sqlalchemy import Column, Float, ForeignKey, Integer, Time
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Person(db.Model):
    __tablename__ = 'person'

    name = Column(VARCHAR(30), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(VARCHAR(30), nullable=False)
    uid = Column(Integer, primary_key=True)


class Alarm(db.Model):
    __tablename__ = 'alarm'

    current_time = Column(DATETIME(fsp=6), nullable=False)
    alarm_time = Column(Time, nullable=False)
    alarm_time_max = Column(Time, nullable=False)
    snooze_time = Column(Integer, nullable=False)
    current_date = Column(DATETIME(fsp=6), nullable=False)
    auid = Column(ForeignKey('person.uid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    on_off = Column(Integer, nullable=False)
    aid = Column(Integer, primary_key=True)

    person = relationship('Person', backref = "")


class Collection(db.Model):
    __tablename__ = 'collection'

    move_detection_sensor1 = Column(Integer, nullable=False)
    move_detection_sensor2 = Column(Integer, nullable=False)
    collected_time = Column(DATETIME(fsp=6), nullable=False)
    caid = Column(ForeignKey('alarm.aid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    cid = Column(Integer, primary_key=True)
    alarm = relationship('Alarm')


'''if __name__ == '__main__':
    db.drop_all()

    db.create_all()

    us1 = Person(name="wang", age=32, gender="male")
    us2 = Person(name="zhang", age=1, gender="female")
    us3 = Person(name="chen", age=22, gender="IDK")
    us4 = Person(name="zhou", age=24, gender="futa")
    db.session.add_all([us1, us2, us3, us4])
    db.session.commit()

    app.run(debug=True) 
'''