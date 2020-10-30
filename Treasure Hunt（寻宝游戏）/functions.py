
# 当代DBMS 2020
# Author:QiushiSun
# Project 1 TreasureHunt:functions.py

from app import players, treasures, markets
import random
import sys

MERGE_COST=20000# 合成需要花费
scale=10 #宝物属性的浮动值，可以理解为寻找到宝物属性的标准差

def day_start():
    print("——————新的一天开始了——————")
    #print("这是寻宝游戏的第%s天" % day)

# 实现每日自动劳动赚取金币
def every_day_work():
    for each_player in players.find():
        wear_treasure_name = each_player['treasure']['Tool']
        wear_treasure_level = treasures.find_one({"name": wear_treasure_name})['level'] #确定当前工作能力
        earned_money = random.randint((wear_treasure_level) * scale, (wear_treasure_level + 1) * scale) #获得劳动收入，数值取决于工作能力，有一个scale的浮动
        name = each_player["name"] #确定当前对象
        income = each_player['money'] + earned_money #把劳动收入添加到money中
        players.update_one({"name": name},
                           {"$set": {"money": income}})
        print("Player %s通过每日劳动获得收入：%d$"% (name, earned_money))

# 每日自动寻宝，随机获得工具或者是饰品
def hunt_treasure():
    for player in players.find():

        player_name = player["name"]
        if len(player['box']) >= 10: #寻宝前为每个玩家检查宝箱是否已经满了
            print("Player %s的存储箱已满，即将抛弃一件价值最低的物品"% (player_name))
            treasure_retrieve(player_name)

        # 将玩家佩戴饰品的级别作为寻到宝物的依据
        box = players.find_one({"name": player_name})['box'] #玩家的存储箱
        wear_treasure_name = player['treasure']['Trinket'] #当前佩戴的饰品
        wear_treasure_level = treasures.find_one({"name": wear_treasure_name})['level'] #获得物品的稀有程度
        # print(wear_treasure_name)
        # print(wear_treasure_level)
        treasure_candidates = [] # 初始化一个空数组存储宝物
        # 随机选取一些可能被寻找到的宝物（能力范围之内）
        # 将运气上下一个标准差个级别的宝物作为寻宝的范围
        # 将运气上下一个标准差个级别的宝物作为寻宝的范围
        for treasure_found in treasures.find({"level": {"$lte": wear_treasure_level + 30, "$gte": wear_treasure_level - 8}}):
            treasure_candidates.append(treasure_found)
        # 随机从可能的宝物中寻找一件
        x = random.randint(0, len(treasure_candidates) - 1)
        box.append(treasure_candidates[x]['name'])
        # 更新储物箱的状态
        players.update_one({"name": player_name}, {"$set": {"box": box}})
        print("Player %s获得宝物：%s(%s)" % (player_name, treasure_candidates[x]['name'],treasure_candidates[x]['property']))
        #找到宝物后打印出宝物和玩家信息


# 宝箱充满之后抛弃一件最差的装备
def treasure_retrieve(name):
    player_box = players.find_one({"name": name})['box']
    treasure_name = player_box[0]
    #先获取箱子里的宝物名，再迭代
    treasure_level = treasures.find_one({"name": player_box[0]})['level']

    for treasure in player_box[1:]: # 遍历找到数值最低的宝物
        temp = treasures.find_one({"name": treasure})['level']
        if temp < treasure_level:
            treasure_level = temp
            treasure_name = treasure

    #获取被删除宝物的信息
    deleted_item_property = treasures.find_one({"name": treasure_name})['property']
    # 从宝箱中删除这个被选中的宝物
    for treasure in player_box:
        if treasure == treasure_name:
            # 删除这个宝物
            player_box.remove(treasure)
            break
    # 更新玩家宝箱
    players.update_one({'name': name}, {"$set": {"box": player_box}})
    print("Player %s被自动回收一件低价值宝物：%s(%s)" % (name, treasure_name, deleted_item_property))



