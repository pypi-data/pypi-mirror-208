#!/usr/bin/python3
# @Time    : 2021-06-30
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk
from dingtalk.workflow import Component, FormComponentProp


class TestWorkFlow(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, agentid=cls.agentid)

    def test_update_workflow(self):
        form_component_prop = FormComponentProp("TextField-12456", "测试审批")
        component = Component("TextField", form_component_prop)
        res = self.dingtalk.workflow.update_workflow(
            "测试审批", "这是一个测试审批", [component])
        self.assertTrue(res, res)

if __name__ == "__main__":
    unittest.main()
