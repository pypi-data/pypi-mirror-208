#!/usr/bin/python3
# @Time    : 2021-06-18
# @Author  : Kevin Kong (kfx2007@163.com)

from .core import Core
from .contact import Department, Role, User
from .message import WorkMessage
from .hr import HR
from .workflow import WorkFlow
from .document import Document
from .session import Session
from .space import Space
from .robot import Robot


class DingTalk(object):

    def __init__(self,  appkey, appsecret, corpid=None, agentid=None, suitticket=None):
        """
        init dingtalk client

        params:
        corpid: Corpration Id
        appkey: app key
        appsecret: app secret
        suitticket: suit ticket from dingtalk when using third party app.
        """
        self._corpid = corpid
        self._appkey = appkey
        self._appsecret = appsecret
        self._suitticket = suitticket
        self._agentid = agentid

    core = Core()
    department = Department()
    role = Role()
    user = User()
    workmessage = WorkMessage()
    hr = HR()
    workflow = WorkFlow()
    doc = Document()
    session = Session()
    space = Space()
    robot = Robot()

    def set_user(self, user_id):
        """
            set user.
        """
        user_info = self.user.get(user_id)
        union_id = user_info['unionid']
        self.space.union_id = union_id
        self.doc.union_id = union_id
        self.session.union_id = union_id