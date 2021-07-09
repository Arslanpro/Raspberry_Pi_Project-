import datetime

from wake_up_bright.alarm_clock.app.crud.controllers import AlarmDao, CollectionDao, PersonDao
from wake_up_bright.alarm_clock.app.crud.models import db, Person, Alarm
from wake_up_bright.alarm_clock.app import create_app

app = create_app()
db.app = app
db.init_app(app)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    us1 = Person(name="wang", age=32, gender="male")
    us2 = Person(name="zhang", age=1, gender="female")
    us3 = Person(name="chen", age=22, gender="IDK")
    us4 = Person(name="zhou", age=24, gender="futa")
    db.session.add_all([us1, us2, us3, us4])
    '''
    '''

    ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    at = datetime.time(8, 30)
    at1 = datetime.time(8, 35)
    #alarm1 = Alarm(current_time=ct, alarm_time=at, time_range=15, snooze_time=10, current_date=ct, auid=1)
    #db.session.add(alarm1)
    #db.session.commit()
    alarmservice = AlarmDao()
    alarmservice.create_Alarm(ct, at, at1, 5, ct, 2, 1)
    '''
    '''
    collectionservice = CollectionDao()
    ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collectionservice.create_collection(1, 1, ct, 1)
    personservice = PersonDao()
    print(personservice.list_all())
    personservice.delete_person(us4)
    us3.gender = "redneg"
    personservice.update_person(us3)

    db.session.commit()
    print(alarmservice.user_alarm(personservice.get_person_by_name("zhang"), "08:30"))
    print(collectionservice.list_time_slot("2020-11-01 15:04:00", "2020-11-29 16:05:00"))
    print(alarmservice.use_alarm_time_and_change_on_off("08:30"))
    print(alarmservice.use_alarm_time_and_change_at1("08:30", "14:00"))
    print(alarmservice.use_alarm_time_and_change_on_off("08:30"))
    ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collectionservice.create_collection(1, 0, ct, 1)
    print(collectionservice.last_one())
    print(collectionservice.get_collection(collectionservice.last_one()))
    print("Done!!")
