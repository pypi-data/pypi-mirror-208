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

    # def test_create_chat(self):
    #     res = self.dingtalk.session.create_chat("测试群","manager2643",["manager2643"])
    #     print(res)
    #     self.assertTrue(res)

    def test_get_bots(self):
        res = self.dingtalk.session.get_robots("cid3w3JQmMUWe0OOgEX1osVEg====")
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()