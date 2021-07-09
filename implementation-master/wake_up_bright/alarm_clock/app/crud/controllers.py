from sqlalchemy import desc

from wake_up_bright.alarm_clock.app.crud.models import db
from wake_up_bright.alarm_clock.app.crud.models import Person, Alarm, Collection


class PersonDao():

    def create_person(self, new_name, new_age, new_gender):
        new_person = Person(name=new_name, age=new_age, gender=new_gender)
        db.session.add(new_person)
        db.session.commit()
        return new_person

    def update_person(self, person):
        modified_person = Person.query.get(person.uid)
        modified_person.name = person.name
        modified_person.age = person.age
        modified_person.gender = person.gender
        db.session.commit()

        return modified_person

    def delete_person(self, person):
        person_to_delete = Person.query.get(person.uid)
        db.session.delete(person_to_delete)
        db.session.commit()

        return person_to_delete

    def list_all(self):
        return Person.query.order_by(desc(Person.uid)).all()

    def get_person(self, uid):
        return Person.query.get(uid)

    def get_person_by_name(self, name):
        # there should not be same name person, anyway we are designing it for a single user.
        person = Person.query.filter(Person.name == name).first()

        return person


class AlarmDao():

    def create_Alarm(self, current_time, alarm_time, alarm_time_max, snooze_time, current_date, auid, on_off):
        new_alarm = Alarm(current_time=current_time, alarm_time=alarm_time, alarm_time_max=alarm_time_max,
                          snooze_time=snooze_time, current_date=current_date, on_off=on_off, auid=auid)
        db.session.add(new_alarm)
        db.session.commit()
        return new_alarm

    def update_alarm(self, alarm):
        modified_alarm = Alarm.query.get(alarm.aid)
        modified_alarm.current_time = alarm.current_time
        modified_alarm.start_wake_up_period = alarm.start_wake_up_period
        modified_alarm.alarm_time_max = alarm.alarm_time_max
        modified_alarm.snooze_time = alarm.snooze_time
        modified_alarm.current_date = alarm.current_date
        modified_alarm.auid = alarm.auid
        modified_alarm.on_off = alarm.on_off
        db.session.commit()

        return modified_alarm

    def delete_alarm(self, alarm):
        alarm_to_delete = Alarm.query.get(alarm.aid)
        db.session.delete(alarm_to_delete)
        db.session.commit()

        return alarm_to_delete

    def list_all(self):
        return Alarm.query.order_by(desc(Alarm.aid)).all()

    def get_alarm(self, aid):
        return Alarm.query.get(aid)

    def alarm_on_off(self, aid):
        alarm = Alarm.query.get(aid)
        return alarm.on_off

    def user_alarm(self, person, date):
        # usage
        '''
        user_alarm(get_person_by_name(name),"2020-10-29 14:45")
        :param person:
        :param date:
        :return:
        '''
        # date = "2020-10-29 14:45"
        auid = person.uid
        ss = date
        sql = "select * from alarm where DATE_FORMAT(alarm_time,'%H:%i')=" \
              + "'" + ss + "'" + "AND alarm.auid=" + "'" + str(auid) + "'"
        rets = db.session.execute(sql).fetchall()
        res1 = {}
        print(rets)
        for ret in rets:
            print(ret.aid)
            res1[ret.aid] = [str(ret.start_wake_up_period), str(ret.alarm_time_max), ret.snooze_time, ret.on_off]
        return res1

    def use_alarm_time_and_change_on_off(self, date):

        # date = "04:45"
        ss = date
        sql = "select * from alarm where DATE_FORMAT(alarm_time,'%H:%i')=" \
              + "'" + ss + "'"
        rets = db.session.execute(sql).fetchone()
        alarmservice = AlarmDao()
        alarm = alarmservice.get_alarm(rets.aid)
        if alarm.on_off == 1:
            alarm.on_off = 0
        else:
            alarm.on_off = 1
        alarmservice.update_alarm(alarm)
        return alarm.aid

    def use_alarm_time_and_change_at1(self, date, new_at1):
        # date = "04:45"
        ss = date
        sql = "select * from alarm where DATE_FORMAT(alarm_time,'%H:%i')=" \
              + "'" + ss + "'"
        rets = db.session.execute(sql).fetchone()
        alarmservice = AlarmDao()
        alarm = alarmservice.get_alarm(rets.aid)
        alarm.alarm_time_max = new_at1
        alarmservice.update_alarm(alarm)
        return alarm.aid


class CollectionDao():

    def create_collection(self, move_detection_sensor1, move_detection_sensor2, collected_time, caid):
        new_collection = Collection(move_detection_sensor1=move_detection_sensor1,
                                    move_detection_sensor2=move_detection_sensor2,
                                    collected_time=collected_time, caid=caid)
        db.session.add(new_collection)
        db.session.commit()
        return new_collection

    def update_collection(self, collection):
        modified_collection = Collection.query.get(collection.cid)
        modified_collection.move_detection_sensor1 = collection.move_detection_sensor1
        modified_collection.move_detection_sensor2 = collection.move_detection_sensor2
        modified_collection.collected_time = collection.collected_time
        modified_collection.caid = collection.caid

        db.session.commit()

        return modified_collection

    def delete_collection(self, collection):
        collection_to_delete = Collection.query.get(collection.cid)
        db.session.delete(collection_to_delete)
        db.session.commit()

        return collection_to_delete

    def list_all(self):
        return Collection.query.order_by(desc(Collection.cid)).all()

    def get_collection(self, cid):
        return Collection.query.get(cid)

    def list_one_day(self, date):
        # date = "2020-10-26" for example
        dic = {}
        ss = date
        sql = "select * from collection where DATE_FORMAT(collected_time,'%Y-%m-%d')=" + "'" + ss + "'"
        ret = db.session.execute(sql).fetchall()
        for one in ret:
            dic[str(one.collected_time)] = [one.move_detection_sensor1, one.move_detection_sensor2]
        return dic

    def list_time_slot(self, date1, date2):
        # date1 = "2020-10-28 12:00:00" for example
        # date2 = "2020-10-29 04:00:00" for example
        dic = {}
        sql = "select * from collection where collected_time between " + "'" + date1 + "'" + "and" + "'" + date2 + "'"
        ret = db.session.execute(sql).fetchall()
        for one in ret:
            dic[str(one.collected_time)] = [one.move_detection_sensor1, one.move_detection_sensor2]
        return dic

    def last_one(self):

        sql = "SELECT LAST_INSERT_ID() FROM project.collection"
        rets = db.session.execute(sql).fetchone()
        return rets
