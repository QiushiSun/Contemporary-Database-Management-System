# 当代DBMS 2020
# Author:QiushiSun
# Project 1 TreasureHunt:tasks.py

# 配置自动任务的类
class Config(object):
    JOBS = [
        {
            'id': 'job0',
            'func': '__main__:day_start',
            'trigger': 'interval',
            'seconds': 8,

        },
        {
            'id': 'job1',
            'func': '__main__:hunt_treasure',
            'trigger': 'interval',
            'seconds': 8,

        },
        {
            'id': 'job2',
            'func': '__main__:every_day_work',
            'trigger': 'interval',
            'seconds': 8,
        },
    ]