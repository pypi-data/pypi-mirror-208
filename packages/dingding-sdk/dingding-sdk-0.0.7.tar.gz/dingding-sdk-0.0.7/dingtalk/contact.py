#!/usr/bin/python3
# @Time    : 2021-06-18
# @Author  : Kevin Kong (kfx2007@163.com)

from dingtalk.core import Core, URL

class Department(Core):

    def get(self, dept_id=None, lang=None):
        """
        get department list
       
        :param dept_id: int id of department, get all departments if dept_id is None
        :param lang: language of contacts

        :return result: list of departments
        """
        # [{'auto_add_user': True, 'create_dept_group': True, 'dept_id': 147953855, 'name': '财务部', 'parent_id': 1}]
        url = f"{URL}/topapi/v2/department/listsub"
        res = self._post(url, data={
            "dept_id": dept_id,
            "language": lang
        })
        return res['result']

    def create(self, name, parent_id=1, **kwargs):
        """
        create a department.

        :param name:  department name
        :param parent_id: parent department id, default 1 root department.
        :param hide_dept: whether hide the department
        :param dept_permits: who can view the department, limit 200 departments.
        :param user_permits: who can view the department, limit 200 persons.
        :param outer_dept: restrict members of this department from viewing the address book.
        :param outer_dept_only_self: whether members of this department can only see the address book of their department and subordinate departments
        :param outer_permit_users: specify the userid list of address book users that the members of this department can view, the total cannot exceed 200
        :param outer_permit_depts: specify a list of department IDs in the address book that members of this department can view, the total number cannot exceed 200
        :param create_dept_group: whether to create an enterprise group associated with this department
        :param order: for the sort value in the parent department, the lower order value is sorted first
        :param source_identifier: department identification field, developers can use this field to uniquely identify a department and map it with the department in the external address book of DingDing

        :return dept_id: deparment id of new created department.
        """
        url = f"{URL}/topapi/v2/department/create"
        data = {'name': name, 'parent_id': parent_id}
        data.update(kwargs)
        res = self._post(url, data=data)
        return res['result']['dept_id']

    def update(self, dept_id, **kwargs):
        """
        udpate department.

        :param dept_id: the department id which to update.
        :param name:  department name
        :param language:  language of department.
        :param parent_id: parent department id, default 1 root department.
        :param hide_dept: whether hide the department
        :param dept_permits: who can view the department, limit 200 departments.
        :param user_permits: who can view the department, limit 200 persons.
        :param outer_dept: restrict members of this department from viewing the address book.
        :param outer_dept_only_self: whether members of this department can only see the address book of their department and subordinate departments
        :param outer_permit_users: specify the userid list of address book users that the members of this department can view, the total cannot exceed 200
        :param outer_permit_depts: specify a list of department IDs in the address book that members of this department can view, the total number cannot exceed 200
        :param create_dept_group: whether to create an enterprise group associated with this department
        :param order: for the sort value in the parent department, the lower order value is sorted first
        :param source_identifier: department identification field, developers can use this field to uniquely identify a department and map it with the department in the external address book of DingDing
        :param auto_add_user: whether auto add user into group when user been added to department.
        :param dept_manager_userid_list: update manager list of department
        :param group_contain_sub_dept: whether has child department.
        :param group_contain_outer_dept: whether has outside department
        :param group_contain_hidden_dept: whether has hide department.
        :param org_dept_owner: the host of group.

        :return result: True or False
        """
        url = f"{URL}/topapi/v2/department/update"
        data = {'dept_id': dept_id}
        data.update(kwargs)
        res = self._post(url, data=data)
        return True

    def delete(self, dept_id):
        """
        delete department

        :param dept_id: department id which is going to be deleted.
        
        :return result: True
        """
        url = f"{URL}/topapi/v2/department/delete"
        data = {'dept_id': dept_id}
        self._post(url, data=data)
        return True

    def get_info(self, dept_id, lang=None):
        """
        get detail infos of department.

        :param dept_id: department id
        :param lang: language of department.

        :return result: department infos.
        """
        url = f"{URL}/topapi/v2/department/get"
        data = {'dept_id': dept_id, 'language': lang}
        res = self._post(url, data=data)
        return res['result']

    def get_children(self, dept_id):
        """
        get childen of the department.

         :param dept_id: department id
         :return departments: id list of children deparments
        """
        url = f"{URL}/topapi/v2/department/listsubid"
        data = {'dept_id': dept_id}
        res = self._post(url, data)
        return res['result']['dept_id_list']

    def get_user_departments(self, userid):
        """
        get all departments of given user.

        :param userid: user id.

        :return parent_list: user's departments.
        """
        url = f"{URL}/topapi/v2/department/listparentbyuser"
        data = {'userid': userid}
        res = self._post(url, data)
        return res['result']['parent_list']

    def get_parents(self, dept_id):
        """
        get parents of one department.

        :param dept_id: id of department
        :param parent_id_list: id list of parent departments

        :return parent_ids: list of parent ids.
        """
        url = f"{URL}/topapi/v2/department/listparentbydept"
        data = {'dept_id': dept_id}
        res = self._post(url, data)
        return res['result']['parent_id_list']


