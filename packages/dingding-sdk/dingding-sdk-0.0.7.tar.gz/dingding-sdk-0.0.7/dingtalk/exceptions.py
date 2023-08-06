#!/usr/bin/python3
# @Time    : 2021-06-18
# @Author  : Kevin Kong (kfx2007@163.com)


class DingTalkException(Exception):

    def __init__(self, errcode=None, sub_code=None, sub_msg=None, errmsg=None, request_id=None):
        self.errcode = errcode
        self.sub_code = sub_code
        self.sub_msg = sub_msg
        self.errmsg = errmsg
        self.request_id = request_id

    def __str__(self):
        return f"""
errcode: {self.errcode} 
errmsg: {self.errmsg}
request_id: {self.request_id}
sub_code: {self.sub_code if self.sub_code else ''}
sub_msg: {self.sub_msg if self.sub_msg else ''}
"""


class DingTalkV2Exception(Exception):

    def __init__(self, code=None, requestid=None, message=None, accessdenieddetail=None):
        self.code = code
        self.requestid = requestid
        self.message = message
        self.accessdenieddetail = accessdenieddetail

    def __str__(self):
        return f"""
code: {self.code}
requestId: {self.requestid}
message: {self.message}
detail: {self.accessdenieddetail}
"""
