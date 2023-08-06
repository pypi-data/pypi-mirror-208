#!/usr/bin/python3
# @Time    : 2021-06-18
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest import TestCase, TestSuite
from dingtalk.dingtalk import DingTalk


class TestContact(TestCase):

    department_id = None
    role_id = None
    group_id = None
    user_id = None

    @classmethod
    def setUpClass(cls):
        cls.appkey = "dingtjjs1pr7nlgmtoxc"
        cls.appsecret = "8a6Ltc8_w-BNpqVOXg3dUH_1PHxxgmWnuf6Gt1ZcQqaMR3fYDDD6rs3Jnmzxr9uy"
        cls.agentid = 1218698174
        cls.dingtalk = DingTalk(cls.appkey, cls.appsecret, cls.agentid)

    def test_create_department(self):
        if not TestContact.department_id:
            res = self.dingtalk.department.create("Test")
            self.assertIsInstance(res, int, res)
            TestContact.department_id = res

    def test_get_departments(self):
        res = self.dingtalk.department.get()
        self.assertGreaterEqual(len(res), 0, res)
        for dept in res:
            if dept['name'].lower() == 'test':
                TestContact.department_id = dept['dept_id']

    def test_update_department(self):
        res = self.dingtalk.department.update(self.department_id, name="TEST")
        self.assertTrue(res)

    def test_get_department_info(self):
        res = self.dingtalk.department.get_info(self.department_id)
        self.assertIsInstance(res, dict)

    def test_get_department_children(self):
        res = self.dingtalk.department.get_children(self.department_id)
        self.assertIsInstance(res, list)

    def test_get_user_departments(self):
        res = self.dingtalk.department.get_user_departments(100)
        self.assertIsInstance(res, list)

    def test_get_parents(self):
        res = self.dingtalk.department.get_parents(self.department_id)
        self.assertIsInstance(res, list)

    def test_delete_department(self):
        res = self.dingtalk.department.delete(self.department_id)
        self.assertTrue(res)

    def test_create_role(self):
        res = self.dingtalk.role.create("TestRole", TestContact.group_id)
        self.assertIsInstance(res, int)
        TestContact.role_id = res

    def test_create_role_group(self):
        # get role first
        res = self.dingtalk.role.get()
        for group in res['list']:
            if group['name'].lower() == 'testrolegroup':
                TestContact.group_id = group['groupId']

        if not TestContact.group_id:
            res = self.dingtalk.role.create_group("TestRoleGroup")
            self.assertIsInstance(res, int)
            TestContact.group_id = res

    def test_update_role(self):
        res = self.dingtalk.role.update(TestContact.role_id, "TESTRole")
        self.assertTrue(res)

    def test_add_roles_to_users(self):
        res = self.dingtalk.role.add_roles_to_users()
        self.assertTrue(res)

    def test_delete_role(self):
        res = self.dingtalk.role.delete(TestContact.role_id)
        self.assertTrue(res)

    def test_get_role_list(self):
        res = self.dingtalk.role.get()
        self.assertIsInstance(res, dict)

    def test_get_role_detail(self):
        res = self.dingtalk.role.get_detail(TestContact.role_id)
        self.assertIsInstance(res, dict)

    def test_create_user(self):
        res = self.dingtalk.user.create(
            "TestUser", "18512345678", str(self.department_id))
        self.assertIsInstance(res, int)
        TestContact.user_id = res

    def test_update_user(self):
        res = self.dingtalk.user.update(TestContact.user_id, "18512345678")
        self.assertTrue(res)

    def test_delete_user(self):
        res = self.dingtalk.user.delete(TestContact.user_id)
        self.assertTrue(res)

    def test_get_user_info(self):
        res = self.dingtalk.user.get(TestContact.user_id)
        self.assertIsInstance(res, dict)

    def test_get_users_by_dept(self):
        res = self.dingtalk.user.get_users_by_department(
            TestContact.department_id)
        self.assertIsInstance(res, dict)

    def test_get_usersids_by_dept(self):
        res = self.dingtalk.user.get_userids_by_department(1)
        self.assertIsInstance(res, list)

    def test_get_userinfo_by_dept(self):
        res = self.dingtalk.user.get_userinfo_by_department(1)
        self.assertIsInstance(res, dict)

    def test_get_managers(self):
        res = self.dingtalk.user.get_managers()
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    suit = TestSuite()
    suit.addTest(TestContact("test_get_departments"))
    # suit.addTest(TestContact("test_create_department"))
    # suit.addTest(TestContact("test_update_department"))
    # suit.addTest(TestContact("test_get_department_children"))
    # suit.addTest(TestContact("test_get_parents"))
    # suit.addTest(TestContact("test_create_role_group"))
    # suit.addTest(TestContact("test_create_role"))
    # suit.addTest(TestContact("test_update_role"))
    # suit.addTest(TestContact("test_get_role_list"))
    # suit.addTest(TestContact("test_get_role_detail"))
    # # suit.addTest(TestContact("test_create_user"))
    # # suit.addTest(TestContact("test_get_user_info"))
    # suit.addTest(TestContact("test_get_users_by_dept"))
    # suit.addTest(TestContact("test_get_usersids_by_dept"))
    # suit.addTest(TestContact("test_get_userinfo_by_dept"))
    # suit.addTest(TestContact("test_get_managers"))

    # # suit.addTest(TestContact("test_delete_user"))
    # suit.addTest(TestContact("test_delete_role"))
    # suit.addTest(TestContact("test_delete_department"))

    unittest.TextTestRunner(verbosity=3).run(suit)
