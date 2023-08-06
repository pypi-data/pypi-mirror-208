# encoding: utf-8
from . import util
from cacheout import Cache

from configobj import ConfigObj

cache = Cache()
config_path = util.get_resource('~/wtfconfig.ini')

cfg = ConfigObj(config_path, encoding='UTF-8')


qmsg = cfg['notify']['qmsg']
pipehub = cfg['notify']['pipehub']
xtuis = cfg['notify']['xtuis']
aiops = cfg['notify']['aiops']
wx_corpid = cfg['notify']['wx_corpid']
wx_corpsecret = cfg['notify']['wx_corpsecret']
wx_agentid = cfg['notify']['wx_agentid']


def _get_wechat_token(req):
    resp = req.get(f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={wx_corpid}&corpsecret={wx_corpsecret}')
    return resp.json()['access_token']


def _send_wechat_message(req, access_token, content):
    return req.post('https://qyapi.weixin.qq.com/cgi-bin/message/send', params={
        "access_token": access_token
    }, json={
        "touser": "@all",
        "toparty": "PartyID1|PartyID2",
        "totag": "TagID1 | TagID2",
        "msgtype": "text",
        "agentid": wx_agentid,
        "text": {
            "content": content
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0
    })


def send_wechat(content: str):
    req = util.requests_session()
    access_token = cache.get('wechat_access_token')

    if not access_token:
        access_token = _get_wechat_token(req)
        # 2 hour expires
        cache.set('wechat_access_token', access_token, ttl=60 * 60 * 2)

    resp = _send_wechat_message(req, access_token, content)
    if resp.status_code == 40014 or resp.status_code == 42001 or resp.status_code == 42007 or resp.status_code == 42009:
        access_token = _get_wechat_token(req)
        cache.set('wechat_access_token', access_token, ttl=60 * 60 * 2)
        resp = _send_wechat_message(req, access_token, content)

    return resp.json()


def send_qq(content, qq=""):
    """
    https://qmsg.zendee.cn/api.html
    Qmsg酱
    @return:
    """
    return util.requests_session().post(f'https://qmsg.zendee.cn/send/{qmsg}', data={
        "msg": content,
        "qq": qq
    })


def send_pipehub(content):
    """
    https://www.pipehub.net
    @return:
    """
    return util.requests_session().post(f'https://api.pipehub.net/send/{pipehub}', data=content.encode('utf-8'))


def send_xtuis(text, desp=""):
    """
    https://wx.xtuis.cn
    @return:
    """
    return util.requests_session().post(f'https://wx.xtuis.cn/{xtuis}.send', data={
        "text": text,
        "desp": desp,
    })


def send_phone(content):
    import uuid
    return util.requests_session().post("http://api.aiops.com/alert/api/event", json={
        "app": aiops,
        "eventId": uuid.uuid4().hex,
        "eventType": "trigger",
        "alarmContent": content,
    })