class Role(Core):

    def create(self, name, groupid):
        """
        create role

        :param name: role name
        :param groupid: group id

        :return role_id: id of new created role.
        """
        url = f"{URL}/role/add_role"
        data = {'roleName': name, 'groupId': groupid}
        res = self._post(url, data)
        return res['roleId']

    def create_group(self, name):
        """
        create role group

        :param name: group name
        :return groupId: group id
        """
        url = f"{URL}/role/add_role_group"
        data = {'name': name}
        res = self._post(url, data)
        return res['groupId']

    def update(self, roleid, rolename):
        """
        update role

        :param roleid: role id
        :param rolename: rolename

        :return result: True
        """
        url = f"{URL}/role/update_role"
        data = {'roleId': roleid, 'roleName': rolename}
        res = self._post(url, data)
        return True

    def add_roles_to_users(self, roles, users):
        """
        add roles to users.

        :param roles: roles
        :param users: users

        :return result: True
        """
        url = "f{URL}/role/addrolesforemps"
        data = {'roleIds': roles, 'userIds': users}
        res = self._post(url, data)
        return True

    def delete(self, role_id):
        """
        delete role

        :param role_id: id of role which is going to be deleted.

        :return result: True
        """
        url = f"{URL}/topapi/role/deleterole"
        data = {'role_id': role_id}
        res = self._post(url, data)
        return True

    def delete_users_roles(self, roleids, userids):
        """
        delete users' roles

        :param roleIds: roles
        :param userids: users

        :return result: True
        """
        url = f"{URL}/topapi/role/removerolesforemps"
        data = {'roleIds': roleids, 'userIds': userids}
        res = self._post(url, data)
        return True

    def get_by_groupid(self, group_id):
        """
        get role groups list.

        :param group_id: id of group.

        :return role_group: role group detail
        """

        url = f"{URL}/topapi/role/getrolegroup"
        data = {'group_id': group_id}
        res = self._post(url, data)
        return res['role_group']

    def get(self, size=20, offset=0):
        """
        get role list

        :param size: support paging query, it will take effect only when it is set at the same time with the offset parameter. This parameter represents the page size, the default value is 20, the maximum value is 200
        :param offset: offset

        :return roles list: {hasMore:True/False,'list':[{'groupId':'xx','name':'xx','roles':[{'id':1,'name':'xx'}]}]}
        """
        url = f"{URL}/topapi/role/list"
        data = {'size': size, 'offset': offset}
        res = self._post(url, data)
        return res['result']

    def get_detail(self, roleid):
        """
        get role detail

        :param roleid: id of the role.

        :return role: role
        """

        url = f"{URL}/topapi/role/getrole"
        data = {'roleId': roleid}
        res = self._post(url, data)
        return res['role']

    def get_users(self, roleid, size=20, offset=0):
        """
        get users by role.

        :param roleid: role id.
        :param size: page size
        :param offset: offset

        :return result:user list
        """

        url = f"{URL}/topapi/role/simplelist"
        data = {'role_id': roleid, 'size': size, 'offset': offset}
        res = self._post(url, data)
        return res['result']

    def set_role_scope(self, userid, roleid, dept_ids):
        """
        setting scope of role users.

        :param userid: user id
        :param roleid: role id
        :param dept_ids: department ids, using , seperate 

        :return result: True
        """

        url = f"{URL}/topapi/role/scope/update"
        data = {'userid': userid, 'role_id': roleid, 'dept_ids': dept_ids}
        res = self._post(url, data)
        return True


