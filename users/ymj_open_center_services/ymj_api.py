# -*- coding: utf-8 -*-

import requests
from . import security
import logging

from config.settings.base import YMJ_CONFIG

logger = logging.getLogger('django')


def post_request(url, params):
    """
    post 请求
    :param url: 请求的url
    :param params:请求参数
    :return:
    """
    headers = {'content-type': 'application/json'}
    payload = security.encrypt(params)
    logger.info('ymj login message: ' + str(params))
    r = requests.post(YMJ_CONFIG['base_url'] + url, data=payload, headers=headers)
    dct = security.decrypt(r.text)
    logger.info('ymj login result message: ' + str(dct))
    return dct


def ymj_login(email, password):
    """
    易美健登录验证
    :param email: 邮箱
    :param password: 密码
    :return:
    """
    content = {"email": email, "password": password}
    login_dict = post_request("/open/v1/accounts/authenticate", content)
    return login_dict


# 没有值
def ymj_my_permissions(email):
    """
    用户所有权限组信息
    :param email:
    :return:
    {'status': 1, 'status_text': 'ok', 'data': '{"roles":[]}'}
    """
    content = {"email": email}
    dct = post_request("/open/v1/admins/role_groups", content)
    return dct


def ymj_my_info(email):
    """
    用户详细信息
    :param email:
    :return:{'status': 1, 'status_text': 'ok', 
    'data': '{"roles":{"id":138,"email":"panyu@yimeijian.cn","name":"潘裕","mobile_number":"18770223348","sensitive_info":1}}'}
    """
    content = {"email": email}
    dct = post_request("/open/v1/admins/detail_info", content)
    return dct


def ymj_department_info(email):
    """
    用户部门信息
    :param email:
    :return:{'status': 1, 'status_text': 'ok', 'data': '{"id":65,"name":"数据"}'}

    """
    content = {"email": email}
    dct = post_request("/open/v1/admins/department_info", content)
    return dct


def ymj_parent_department_info(email):
    """
    用户父级部门
    :param email:
    :return:
    """
    content = {"email": email}
    dct = post_request("/open/v1/admins/parent_department_info", content)
    return dct


def ymj_ancestor_departments(email):
    """
    用户所有祖先departments
    :param email:
    :return:
    """
    content = {"email": email}
    dct = post_request("/open/v1/admins/ancestor_departments", content)
    return dct


def ymj_department_list(department_id):
    """
    所有子department数据
    :param department_id:
    :return:
    {'status': 1, 'status_text': 'ok', 
    'data': '{"departments":[{"id":2,"name":"销售部"},{"id":3,"name":"研发部"},
    {"id":4,"name":"市场部"},{"id":9,"name":"财务部"},{"id":10,"name":"人事部ame":"风控部"},
    {"id":58,"name":"SaaS+市场部"},{"id":67,"name":"产品部"}]}'}
    """
    content = {"department_id": department_id}
    dct = post_request("/open/v1/departments/department_list", content)
    return dct


def ymj_all_parent_departmens(department_id):
    """
    所有的父department数据
    :param department_id:
    :return:
    """
    content = {"department_id": department_id}
    dct = post_request("/open/v1/departments/all_parent_departments", content)
    return dct


def ymj_find_manage_by_department(department_id):
    """
    department的负责人
    :param department_id:
    :return:{'status': 1, 'status_text': 'ok', 'data': '{}'} 找不到
    """
    content = {"department_id": department_id}
    dct = post_request("/open/v1/departments/find_manage_by_department", content)
    return dct


def ymj_department_users(department_id):
    """
    department的所有员工
    :param department_id:
    :return:
    {'status': 1, 'status_text': 'ok', 
    'data': '[{"id":19,"email":"yuanxiaowei@yimeijian.cn","name":"原小卫","mobile_number":"18515927521"},
    """
    content = {"department_id": department_id}
    dct = post_request("/open/v1/departments/find_employees_by_department", content)
    return dct
