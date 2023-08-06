#!/usr/bin/python3
# @Time    : 2023-05-08
# @Author  : Kevin Kong (kfx2007@163.com)

from .core import Core, URL, NEW_URL
import requests


class Document(Core):

    def __init__(self, union_id=None, space_id=None):
        self.union_id = union_id
        self.space_id = space_id
        self.file_id = None

    def upload(self, type, file):
        """
            upload media file.

            :param type: file type.
            :param fiels: files.

            :return media_id
        """

        url = f"{URL}/media/upload"

        data = {
            "type": type,
        }

        files = {
            "media": file
        }

        res = self._post(url, data=data, files=files)
        return res['media_id']

    def get_upload_file_info(self, protocol="HEADER_SIGNATURE", multipart=False, options=None):
        """
            get info before upload file
        """

        url = f"{NEW_URL}/v1.0/storage/spaces/{self.space_id}/files/uploadInfos/query?unionId={self.union_id}"

        data = {
            "protocol": protocol,
            "multipart": multipart,
            "option": options
        }

        res = self._v2_post(url, data)
        return res

    def oss_put_file(self, url, headers, file_stream):
        """
            put file to oss.
        """

        return requests.put(url, data=file_stream, headers=headers)

    def upload_file(self,upload_key, name, parent_id, options=None):
        """
            upload file
        """

        url = f"{NEW_URL}/v1.0/storage/spaces/{self.space_id}/files/commit?unionId={self.union_id}"

        data = {
            "uploadKey": upload_key,
            "name": name,
            "parentId": parent_id,
            "option": options
        }

        res = self._v2_post(url, data)
        if res.get("dentry"):
            self.file_id = res['dentry']['id']
