#!/usr/bin/python3
# @Time    : 2023-05-08
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk

class TestDocument(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, cls.agentid)

    def test_upload_document(self):
        with open('/root/codes/projects/github/dingding-sdk/tests/test.txt') as f:
            file = f.read()
        res = self.dingtalk.doc.upload("file",file)
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()