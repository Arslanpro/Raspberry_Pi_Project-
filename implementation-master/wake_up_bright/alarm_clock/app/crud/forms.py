from wtforms import StringField, SelectField, SubmitField, IntegerField, DateTimeField, TimeField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from wake_up_bright.alarm_clock.app.crud.models import Person
from flask_wtf import Form


class AddPersonForm(Form):
    name = StringField('name')
    age = IntegerField('age')
    gender = StringField('gender')
    submit = SubmitField('save')


class EditPersonForm(Form):
    name = StringField('name')
    age = IntegerField('age')
    gender = StringField('gender')
    submit = SubmitField('update')


class AddAlarmForm(Form):
    current_time = DateTimeField('current_time')
    alarm_time = TimeField('alarm_time')
    alarm_time_max = TimeField('alarm_time_max')
    snooze_time = IntegerField('snooze_time')
    current_date = DateTimeField('current_date')
    auid = IntegerField('auid')
    on_off = IntegerField('on_off')
    submit = SubmitField('save')


class EditAlarmForm(Form):
    current_time = DateTimeField('current_time')
    alarm_time = TimeField('alarm_time')
    alarm_time_max = TimeField('alarm_time_max')
    snooze_time = IntegerField('snooze_time')
    current_date = DateTimeField('current_date')
    auid = IntegerField('auid')
    on_off = IntegerField('on_off')
    submit = SubmitField('update')


class AddCollectionForm(Form):
    move_detection_sensor1 = IntegerField('move_detection_sensor1')
    move_detection_sensor2 = IntegerField('move_detection_sensor2')
    collected_time = DateTimeField('collected_time')
    caid = IntegerField('caid')
    submit = SubmitField('save')


class EditCollectionForm(Form):
    move_detection_sensor1 = IntegerField('move_detection_sensor1')
    move_detection_sensor2 = IntegerField('move_detection_sensor2')
    collected_time = DateTimeField('collected_time')
    caid = IntegerField('caid')
    submit = SubmitField('update')
