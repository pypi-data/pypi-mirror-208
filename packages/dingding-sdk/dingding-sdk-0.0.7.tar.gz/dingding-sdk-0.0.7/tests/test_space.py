#!/usr/bin/python3
# @Time    : 2023-05-08
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk


class TestSession(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, cls.agentid)

    def test_get_space_info(self):
        self.dingtalk.set_user("manager2643")
        # user_info = self.dingtalk.user.get("manager2643")
        # chat_info = self.dingtalk.session.create_chat("测试群","manager2643",["manager2643"])
        chat = "cid0H8UpqQfd5/IrcPDvsxuTQ=="
        # print(chat_info)
        # res = self.dingtalk.space.get_info(user_info['unionid'],chat_info['openConversationId'])
        self.dingtalk.space.get_info(chat)
        spaceId = self.dingtalk.space.id
        with open('/root/codes/projects/github/dingding-sdk/tests/test.txt') as f:
            file = f.read()
        self.dingtalk.doc.space_id = spaceId
        pre_info = self.dingtalk.doc.get_upload_file_info()
        print('----preinfo----')
        print(pre_info)
        headerSignInfo = pre_info['headerSignatureInfo']
        self.dingtalk.doc.oss_put_file(headerSignInfo['resourceUrls'][0],headerSignInfo['headers'], file)
        self.dingtalk.doc.upload_file(pre_info['uploadKey'],'test.txt',0)
        file_id = self.dingtalk.doc.file_id
        # file_id = self.dingtalk.doc.upload("file", file)
        # print(res)
        # file_id = res['media_id']

        # 需要在群空间设置里开启云存储
        self.dingtalk.session.space_id = spaceId
        xxx = self.dingtalk.session.send_file(file_id, chat)
        print('==================')
        print(xxx)
        # 发送文件
        self.assertTrue(xxx)


if __name__ == "__main__":
    unittest.main()
