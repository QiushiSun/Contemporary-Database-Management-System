
# 当代DBMS 2020
# Author:QiushiSun
# Project 1 TreasureHunt:app.py

import os
import random
import sys
import tasks
import pymongo
from pymongo import MongoClient
from flask import Blueprint
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from pymongo.errors import DuplicateKeyError
scale=10

#————————————————————————————————————————————#
#————————————————————————————————————————————#

# bp = Blueprint ("TreasureHunt",__name__,url_prefix="/")

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

client = MongoClient('localhost', 27017)

players = client.MongoDB_Treasure_Hunt.players
markets = client.MongoDB_Treasure_Hunt.markets
treasures = client.MongoDB_Treasure_Hunt.treasures

app = Flask(__name__)

@app.route("/", methods=['GET'])
def Game_start():
    return render_template('index.html')

# @app.route("/", methods=['GET'])
# def Game_start():
#     return 'ok'

@app.route("/showstatus", methods=['GET'])
def init():
    return render_template('index.html')


# 设置以下五个路由
@app.route("/<string:username>/<string:operation>/<string:password>", methods=['GET'])
@app.route("/<string:username>/<string:operation>/<string:treasure_1>/<int:price>", methods=['GET'])
@app.route("/<string:username>/<string:operation>/<string:treasure_1>", methods=['GET'])
@app.route("/<string:username>/<string:operation>/<string:treasure_1>/<string:treasure_2>", methods=['GET'])
@app.route("/<string:username>/<string:operation>", methods=['GET'])

def find_method(username,operation,password=123,treasure_1='test',treasure_2='test',price=0):
    if operation == 'register':
        return login(username,password)
    elif operation == 'login':
        cur_password=players.find_one({"name": username})['pwd']
        if password==cur_password:
            return login(username,password)
        else:
            return "<h1>Oops!Wrong password</h1>"
    elif operation == 'market':
        return look_market(username)
    elif operation == 'wear':
        return wear(username, treasure_1)
    elif operation == 'buy':
        return buy(username, treasure_1)
    elif operation == 'withdraw':
        return withdraw(username, treasure_1)
    elif operation == 'sell':
        return sell_treasure(username, treasure_1, price)
    elif operation == 'merge':
        return merge(username, treasure_1, treasure_2)
    elif operation == 'ranking':
        return check_rank(username)
    elif operation == 'ranking':
        return check_rank(username)
    else:
        return "<h1>Oops!An error is caused due to invalid operation</h1>"



if __name__ == "__main__":
    app.config.from_object(tasks.Config())  # 每日自动执行任务
    scheduler = APScheduler() # 设定调度器
    scheduler.init_app(app)
    scheduler.start() #开始调度
    app.run()


