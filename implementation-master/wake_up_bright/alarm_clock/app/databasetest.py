import datetime
import unittest
from wake_up_bright.alarm_clock.app import create_app
from wake_up_bright.alarm_clock.app.crud.controllers import AlarmDao, CollectionDao, PersonDao
from wake_up_bright.alarm_clock.app.crud.models import db, Person, Alarm



alarmservice = AlarmDao()
collectionservice = CollectionDao()
personservice = PersonDao()


class databasetest(unittest.TestCase):

    def setUp(self):
        app = create_app()
        db.app = app
        db.init_app(app)
        app.config['TESTING'] = True

    def tearDown(self):
        pass

    def test_case1(self):
        db.drop_all()
        db.create_all()
        us1 = Person(name="wang", age=32, gender="male")
        us2 = Person(name="zhang", age=1, gender="female")
        us3 = Person(name="chen", age=22, gender="IDK")
        us4 = Person(name="zhou", age=24, gender="futa")
        db.session.add_all([us1, us2, us3, us4])
        print("reached here!!!!!!!!!!!!")
        print(personservice.list_all())
        chen = personservice.get_person_by_name("chen")
        self.assertTrue(chen in personservice.list_all())

    def test_case2(self):

        chen = personservice.get_person_by_name("chen")
        chen.age = 12
        personservice.update_person(chen)
        self.assertEquals(chen.age, 12)

    def test_case3(self):
        zhou = personservice.get_person_by_name("zhou")
        personservice.delete_person(zhou)
        self.assertFalse(zhou in personservice.list_all())

    def test_case4(self):
        ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        at = datetime.time(8, 30)
        at1 = datetime.time(8, 35)
        alarmservice.create_Alarm(ct, at, at1, 5, ct, 2, 1)
        alarm1 = alarmservice.get_alarm(1)
        self.assertTrue(alarm1 in alarmservice.list_all())

    def test_case5(self):
        alarm1 = alarmservice.get_alarm(1)
        self.assertTrue(alarm1.on_off, 1)
        aid = alarmservice.use_alarm_time_and_change_on_off("08:30")
        self.assertTrue(aid, 1)
        self.assertEqual(alarmservice.get_alarm(aid).on_off, 0)

    def test_case6(self):
        alarm1 = alarmservice.get_alarm(1)
        self.assertEqual(str(alarm1.alarm_time_max), "08:35:00")
        aid = alarmservice.use_alarm_time_and_change_at1("08:30", "14:00")
        self.assertEqual(aid, 1)
        self.assertEqual(str(alarmservice.get_alarm(aid).alarm_time_max), "14:00:00")

    def test_case7(self):
        alarm1 = alarmservice.get_alarm(1)
        self.assertTrue(alarm1.snooze_time, 5)
        alarm1.snooze_time = 10
        alarm2 = alarmservice.update_alarm(alarm1)
        self.assertEqual(alarmservice.get_alarm(alarm2.aid).snooze_time, 10)

    def test_case8(self):
        ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        collectionservice.create_collection(1, 1, ct, 1)
        time1 = (datetime.datetime.now()+datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        time2 = (datetime.datetime.now()+datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
        ct1 = datetime.datetime.now().strftime("%Y-%m-%d")
        cl = collectionservice.get_collection(1)
        self.assertEqual((collectionservice.get_collection(1)).move_detection_sensor1, 1)
        cl.move_detection_sensor1 = 0
        collectionservice.update_collection(cl)
        self.assertEqual((collectionservice.get_collection(1)).move_detection_sensor1, 0)
        self.assertTrue(collectionservice.get_collection(1) in collectionservice.list_all())
        self.assertTrue(collectionservice.get_collection(1).collected_time, list(collectionservice.list_one_day(ct1))[0])
        self.assertTrue(collectionservice.get_collection(1).collected_time, list(collectionservice.list_time_slot(time1, time2))[0])
        ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        collectionservice.create_collection(1, 0, ct, 1)
        self.assertEqual(collectionservice.get_collection(collectionservice.last_one()).move_detection_sensor2, 0)



if __name__ == '__main__':
    unittest.main()
