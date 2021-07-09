from flask import request, render_template, Blueprint, flash, redirect, url_for

from .forms import *
from flask import Blueprint
from .controllers import *

crud = Blueprint('crud', __name__, template_folder="templates", static_url_path='',
                 static_folder='templates/static')

@crud.route('/')
def index():
    return render_template('index.html')

@crud.route('/user/', methods=['GET'])
def user_index():
    personservice = PersonDao()
    persons = personservice.list_all()
    return render_template('user_index.html', persons=persons)


@crud.route('/user/new', methods=['GET', 'POST'])
def new_person():
    form = AddPersonForm()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        personservice = PersonDao()
        personservice.create_person(name, age, gender)

        return redirect(url_for('crud.user_index'))

    return render_template('user.html', form=form)


@crud.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_person(user_id):
    form = EditPersonForm()
    person_service = PersonDao()
    person = person_service.get_person(user_id)
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        person.age = age
        person.name = name
        person.gender = gender
        person_service.update_person(person)
        return redirect(url_for('crud.user_index'))

    form.name.data = person.name
    form.gender.data = person.gender
    form.age.data = person.age
    return render_template('edit_person.html', form=form)


@crud.route('/user/delete/<int:user_id>', methods=['GET'])
def delete_person(user_id):
    personservice = PersonDao()
    person = personservice.get_person(user_id)
    personservice.delete_person(person)

    return redirect(url_for('crud.user_index'))


@crud.route('/alarm')
def alarm_index():
    alarmservice = AlarmDao()
    alarms = alarmservice.list_all()
    return render_template('alarm.html', alarms=alarms)


@crud.route('/alarm/new', methods=['GET', 'POST'])
def new_alarm():
    form = AddAlarmForm()
    alarmservice = AlarmDao()
    if request.method == 'POST':
        current_time = request.form['current_time']
        alarm_time = request.form['alarm_time']
        alarm_time_max = request.form['alarm_time_max']
        snooze_time = request.form['snooze_time']
        current_date = request.form['current_date']
        auid = request.form['auid']
        on_off = request.form['on_off']

        alarmservice.create_Alarm(current_time, alarm_time, alarm_time_max, snooze_time, current_date, auid, on_off)

        return redirect(url_for('alarm.index'))

    return render_template('alarm.html', form=form)


@crud.route('/alarm/edit/<int:alarm_id>', methods=['GET', 'POST'])
def edit_alarm(alarm_id):
    form = EditAlarmForm()
    alarm_service = AlarmDao()
    alarm = alarm_service.get_alarm(alarm_id)
    if request.method == 'POST':
        current_time = request.form['current_time']
        alarm_time = request.form['alarm_time']
        alarm_time_max = request.form['alarm_time_max']
        snooze_time = request.form['snooze_time']
        current_date = request.form['current_date']
        on_off = request.form['on_off']
        alarm.current_time = current_time
        alarm.alarm_time_max = alarm_time_max
        alarm.start_wake_up_period = alarm_time
        alarm.snooze_time = snooze_time
        alarm.current_date = current_date
        alarm.on_off = on_off
        alarm_service.update_alarm(alarm)
        return redirect(url_for('person.index'))

    form.current_date.data = alarm.current_date
    form.current_time.data = alarm.current_time
    form.snooze_time.data = alarm.snooze_time
    form.alarm_time_max.data = alarm.alarm_time_max
    form.alarm_time.data = alarm.start_wake_up_period
    form.auid.data = alarm.auid
    form.on_off.data = alarm.on_off
    return render_template('edit_alarm.html', form=form)


@crud.route('/alarm/delete/<int:alarm_id>', methods=['GET'])
def delete_alarm(alarm_id):
    alarmservice = AlarmDao()
    alarm = alarmservice.get_alarm(alarm_id)
    alarmservice.delete_alarm(alarm)
    return redirect(url_for('alarm.index'))


@crud.route('/collection')
def collection_index():
    collectionservice = CollectionDao()
    collections = collectionservice.list_all()
    return render_template('collection.html', collections=collections)


@crud.route('/collection/new', methods=['GET', 'POST'])
def new_collection():
    form = AddCollectionForm()

    if request.method == 'POST':
        move_detection_sensor1 = request.form['move_detection_sensor1']
        move_detection_sensor2 = request.form['move_detection_sensor2']
        collected_time = request.form['collected_time']
        caid = request.form['caid']
        collectionservice = CollectionDao()
        collectionservice.create_collection(move_detection_sensor1=move_detection_sensor1,
                                            move_detection_sensor2=move_detection_sensor2,
                                            collected_time=collected_time, caid=caid)

        return redirect(url_for('collection.index'))

    return render_template('collection.html', form=form)


@crud.route('/collection/edit/<int:collection_id>', methods=['GET', 'POST'])
def edit_collection(collection_id):
    form = EditCollectionForm()
    collection_service = CollectionDao()
    collection = collection_service.get_collection(collection_id)
    if request.method == 'POST':
        move_detection_sensor1 = request.form['move_detection_sensor1']
        move_detection_sensor2 = request.form['move_detection_sensor2']
        collected_time = request.form['collected_time']
        caid = request.form['caid']
        collection.move_detection_sensor1 = move_detection_sensor1
        collection.move_detection_sensor2 = move_detection_sensor2
        collection.collected_time = collected_time
        collection.caid = caid
        collection_service.update_collection(collection)
        return redirect(url_for('collection.index'))

    form.move_detection_sensor1.data = collection.move_detection_sensor1
    form.move_detection_sensor2.data = collection.move_detection_sensor2
    form.collected_time.data = collection.collected_time
    form.caid.data = collection.caid
    return render_template('edit_collection.html', form=form)


@crud.route('/collection/delete/<int:collection_id>', methods=['GET'])
def delete_collection(collection_id):
    collectionservice = CollectionDao()
    collection = collectionservice.get_collection(collection_id)
    collectionservice.delete_collection(collection)
    return redirect(url_for('collection.index'))

