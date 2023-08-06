#!/usr/bin/python3
# @Time    : 2021-06-29
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk


class TestHR(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, cls.agentid)

    def test_get_official_employees(self):
        res = self.dingtalk.hr.get_official_employees()
        self.assertIsInstance(res, dict, res)

    def test_get_candidates(self):
        res = self.dingtalk.hr.get_candidates()
        self.assertIsInstance(res, dict, res)

    def test_get_dimission_userids(self):
        res = self.dingtalk.hr.get_dimission_userids()
        self.assertIsInstance(res, dict, res)

    def test_get_dimission_info(self):
        res = self.dingtalk.hr.get_dimission_info("1,2")
        self.assertIsInstance(res, list, res)


if __name__ == "__main__":
    unittest.main()