# 返回一个json，_id会被删除，类型为ObjectId
def display_dict(dictionary):
    buffer = {} # initialize
    for key in dictionary.keys():
        if key != '_id':
            buffer[key] = dictionary[key]
    return buffer

# 出卖宝物
def sell_treasure(username, treasure, price):
    player = players.find_one({"name": username})
    # 卖家宝物到位
    box = player['box']
    for treasure_sold in box:
        if treasure_sold == treasure:
            box.remove(treasure_sold)
            break

    players.update_one({"name": username}, {"$set": {"box": box}})
    # 市场宝物到位
    markets.insert_one({"name": treasure, "price": price, "source": username})
    return "<h2>挂牌成功</h2>" + "<br><br>" + \
           str(display_dict(players.find_one({"name": username})))

# 佩戴宝物
def wear(username, treasure):
    if treasures.find_one({"name": treasure}) is None: #目前存储箱中可能没这个宝物
        return "佩戴失败，存储箱中没有 %s" % treasure + "" + \
               str(display_dict(players.find_one({"name": username})))
    treasure_class = treasures.find_one({"name": treasure})['property'] # 查看宝物类型
    current_trasure = players.find_one({"name": username})["treasure"][treasure_class] # 替换当前宝物
    treasure_exists = 0 #检查宝物状态
    current_box = players.find_one({'name': username})['box'] # 玩家装备的宝物（{treasure:{"Tool",... ,"Trinket",...}）
    player_treasure = players.find_one({"name": username})["treasure"]

    for item in current_box:

        if (item==treasure):
            current_box.remove(item) #把装备从存储箱中取出来
            current_box.append(current_trasure)
            player_treasure[treasure_class] = treasure
            players.update_one({"name": username}, {"$set": {"box": current_box}}) #在数据库中更新玩家状态
            players.update_one({"name": username}, {"$set": {"treasure": player_treasure}}) #在数据库中更新玩家状态
            treasure_exists+=1
            return "<h2>装备 %s 宝物成功</h2>" % treasure + "" \
                   + str(display_dict(players.find_one({"name": username})))
    if treasure_exists == 0:  #如果宝物不存在则返回一个错误提示
        return "<h2>发生错误，储物箱中无 %s 宝物</h2>" % treasure + "" \
               + str(display_dict(players.find_one({"name": username}))) #打印出当前玩家储物箱和装备的信息

# 浏览市场
def look_market(username):
    # 用户名不存在
    if players.find_one({"name": username}) is None:
        return "<h1>请先注册用户</h1>"
    asset = ''
    for treasure in markets.find():
        asset += str(display_dict(treasure))
        asset += '<br> <br>'
    return "<h2>来到了市场</h2><br><br>" + asset

# 收回挂牌宝物
def withdraw(username, treasure):
    if markets.find_one({"name": treasure}) is None:     # 市场可能没有该宝物
        return "<h1>Market中目前没有 %s 宝物</h1>" % treasure + "<br><br>" \
               + str(display_dict(players.find_one({"name": username})))
    markets.delete_one({"name": treasure})     # 市场需要删除宝物
    box = players.find_one({"name": username})['box']
    if len(box) >= 10:     # 别忘了测试储物箱是不是满了
        treasure_retrieve(username)
    box = players.find_one({"name": username})['box']
    box.append(treasure)
    players.update_one({"name": username}, {"$set": {"box": box}})

    return "<h2>回收完成，已经从Market中收回宝物 %s </h2>" % treasure + "<br><br>" + \
           str(display_dict(players.find_one({"name": username})))

