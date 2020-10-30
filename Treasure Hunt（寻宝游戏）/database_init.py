
# 当代DBMS 2020
# Author:QiushiSun
# Project 1 TreasureHunt:database_init.py

# 连接数据库
from pymongo import ASCENDING
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import BulkWriteError
from treasures import weapon,trinket #导入宝物名
from treasures import weapon_level,weapon_value,trinket_level,trinket_value #导入宝物数据
from treasures import rarity_map #导入稀有度，对宝物的稀有程度做一个映射

treasure_list = [] #初始化一个空数据用来存宝物并插入数据库

for weap in range(len(weapon)):
    treasure_list.append(
        {"name": weapon[weap], "property": "Tool", "level": weapon_value[weap], "item_level": rarity_map[weapon_level[weap]]})
    #读取武器名，数据，稀有程度
for trink in range(len(trinket)):
    treasure_list.append({"name": trinket[trink], "property": "Trinket", "level": trinket_value[trink],
                          "item_level": rarity_map[trinket_level[trink]]})
    #读取饰品名，数据，稀有程度

client = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false') #连接本地数据库
players = client.MongoDB_Treasure_Hunt.players      #连接玩家collection
markets = client.MongoDB_Treasure_Hunt.markets      #连接市场collection
treasures = client.MongoDB_Treasure_Hunt.treasures  #连接宝物collection

try:
    treasures.insert_many(treasure_list)
    print("宝物创建完成了，共80件工具，45件饰品")
except BulkWriteError:
    print("所有宝物都已被创建完成了")

