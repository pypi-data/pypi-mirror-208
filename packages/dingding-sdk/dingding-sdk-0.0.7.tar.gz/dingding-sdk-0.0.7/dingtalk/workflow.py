#!/usr/bin/python3
# @Time    : 2021-06-29
# @Author  : Kevin Kong (kfx2007@163.com)

from .core import Core, URL


class Component(object):

    def __init__(self, name, props):

        self.component_name = name
        self.props = props

    def to_json(self):
        return {
            "component_name": self.component_name,
            "props": self.props.to_json()
        }


class FormComponentProp(object):

    def __init__(self, id, label, required=False):

        self.id = id
        self.label = label
        self.required = required

    def to_json(self):
        return {
            "id": self.id,
            "label": self.label,
            "required": self.required
        }


class WorkFlow(Core):

    def update_workflow(self, name, description, form_components, process_code=None,):
        """
        create or update process template.

        :param name: component name.
        :param description: description of process.
        :param form_components: form component list.
        :param process_code: unique code of process.

        :return result: True.
        """
        url = f"{URL}/topapi/process/save"
        data = {
            "saveProcessRequest": {
                "agentid": self._agentid,
                "name": name,
                'process_code': process_code,
                "description": description,
                "form_component_list": [comp.to_json() for comp in form_components]
            }

        }
        res = self._post(url, data)
        return res['result']