# 融合宝物
def merge(username, treasure_1, treasure_2):
    player = players.find_one({"name": username})
    player_box = player['box']
    if player['money'] < MERGE_COST:
        return "<h1>操作失败，当前金币不足</h1>" + "<br><br>" \
               + str(display_dict(players.find_one({"name": username})))
    if treasure_1 not in player_box:
        return "<h1>操作失败，存储箱没有 %s 宝物</h1>" % treasure_1 + "<br><br>" \
               + str(display_dict(players.find_one({"name": username})))
    if treasure_2 not in player_box:
        return "<h1>操作失败，存储箱没有 %s 宝物</h1>" % treasure_2 + "<br><br>" \
               + str(display_dict(players.find_one({"name": username})))
    if treasure_1 == treasure_2:
        treasure_num = 0
        for each_treasure in player_box:
            if each_treasure == treasure_1: treasure_num += 1
        if treasure_num< 2:
            return "<h2>抱歉，操作失败，存储箱没有两件 %s 宝物</h2>" % treasure_2 + "<br><br>" \
                   + str(display_dict(players.find_one({"name": username})))
    for each_treasure in player_box: #从储物箱中移除两件装备
        if each_treasure == treasure_1:
            player_box.remove(each_treasure)
            break
    for each_treasure in player_box: #同上 移除第二件装备ß
        if each_treasure == treasure_2:
            player_box.remove(each_treasure)
            break
    merge_ls = []
    for col in treasures.find():
        merge_ls.append(col)
    x = random.randint(0, len(merge_ls) - 1)
    player_box.append(merge_ls[x]['name'])
    players.update_one({"name": username}, {"$set": {"box": player_box}})
    money_update = player['money'] - MERGE_COST
    players.update_one({"name": username}, {"$set": {"money": money_update}})
    return "<h1>融合成功，请查看背包，10000元已经扣除</h1>" + "<br><br>" + \
           str(display_dict(players.find_one({"name": username})))

# 从市场购买宝物
def buy(username, treasure):
    if markets.find_one({"name": treasure}) is None:     # 市场可能没有该宝物
        return "<h1>错误：Market中目前并没有 %s 宝物</h1>" % treasure + "<br><br>" \
               + str(display_dict(players.find_one({"name": username})))
    player = players.find_one({"name": username})
    new_box = player['box']
    if len(new_box) >= 10:
        treasure_retrieve(username) #如果宝物满了就要回收最低价值宝物
    box = player['box']  #重新指定被box，因为有可能被回收了
    box.append(treasure) #把宝物添加进box
    players.update_one({"name": username}, {"$set": {"box": box}})
    treasure_money = 65535 #定义一个最大的价格
    id = markets.find_one({"name": treasure})['_id']  # 这里避免市场很多重复宝物需要用_id进行记录
    for thing in markets.find({"name": treasure}):     # 由于可能有多个卖家在出售同一个宝物，所以需要比一比价格
        if thing['price'] < treasure_money:
            treasure_money = thing['price']
            id = thing['_id']
    money_updated = player['money'] - treasure_money
    players.update_one({"name": username}, {"$set": {"money": money_updated}})
    sold_treasure = markets.find_one({"_id": id})['source']
    money2 = players.find_one({"name": sold_treasure})['money'] + treasure_money
    players.update_one({"name": sold_treasure}, {"$set": {"money": money2}})
    markets.delete_one({"name": treasure}) #完成购买后需要把宝物移除出markt

    return "<h1>Player %-3s 通过Market交易收入： %d </h1>" % (sold_treasure, treasure_money) + "<br><br>" \
           + "土豪买家" + str(display_dict(players.find_one({"name": username}))) + "<br><br>" \
           + "土豪卖家" + str(display_dict(players.find_one({"name": sold_treasure})))

def check_rank(username):
    cur_player_score = players.find_one({"name": username})['money']
    rank=0
    ranking_list=[]

    for player in players.find():
        temp=[]
        playername=player['name']
        playerscore = player['money']
        temp.append(playername)
        temp.append(playerscore)
        ranking_list.append(temp)

    for i in range(0,len(ranking_list)):
        if cur_player_score < ranking_list[i][1]:
            rank = rank+1

    return "<h2>您的当前财富排名为第：%s 名</h2>" % str(rank)