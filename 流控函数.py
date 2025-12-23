#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流控函数模块
参考手机脚本流控函数.lua的实现
"""

import os
import sys
import time
import random
from FreeGame_X import Point, Action, FreeGame, add_log

# 全局变量
抓鬼轮数 = 0
采集次数 = 0
更新记录时间 = 0
界面数据 = {}
fg = FreeGame()  # 创建FreeGame实例


def 判断次数0():
    """
    抓鬼次数控制函数
    每5分钟增加一次抓鬼轮数，达到设定值后返回True
    """
    global 抓鬼轮数, 更新记录时间
    current_time = time.time()
    if current_time - 更新记录时间 > 300:  # 5分钟
        抓鬼轮数 += 1
        # fwShowTextView相当于显示文本信息，在Python中可以用日志代替
        add_log(f"抓鬼轮数: {抓鬼轮数}")
        add_log(f"已经抓了_{抓鬼轮数}_轮鬼！")
        更新记录时间 = current_time
        if 抓鬼轮数 > (界面数据.get('zgls', 0) - 1):
            return True, True  # 返回True表示退出，第二个True可能是扩展参数
    return False


def 判断次数1():
    """
    采集次数控制函数
    每20秒增加一次采集次数，达到设定值后返回True
    """
    global 采集次数, 更新记录时间
    current_time = time.time()
    if current_time - 更新记录时间 > 20:
        采集次数 += 1
        add_log(f"采集次数: {采集次数}")
        add_log(f"正在采集第_{采集次数}_次！")
        更新记录时间 = current_time
        if 采集次数 > (界面数据.get('cjcs', 0) - 1):
            return True, True
    return False


def 滑动任务():
    """
    滑动任务列表的动作
    """
    # 注意：这里需要确保FreeGame类已经初始化，并且page.txt中包含对应的特征点
    bb = Action('t.语音话筒', 't.任务列表').except_('t.点击捉鬼').click(Point(199, 580)).sleep(1500)
    bb.slid(Point(1142, 210), Point(1230, 558)).sleep(500)
    bb.slid(Point(1142, 210), Point(1230, 558)).sleep(1500)
    fg.runAction(bb)
    return False


def 检查滑动任务(ttime):
    """
    检查滑动任务的时间
    """
    add_log(f"检查滑动任务时间: {ttime}")
    # fwShowTextView相当于显示文本信息
    add_log(f"抓鬼轮数-{ttime}/240")
    if ttime > 240:
            aa = Action('t.继续抓鬼', 't.确定继续').before(判断次数0).sleep(1000).click().cs(1).sleep(8000)
            fg.runAction(aa)
            
            bb = Action('t.抓鬼任务').sleep(1000).click().cs(2).sleep(3000)
            fg.runAction(bb)
            
            cc = Action('t.任务列表').click(Point(199, 580)).sleep(1500)
            cc.slid(Point(1142, 210), Point(1230, 558)).sleep(500)
            cc.slid(Point(1142, 210), Point(1230, 558)).cs(2).sleep(1500)
            fg.runAction(cc)
            
            dd = Action('t.点击捉鬼').click(80, 30).sleep(1500).click(50, 20).cs(1).sleep(900).uncheck(滑动任务)
            fg.runAction(dd)
    return False


def 测试程序(action, points):
    """
    测试动作和点位的函数
    """
    for v in points:
        add_log(f"点位: {v.x},{v.y}")
    return False


def 找不到飞东海():
    """
    找不到东海时的处理
    """
    bb = Action('t.打开地图').click(Point(46, 51)).sleep(1500).click(Point(980, 390))
    fg.cs(1)
    FreeGame:runAction(bb)
    return True


def 找不到飞长寿():
    """
    找不到长寿时的处理
    """
    bb = Action('t.打开地图').click(Point(46, 51)).sleep(1500).click(Point(240, 390)).cs(1)
    fg.runAction(bb)
    return True


def 找不到飞花果():
    """
    找不到花果山时的处理
    """
    bb = Action('t.打开地图').click(Point(46, 51)).sleep(1500).click(Point(1138, 253)).cs(1)
    fg.runAction(bb)
    return True


def 找不到飞大雪():
    """
    找不到大雪山时的处理
    """
    bb = Action('t.打开地图').click(Point(46, 51)).sleep(1500).click(Point(610, 148)).cs(1)
    fg.runAction(bb)
    return True


def 找不到飞两界():
    """
    找不到两界山时的处理
    """
    bb = Action('t.打开地图').click(Point(46, 51)).sleep(1500).click(Point(411, 445)).cs(1)
    fg.runAction(bb)
    return True


def 找花草2():
    """
    找花草的处理
    """
    bb = Action('t.采集花草2').click(15, -40).s(1).cs(2).sleep(3000).cs(1)
    fg.runAction(bb)
    return False


def 找矿石2():
    """
    找矿石的处理
    """
    bb = Action('t.挖掘矿石2').click(15, -40).s(1).cs(2).sleep(3000).cs(1)
    fg.runAction(bb)
    return False


def 任务没有执行(ttime):
    """
    任务没有执行时的处理
    """
    add_log(f"任务没有执行时间: {ttime}")
    # fwShowTextView相当于显示文本信息
    add_log(f"任务超时: {ttime}")
    if ttime > 30:
        random.seed(time.time())  # 使用时间作为随机种子
        xzdt = 界面数据.get('xzdt', '')
        if '0' in xzdt:
            aa = Action('t.当前东海').click(Point(160, 46)).sleep(1500)
            aa.click(Point(random.randint(454, 868), random.randint(210, 507))).uncheck(找不到飞东海).cs(1)
            fg.runAction(aa)
        elif '1' in xzdt:
            aa = Action('t.当前长寿').click(Point(160, 46)).sleep(1500)
            aa.click(Point(random.randint(391, 945), random.randint(254, 566))).uncheck(找不到飞长寿).cs(1)
            fg.runAction(aa)
        elif '2' in xzdt:
            aa = Action('t.当前花果').click(Point(160, 46)).sleep(1500)
            aa.click(Point(random.randint(531, 853), random.randint(234, 530))).uncheck(找不到飞花果).cs(1)
            fg.runAction(aa)
        elif '3' in xzdt:
            aa = Action('t.当前大雪').click(Point(160, 46)).sleep(1500)
            aa.click(Point(random.randint(485, 900), random.randint(232, 567))).uncheck(找不到飞大雪).cs(1)
            fg.runAction(aa)
        elif '4' in xzdt:
            aa = Action('t.当前两界').click(Point(160, 46)).sleep(1500)
            aa.click(Point(random.randint(312, 1011), random.randint(270, 503))).uncheck(找不到飞两界).cs(1)
            fg.runAction(aa)
    return False


def 师门停止检测(smtime):
    """
    师门任务停止检测
    """
    add_log(f"师门任务时间: {smtime}")
    退出 = 1  # 定义退出常量
    if smtime > 40:
        aa = Action('t.师门关闭').click().sleep(1500).cs(1)
        fg.runAction(aa)
        return 退出
    elif smtime > 20:
        aa = Action('t.活动关闭1').click().sleep(1500).except_('商城购买按钮').cs(1)
        fg.runAction(aa)
    return False


# 导出所有流控函数
__all__ = [
    '判断次数0', '判断次数1', '滑动任务', '检查滑动任务',
    '测试程序', '找不到飞东海', '找不到飞长寿', '找不到飞花果',
    '找不到飞大雪', '找不到飞两界', '找花草2', '找矿石2',
    '任务没有执行', '师门停止检测'
]
