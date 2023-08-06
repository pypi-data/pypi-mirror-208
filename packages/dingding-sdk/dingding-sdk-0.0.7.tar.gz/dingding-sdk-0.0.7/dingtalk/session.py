#!/usr/bin/python3
# @Time    : 2023-05-08
# @Author  : Kevin Kong (kfx2007@163.com)

from dingtalk.core import Core, URL, NEW_URL


class Session(Core):

    def __init__(self, union_id=None, space_id=None):
        self.union_id = union_id
        self.space_id = space_id

    def create_chat(self, name, owner, userlist, show_history=1,
                    searchable=1, need_validate=0, user_all=0, manage_all=0, ban=1):
        """
            create chat.

            :param name: Chat Name
            :param owner: owner user id
            :param userlist: users list
            :param show_history: show history.(1/0 enable/unable)
            :param searchable: can be search or not.
            :param need_validate: need validate or not when new user in.
            :param user_all: wether all user can use @all or not(manager only).
            :param manage_all: wether all users can manage the chat.
            :param ban: mute the chat.(no one can talk)
        """

        url = f"{URL}/chat/create"

        data = {
            "name": name,
            "owner": owner,
            "useridlist": userlist,
            "showHistoryType": show_history,
            "searchable": searchable,
            "validationType": need_validate,
            "mentionAllAuthority": user_all,
            "managementType": manage_all,
            "chatBannedType": ban
        }

        return self._post(url, data)

    def send_file(self, file_id, conver_id):
        """
            send file to chat
        """

        url = f"{NEW_URL}/v1.0/convFile/conversations/files/send?unionId={self.union_id}"

        data = {
            "spaceId": self.space_id,
            "dentryId": file_id,
            "openConversationId": conver_id
        }

        return self._v2_post(url, data)

    def get_robots(self, conver_id):
        """
            get robots
        """

        url = f"{NEW_URL}/v1.0/robot/groups/robots/query"

        data = {
            "openConversationId": conver_id
        }

        return self._v2_post(url, data)
