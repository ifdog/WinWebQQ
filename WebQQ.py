# -*- coding: utf-8 -*-

from HttpClient import HttpClient
import re, random, md5, json, os, sys, datetime, time, thread, subprocess, logging, commands
reload(sys)  
sys.setdefaultencoding('utf-8')

class WebQQ(HttpClient):
  ClientID = int(random.uniform(111111, 888888))
  APPID = 0
  MaxTryTime = 5
  Referer = 'http://w.qq.com/index.html?webqq_type=10'
  SmartQQUrl = 'http://w.qq.com/login.html'

  def __init__(self, vpath):
    self.VPath = vpath#QRCode保存路径
    logging.basicConfig(filename='qq.log', level=logging.DEBUG, format='%(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    self.initUrl = self.getReValue(self.Get(self.SmartQQUrl), r'src="(.+?)"', 'Get Login Url Error.', 1)

    html = self.Get(self.initUrl)

    self.APPID = self.getReValue(html, r'var g_appid =encodeURIComponent\("(\d+)"\);', 'Get AppId Error', 1)

    sign = self.getReValue(html, r'var g_login_sig=encodeURIComponent\("(.+?)"\);', 'Get Login Sign Error', 1)
    logging.info('get sign : %s', sign)

    JsVer = self.getReValue(html, r'var g_pt_version=encodeURIComponent\("(\d+)"\);', 'Get g_pt_version Error', 1)
    logging.info('get g_pt_version : %s', JsVer)

    MiBaoCss = self.getReValue(html, r'var g_mibao_css=encodeURIComponent\("(.+?)"\);', 'Get g_mibao_css Error', 1)
    logging.info('get g_mibao_css : %s', sign)

    StarTime = self.date_to_millis(datetime.datetime.utcnow())

    T = 0
    while True:
      T = T + 1
      self.Download('https://ssl.ptlogin2.qq.com/ptqrshow?appid={0}&e=0&l=L&s=8&d=72&v=4'.format(self.APPID), self.VPath)
      logging.info('[{0}] Get QRCode Picture Success.'.format(T))
      while True:
        html = self.Get('https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid={0}&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{1}&mibao_css={2}&t=undefined&g=1&js_type=0&js_ver={3}&login_sig={4}'.format(self.APPID, self.date_to_millis(datetime.datetime.utcnow()) - StarTime, MiBaoCss, JsVer, sign), self.initUrl)
        logging.info(html)
        ret = html.split("'")
        if ret[1] == '65' or ret[1] == '0':#65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
          break
        time.sleep(2)
      if ret[1] == '0' or T > self.MaxTryTime:
        break

    if ret[1] != '0':
      return

    if os.path.exists(self.VPath):#删除QRCode文件
      os.remove(self.VPath)

    html = self.Get(ret[5])

    self.PTWebQQ = self.getCookie('ptwebqq')
    skey = self.getCookie('p_skey')
    uin = self.getCookie('p_uin')

    logging.info('PTWebQQ: {0}'.format(self.PTWebQQ))
    logging.info('p_skey: {0}    p_uin: {1}'.format(skey, uin))

    self.setCookie('p_skey', skey, 'qq.com')
    self.setCookie('p_uin', uin, 'qq.com')

    html = self.Post('http://w.qq.com/d/channel/login2', {
      'r' : '{{"status":"online","ptwebqq":"{0}","clientid":"{1}","psessionid":""}}'.format(self.PTWebQQ, self.ClientID)
    }, self.Referer)

    logging.debug(html)
    ret = json.loads(html)

    if ret['retcode'] != 0:
      return

    self.VFWebQQ = ret['result']['vfwebqq']
    self.PSessionID = ret['result']['psessionid']

    logging.info('Login success')

    msgId = int(random.uniform(20000, 50000))

    E = 0
    while 1:
      html = self.Post('http://w.qq.com/d/channel/poll2', {
        'r' : '{{"key":"","psessionid":"{0}","ptwebqq":"{1}","clientid":"{2}"}}'.format(self.PSessionID, self.PTWebQQ, self.ClientID)
      }, self.Referer)

      if html.find('504') != -1:
        continue

      logging.info(html)

      try:
        ret = json.loads(html)
      except ValueError as e:
        logging.debug(e)
        E += 1
      except Exception as e:
        logging.debug(e)
        E += 1

      if E > 0 and E < 5:
        time.sleep(5)
        continue

      if E > 0:
        logging.debug('error max')
        break

      E = 0

      if ret['retcode'] != 102:
        if ret['retcode'] == 116:
          self.PTWebQQ = ret['p']
        else:
          if ret['retcode'] == 0:
            for msg in ret['result']:
              msgType = msg['poll_type']
              if msgType == 'message':
                txt = msg['value']['content'][1]
                logging.debug(txt)

                if txt[0:5] == '@exit':
                  logging.info(self.Get('http://w.qq.com/d/channel/logout2?ids=&clientid={0}&psessionid={1}'.format(self.ClientID, self.PSessionID), self.Referer))
                  exit(0)
                thread.start_new_thread(self.handler, (msg, msgId))
##                if txt[0] == '#':
##                    thread.start_new_thread(self.runCommand, (msg['value']['from_uin'], txt[1:].strip(), msgId))
##                    msgId += 1

              elif msgType == 'kick_message':
                logging.error(msg['value']['reason'])
                break
              elif msgType != 'input_notify':
                logging.debug(msg)
          else:
            logging.debug(ret)

  def handler(self, msg, msgId):
    fuin = msg['value']['from_uin']
    cmd=msg['value']['content'][1:]
    scmd="".join([x.decode('utf8').strip() for x in cmd if isinstance(x,unicode)])
    icmd="_".join([str(x[1]) for x in cmd if isinstance(x,list)])
    ret=commands.command(scmd=scmd,icmd=icmd)
    ret = ret.replace('\\', '\\\\\\\\').replace('\t', '\\\\t').replace('\r', '\\\\r').replace('\n', '\\\\n')
    ret = ret.replace('"', '\\\\\\"')
    self.Post("http://w.qq.com/d/channel/send_buddy_msg2", (
      ('r', '{{"to":{0},"face":567,"content":"[\\"{4}\\",[\\"font\\",{{\\"name\\":\\"Arial\\",\\"size\\":\\"10\\",\\"style\\":[0,0,0],\\"color\\":\\"000000\\"}}]]","msg_id":{1},"clientid":"{2}","psessionid":"{3}"}}'.format(fuin, msgId, self.ClientID, self.PSessionID, ret)),
      ('clientid', self.ClientID),
      ('psessionid', self.PSessionID)
    ), self.Referer)

  def getReValue(self, html, rex, er, ex):
    v = re.search(rex, html)
    if v is None:#如果匹配失败
      logging.error(er)#记录错误
      if ex:#如果条件成立,则抛异常
        raise Exception, er
    return v.group(1)#返回匹配到的内容

  def date_to_millis(self, d):
    return int(time.mktime(d.timetuple())) * 1000


if __name__ == "__main__":
  vpath = './v.jpg'
  if len(sys.argv) > 1:
    vpath = sys.argv[1]
  while True:
    try:
      WebQQ(vpath)
    except Exception, e:
      print e
# vim: tabstop=2 softtabstop=2 shiftwidth=2 expandtab
