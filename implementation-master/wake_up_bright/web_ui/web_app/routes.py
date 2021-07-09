from flask import Blueprint, redirect, url_for, render_template, jsonify
import os, sys, inspect

# Get directory needed to extract data from database.
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentparentdir)

from wake_up_bright.cycle_detection.Retrieve_sleep_graph import *

bp = Blueprint('home', __name__)


# Hello world response as test message
@bp.route('/hello')
def hello():
    return "Hello, World!"


@bp.route('/')
@bp.route('/home')
@bp.route('/index')
def index():
    # return redirect(url_for('home.hello'))
    return render_template('index.html',
                           chart_element='lastNightAreaChart',
                           values=[0, 10, 5, 10, 13, 17, 0, 1, 16, 21, 4, 5],
                           labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                           chart_title='Movement per minute'
                           )


@bp.route('/mockup1')
def test1():
    return jsonify(chart_element='variableChart',
                   values=[99, 98, 65, 87, 63, 77, 88, 96, 75, 74, 73, 55],
                   labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   chart_title='sleep quality')


@bp.route('/mockup2')
def test2():
    return jsonify(chart_element='variableChart',
                   values=[7.23, 8.33, 6.44, 8.33, 7.65, 7.89, 10.12, 12.11, 8.33, 8.25, 8.14, 9.12],
                   labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   chart_title='sleep time')


@bp.route('/mockup3')
def test3():
    return jsonify(chart_element='variableChart',
                   values=[7, 8, 6, 8, 7, 8, 10, 6, 5, 7, 8, 9],
                   labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   chart_title='sleep grade')


@bp.route('/mockup4')
def test4():
    return jsonify(chart_element='variableChart',
                   values=[2, 3, 3, 4, 2, 4, 3, 2, 2, 3, 3, 4],
                   labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   chart_title='sleep cycles')


@bp.route('/mockup5')
def test5():
    return jsonify(chart_element='variableChart',
                   values=[0.8, 0.7, 0.5, 0.6, 0.6, 0.7, 0.8, 0.7, 0.6, 0.5, 0.6, 0.9],
                   labels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                   chart_title='sleep cycle ratios')




@bp.route('/lastnight')
def last_night():
    ct_1 = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    ct_2 = ct_1 + " 12:00:00"
    print(ct_2)
    retrieve_sleep_graph(ct_2)
    return jsonify(chart_element='lastNightAreaChart',
                   values=y_vector,
                   labels=x_vector,
                   chart_title='Movement per minute')


@bp.route('/sp/<string:date>')
def sp_date(date):
    print(date)
    retrieve_sleep_graph(date)
    return jsonify(chart_element='lastNightAreaChart',
                   values=y_vector,
                   labels=x_vector,
                   chart_title='Movement per minute')


@bp.route('/28_29_data')
def data_28_29():
    retrieve_sleep_graph("2020-10-28 12:00:00")
    return jsonify(chart_element='lastNightAreaChart',
                   values=y_vector,
                   labels=x_vector,
                   chart_title='Movement per minute')

@bp.route('/27_28_data')
def data_27_28():
    retrieve_sleep_graph("2020-10-27 12:00:00")
    return jsonify(chart_element='lastNightAreaChart',
                   values=y_vector,
                   labels=x_vector,
                   chart_title='Movement per minute')
