#!/usr/bin/python3
# @Time    : 2023-05-08
# @Author  : Kevin Kong (kfx2007@163.com)

from dingtalk.core import Core, URL, NEW_URL


class Space(Core):

    def __init__(self, union_id=None):
        self.union_id = union_id
        self.space_id = None
        self.corpId = None

    def get_info(self, conver_id):
        """
            get space info.

            :param unionid: User UnionId
            :param conver_id: Conversation Id
            :return dict: space info
        """

        url = f"{NEW_URL}/v1.0/convFile/conversations/spaces/query?unionId={self.union_id}"

        data = {
            "openConversationId": conver_id
        }

        res = self._v2_post(url, data)
        if res.get('space'):
            self.space_id = res['space']['spaceId']
            self.corpId = res['space']['corpId']
