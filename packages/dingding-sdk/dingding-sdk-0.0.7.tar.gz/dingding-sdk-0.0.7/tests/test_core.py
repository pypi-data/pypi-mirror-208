#!/usr/bin/python3
# @Time    : 2021-06-18
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase
from dingtalk.dingtalk import DingTalk


class TestCore(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret)  

    def test_get_enterprise_access_token(self):
        res = self.dingtalk.core._get_enterprise_access_token()
        self.assertEqual(res['errcode'], 0, res)

if __name__ == "__main__":
    unittest.main()
