#!/usr/bin/python3
# @Time    : 2023-05-09
# @Author  : Kevin Kong (kfx2007@163.com)

import json
from dingtalk.core import Core, NEW_URL


class RobotFile(object):
    def __init__(self, media_id, file_name, file_type):
        self.media_id = media_id
        self.file_name = file_name
        self.file_type = file_type
        self.key = "sampleFile"

    def __repr__(self):
        return f"<Robot FIle,{self.media_id},{self.file_name},{self.file_type}>"

    def __str__(self):
        return self.file_name

    def to_json(self):
        return {
            "mediaId": self.media_id,
            "fileName": self.file_name,
            "fileType": self.file_type
        }


class Robot(Core):

    def __init__(self, code=None):
        self.code = code

    def push_text_group_message(self, text, conver_id=None, coolAppCode=None):
        url = f"{NEW_URL}/v1.0/robot/groupMessages/send"

        data = {
            "msgParam": str({"content": text}),
            "msgKey": "sampleText",
            "robotCode": self.code,
        }

        if conver_id:
            data['openConversationId'] = conver_id
        if coolAppCode:
            data['coolAppCode'] = coolAppCode

        # data = json.dumps(data)

        res = self._v2_post(url, json=data)
        return res

    def push_markdown_group_message(self, title, text, conver_id=None, coolAppCode=None):
        url = f"{NEW_URL}/v1.0/robot/groupMessages/send"

        data = {
            "msgParam": str({"title": title, "text": text}),
            "msgKey": "sampleMarkdown",
            "robotCode": self.code,
        }

        if conver_id:
            data['openConversationId'] = conver_id
        if coolAppCode:
            data['coolAppCode'] = coolAppCode

        # data = json.dumps(data)
        print('----')
        print(data)
        res = self._v2_post(url, json=data)
        return res

    def push_file_group_message(self, file, conver_id=None, coolAppCode=None):
        """
            push message to chat.

            :param file: Robot File
            :param conver_id: Conversation Id

            :return 

        """

        url = f"{NEW_URL}/v1.0/robot/groupMessages/send"

        data = {
            "msgParam": str(file.to_json()),
            "msgKey": file.key,
            "robotCode": self.code,
        }
        if conver_id:
            data['openConversationId'] = conver_id
        if coolAppCode:
            data['coolAppCode'] = coolAppCode

        res = self._v2_post(url, data)
        return res
