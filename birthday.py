from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.modules.priconne import chara
from . import _chara_data

import datetime
import hoshino
import re
import os
import random

bdrm = Service('birthday_reminder', enable_on_default=True, help_='生日提醒', bundle='pcr订阅')
svbdsrh = Service('birthday_search', bundle='pcr娱乐', help_='''
谁的生日是+生日 这天哪位'老婆'过生日呢
谁的生日是今天 看看今天哪位'老婆'过生日呢
'''.strip())

def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]

    
def get_cqcode(chara_id):
    dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'priconne', 'unit')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    c = chara.fromid(chara_id)
    cqcode = '' if not c.icon.exist else c.icon.cqcode
    return c.name, cqcode

@bdrm.scheduled_job('cron', hour='00', minute='01')
async def birthday_reminder():
    chara_id_list = list(_chara_data.CHARA_DATA.keys())
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    birthdate = str(month)+'月' + str(day) + '日'
    birthday_chara_id = 0
    #测试用
    #birthdate = '2月2日'
    birthday_chara_id_lst = []
    for i in range(len(chara_id_list)):
        if _chara_data.CHARA_DATA[chara_id_list[i]][2] == birthdate:
            birthday_chara_id_lst.append(chara_id_list[i])
    ninsuu = len(birthday_chara_id_lst)
    if ninsuu == 0:
        print('无人过生日')
        return
    else:
        msg = f'今天有{ninsuu}人过生日：\n'
        for caraId in birthday_chara_id_lst:
            name, cqcode = get_cqcode(caraId)
            msg = msg + f'{name}ちゃん{cqcode}在今天过生日哦~\n'
        await bdrm.broadcast(msg, 'birthday_reminder', 0.2)

@svbdsrh.on_prefix(('谁的生日','谁生日'))
async def birthday_search(bot, ev: CQEvent):
    chara_id_list = list(_chara_data.CHARA_DATA.keys())
    birthdate = ev['raw_message'].replace("谁的生日", "").replace("过", "").replace("在", "").replace("谁生日", "").replace("号", "日").replace("的", "").replace("生日", "").replace("-", "").replace("是", "").replace(" ","")
    #检测并转换生日格式
    if re.match(r"([01][0-9][0123][0-9])",birthdate):
        bMonth = birthdate[1:2] if birthdate[0:1] == '0' else birthdate[0:2]
        bDay = birthdate[3:4] if birthdate[2:3] == '0' else birthdate[2:4]
        birthdate = bMonth + '月' + bDay + '日'
    elif re.match(r"([01]?[0-9]月[0123]?[0-9][日号]?)",birthdate):
        birthdate = re.search(r"(\d{1,2}月\d{1,2})",birthdate).group(0) + '日'
    elif re.match(r"(今天)",birthdate):
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        birthdate = str(month)+'月' + str(day) + '日'
    print(birthdate)
    #判断日期格式是否正确
    if re.match(r"(\d{1,2}月\d{1,2}日)",birthdate) == "":
        await bot.send(ev, f'请输入正确的生日格式，如"0723"或者"7月23日"')
        return
    birthday_chara_id_lst = []
    for i in range(len(chara_id_list)):
        if _chara_data.CHARA_DATA[chara_id_list[i]][2] == birthdate:
            birthday_chara_id_lst.append(chara_id_list[i])
    ninsuu = len(birthday_chara_id_lst)
    if ninsuu == 0:
        print('无人过生日')
        await bot.send(ev, f'{birthdate}没有人过生日哦~')
        return
    else:
        msg = f'{birthdate}有{ninsuu}人过生日：\n'
        for caraId in birthday_chara_id_lst:
            name, cqcode = get_cqcode(caraId)
            msg = msg + f'{name}ちゃん{cqcode}在{birthdate}过生日哦~\n'
        await bot.send(ev, msg)