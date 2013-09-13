#-*- coding:utf-8 -*-
import parallel,time,random
p=parallel.Parallel()
p.setData(0b00000000)
WHEN=10000
m=  """
开门助手功能简介:
本助手用于召唤神龙帮你开启益嘉广场1号楼门禁，或是开启一楼大厅大门，常用命令包括:
open 开门
ans  应答呼叫(当然，你得先呼叫)
以及其他未公开的命令，后续打算添加乱七八糟的功能比如查询水电费什么的- -
由于硬件限制，开门及应答动作的全局最小间隔设置为60秒.
"""
n="来自美国的交换生奥利奥同学昨天被残忍分尸身上涂满口水和牛奶。x小明半夜饿的肚子咕咕叫于是生了一窝鸽子。x院长吃了麻婆豆腐以后，当场被麻婆砍了二十多刀。x对于发烧的病人要趁热吃。x我院门口有良心的小贩老王谋杀百余老党员只为制作合格红领巾。x孩子睡觉老踢被子幸亏被我打断了腿，不然就感冒了！x因患密集恐惧症校领导拒绝开校庆大会。x妈妈说我瘦得像猴我愤怒的背着筐桃子爬上电线杆死活不下来了。x体操冠军转体1080度成功把自己拧出水。x在一口咬定凶手之后警察从始至终未松开啃住嫌犯的嘴。x眼看色狼就要得手我急中生智掏出一瓶浓硫酸泼到姑娘脸上解救了她 x实验课小明突发酒瘾喝干所有酒精灯。x一男童惨遭食人魔毒手，丧尽天良的凶手竟忘记放葱。x练成铁头功的大师兄刚下山，就 被一个有电磁吸盘的大吊车吸走了 x医院送来小明的病危通知书却忘了收快递费全家人为此喜极而泣 x当荆轲在咸阳宫门外听到大包小包请过安检的一瞬间还是崩溃了。 x我因多次在公交车上给老弱病残让座，荣获感动中国十大司机。 x青年小王麦当劳买饮料执意只要第二杯被店员赶出。x十岁男童掉入下水井，热心路人及时将井盖盖上防止事故再发。 x饭馆服务员刚才告诉我，隔壁桌的老夫妇是老顾客了，从很多年前小饭馆刚开业，夫妇二人就经常过来，每次都打包一两个菜带走，数十年如一日从未间断。我听了很受触动，没想到一对老夫妇能相濡以沫的恩爱几十年，竟然还是不会做饭。 x我炒了我们公司的一个员工，味道还可以，就是有点咸。 x从小爱占便宜的小王为多骗奶油谎称自己是台湾人，要求用繁体字写祝福语 x色狼抱住女路人欲施爆,机智女孩十秒完成卸妆,将流氓成功吓跑 x无良商家用鼠肉加明胶冒充羊肉销售，据执法人员称舒克和贝塔均已遇难 x孕妇公交车上突然晕倒，最美售票员联合数十名爱心乘客奋力施救，终唤醒孕妇令其补票 x无头女尸拍大头贴竟被老板收钱惹民愤 x我家小狗走丢了，用搜狗搜不到，急死我了"
nl=n.split("x")
def command(scmd="",icmd=""):
    global WHEN
    if scmd=="" and icmd=="13_13":
        if checkwhen(WHEN):
            opendoor()
            WHEN=time.time()
            return u"开锁完成"
        else:
            return u"60秒内只能发送一次命令,剩余%d秒。" %(60-time.time()+WHEN)
    elif scmd=="" and icmd=="13_13_13":
        if checkwhen(WHEN):
            ansdoor()
            WHEN=time.time()
            return u"应答完成"
        else:
            return u"60秒内只能发送一次命令,剩余%d秒。" %(60-time.time()+WHEN)
    elif scmd=="help" and icmd=="":
        return m
    elif scmd=="ulk" and icmd=="":
        WHEN=10000
        return "解锁完成"
    else:
        return random.choice(nl)

def checkwhen(t):
    if time.time()-t>60:
        return True
    else:
        return False
    
def opendoor():
    p.setData(0b00000001)
    time.sleep(0.5)
    p.setData(0b00000000)
    time.sleep(1.5)
    p.setData(0b00000010)
    time.sleep(0.5)
    p.setData(0b00000000)
    time.sleep(2.0)
    p.setData(0b00000100)
    time.sleep(0.5)
    p.setData(0b00000000)
    time.sleep(1.0)
    p.setData(0b00000010)
    time.sleep(0.5)
    p.setData(0b00000000)
    return "done"

def ansdoor():
    p.setData(0b00000010)
    time.sleep(0.5)
    p.setData(0b00000000)
    time.sleep(2.0)
    p.setData(0b00000100)
    time.sleep(0.5)
    p.setData(0b00000000)
    time.sleep(2.0)
    p.setData(0b00000010)
    time.sleep(0.5)
    p.setData(0b00000000)
    return "done"
