#!/usr/bin/python3
# @Time    : 2023-05-08
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk
from dingtalk.robot import RobotFile
from io import BytesIO

class TestRobot(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, cls.agentid)

    def test_push_group_message(self):
        #上传文件
        # buffer = BytesIO()
        # buffer.write(f"""
        #     ASBXCS
        # """.encode('utf-8'))
        # file = buffer.getvalue()
        # media_id = self.dingtalk.doc.upload("file", file)
        # media_id = "@lAjPDgCwbMno3NTOBLLHs85BmCi_"
        # robot_file = RobotFile(media_id, "test.txt","txt")
        # self.dingtalk.robot.code = "dingtjjs1pr7nlgmtoxc"
        # # res = self.dingtalk.robot.push_text_group_message("1234",conver_id="cid3w3JQmMUWe0OOgEX1osVEg==")
        # res = self.dingtalk.robot.push_file_group_message(robot_file,conver_id="cid3w3JQmMUWe0OOgEX1osVEg==")
        # print(res)
        # self.assertTrue(res)
        pass

    def test_push_markdown_group_message(self):
        media_id = "@lAjPDgCwbMno3NTOBLLHs85BmCi_"
        # robot_file = RobotFile(media_id, "test.txt","txt")
        self.dingtalk.robot.code = "dingtjjs1pr7nlgmtoxc"
        # res = self.dingtalk.robot.push_text_group_message("1234",conver_id="cid3w3JQmMUWe0OOgEX1osVEg==")
        mk = f"""
|标题1|题2|
|----|----|
|1|1|
"""
        res = self.dingtalk.robot.push_markdown_group_message("测试Markdown",mk,conver_id="cid3w3JQmMUWe0OOgEX1osVEg==")
        print(res)
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()