class User(Core):

    def create(self, name, mobile, dept_ids, **kwargs):
        """
        create user new user.

        :param name: name of user.
        :param mobile: mobile
        :param dept_ids: department ids
        :param userid: unque id in enterprise. 
        :param hide_mobile: whether hide the mobile
        :param telephone: tel 
        :param job_number: work number.
        :param title: job title.
        :param org_email: email
        :param work_place: work place.
        :param remark: remark
        :param dept_order_list: the order user in departments.   [{'dept_id':x,'order':1}]
        :param dept_title_list: the title user in departments. [{'dept_id':x,'title':'xx'}]
        :param extension: extension
        :param senior_mode: true/false 
        :param hired_date: hire date
        :param login_email: login email
        :param exclusive_account: whether special account.
        :param exclusive_account_type: selection sso or dingtalk.
        :param login_id: dingtalk login id
        :param init_password: init password.
        :return userid: id of new created User.
        """

        url = f"{URL}/topapi/v2/user/create"
        data = {'name': name, 'mobile': mobile, 'dept_id_list': dept_ids}
        data.update(kwargs)
        res = self._post(url, data)
        return res['result']['userid']

    def update(self, userid, mobile, **kwargs):
        """
        update user info.

        :param userid: user id
        :param mobile: mobile
        :param dept_ids: department ids
        :param userid: unque id in enterprise. 
        :param hide_mobile: whether hide the mobile
        :param telephone: tel 
        :param job_number: work number.
        :param title: job title.
        :param org_email: email
        :param work_place: work place.
        :param remark: remark
        :param dept_order_list: the order user in departments.   [{'dept_id':x,'order':1}]
        :param dept_title_list: the title user in departments. [{'dept_id':x,'title':'xx'}]
        :param extension: extension
        :param senior_mode: true/false 
        :param hired_date: hire date
        :param language: language of contacts.
        :return result: True
        """
        url = f"{URL}/topapi/v2/user/update"
        data = {'userid': userid, 'mobile': mobile}
        data.update(kwargs)
        res = self._post(url, data)
        return True

    def delete(self, userid):
        """
        delete user.

        :param userid: user id
        :return True
        """
        url = f'{URL}/topapi/v2/user/delete'
        data = {'userid': userid}
        self._post(url, data)
        return True

    def get(self, userid, lang=None):
        """
        get user detail info.

        :param userid: user id
        :param lang: language of contact.

        :return object: user infos.(dict)
        """
        url = f"{URL}/topapi/v2/user/get"
        data = {'userid': userid, 'language': lang}
        res = self._post(url, data)
        return res['result']

    def get_users_by_department(self, dept_id, cursor=0, size=10, **kwargs):
        """
        get user name and ids by department.
test_create_user
        :param dept_id: id of department.
        :param cursor: offset , default 0
        :param size: page size , max 100.
        :param order_field: order rule of department. 
        :param contain_access_limit: true/false whether contains limited users.
        :param language: language of contacts

        :return object: user and name list object; {'has_more':true,'next_cursor':10,'list':[{'name':xx,'userid':xx}]}
        """

        url = f"{URL}/topapi/user/listsimple"
        data = {'dept_id': dept_id, 'cursor': cursor, 'size': size}
        data.update(kwargs)
        res = self._post(url, data)
        return res['result']

    def get_userids_by_department(self, dept_id):
        """
        get user ids by department.

        :param dept_id: department id
        :return userId_list: list of userids. 
        """
        url = f"{URL}/topapi/user/listid"
        data = {'dept_id': dept_id}
        res = self._post(url, data)
        return res['result']['userid_list']

    def get_userinfo_by_department(self, dept_id, cursor=0, size=10, **kwargs):
        """
        get userinfos by department.

        :param dept_id: id of department.
        :param cursor: offset , default 0
        :param size: page size , max 100.
        :param order_field: order rule of department. 
        :param contain_access_limit: true/false whether contains limited users.
        :param language: language of contacts
        :return object: user 'and name list object
        """

        url = f"{URL}/topapi/v2/user/list"
        data = {'dept_id': dept_id, 'cursor': cursor, 'size': size}
        data.update(kwargs)
        res = self._post(url, data)
        return res['result']

    def get_users_count(self, only_active=False):
        """
        get users count.

        :param only_active: whether the unactive user into consideration.
        :return count of users.
        """
        url = f"{URL}/topapi/user/count"
        data = {'only_active': only_active}
        res = self._post(url, data)
        return res['result']['count']

    def get_inactive_users(self, query_date, is_active=False, offset=0, size=100, **kwargs):
        """
        get users who was  unactive.

        :param query_date: query date, format: yyyyMMdd
        :param is_active: whether user is active
        :param offset: offset
        :param size: page size.
        :param dept_ids: department ids. get whole enterprise if dept_ids is None
        :return result
        """

        url = f"{URL}/topapi/inactive/user/v2/get"
        data = {'query_date': query_date, 'is_active': is_active,
                'offset': offset, 'size': size}
        data.update(kwargs)
        res = self._post(url, data)
        return res['result']

    def get_managers(self):
        """
        get user managers.

        :return list of result [userid,sys_level]
        """
        url = f"{URL}/topapi/user/listadmin"
        res = self._post(url, None)
        return res['result']

    def get_manager_contact_scope(self, user_id):
        """
        get scope of manager's contacts

        :param: user_id: manager user id.
        :return dept_is: departments which he can manage.
        """

        url = f"{URL}/topapi/user/get_admin_scope"
        data = {'user_id': user_id}
        res = self._post(url, data)
        return res['result']['dept_ids']

    def get_manager_app_scope(self):
        """
        get scope of manager's apps

        """
        # [TODO]
        pass

    def get_userid_by_phone(self, mobile):
        """
        get userid by phone number.

        :param mobile: phone number.
        :return userid
        """

        url = f"{URL}/topapi/v2/user/getbymobile"
        data = {'mobile': mobile}
        res = self._post(url)
        return res['result']['userid']

    def get_userid_by_unionid(self, unionid):
        """
        get userid by union id.

        :param unionid: unionid
        :return dict: {contact_type,userid} contact_type: 0 internal 1 external employee.
        """

        url = f"{URL}/topapi/user/getbyunionid"
        data = {'unionid': unionid}
        res = self._post(url, data)
        return res['result']

    def get_unlogin_users(self, query_date, offset=0, size=100):
        """
        get user who havent login during last month.

        :param query_date: query date, format yyyyMMdd
        :param offset: offset
        :param size: page size.
        """

        url = f"{URL}/topapi/inactive/user/get"
        data = {'query_date': query_date, 'offset': offset, 'size': size}
        res = self._post(url, data)
        return res['result']
