#!/usr/bin/python3
# @Time    : 2021-06-21
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk


class TestMessage(TestCase):

    task_id = None

    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, agentid=cls.agentid)

    def test_send_notication(self):
        depts = self.dingtalk.department.get()
        res = self.dingtalk.workmessage.send_notification(
            {"msgtype": "text", "text": {"content": "快点提交日报啊。"}}, dept_id_list=depts[0]['dept_id'])
        self.assertTrue
        TestMessage.task_id = res

    def test_get_notificatioin_progress(self):
        res = self.dingtalk.workmessage.get_notificatioin_progress(
            self.task_id)
        print(res)
        self.assertIsInstance(res, dict, res)

    def test_get_notificatioin_result(self):
        res = self.dingtalk.workmessage.get_notification_result(self.task_id)
        self.assertIsInstance(res, dict, res)
        print(res)

    def test_update_status_bar(self):

        res = self.dingtalk.workmessage.update_status_bar(self.task_id, 'YES')
        self.assertTrue(res)

    def test_recall(self):
        res = self.dingtalk.workmessage.recall(self.task_id)
        self.assertTrue(res)


if __name__ == "__main__":
    suit = TestSuite()
    suit.addTest(TestMessage("test_send_notication"))
    suit.addTest(TestMessage("test_get_notificatioin_progress"))
    suit.addTest(TestMessage("test_get_notificatioin_result"))
    suit.addTest(TestMessage("test_update_status_bar"))
    # suit.addTest(TestMessage("test_recall"))

    unittest.TextTestRunner(verbosity=3).run(suit)
