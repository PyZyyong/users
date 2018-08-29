import requests
import json
import logging

from b2c.wxapp.models.wx_app_review_state_type import WXAppReviewStateType

logger = logging.getLogger('django')

wx_api_base_url = 'https://api.weixin.qq.com/'

# 小程序基本信息
base_info_url = wx_api_base_url + 'cgi-bin/account/getaccountbasicinfo?access_token='
# 设置域名
modify_domain_url = wx_api_base_url + 'wxa/modify_domain?access_token='
# 设置域名
modify_domain_url = wx_api_base_url + 'wxa/modify_domain?access_token='
# 设置业务域名
web_view_domain_url = wx_api_base_url + 'wxa/setwebviewdomain?access_token='
# 模版列表
template_list_url = wx_api_base_url + 'wxa/gettemplatelist?access_token='
# 提交代码
code_commit_url = wx_api_base_url + 'wxa/commit?access_token='
# 分类列表
category_url = wx_api_base_url + 'wxa/get_category?access_token='
# 页面配置
page_url = wx_api_base_url + 'wxa/get_page?access_token='
# 提交审核
submit_url = wx_api_base_url + 'wxa/submit_audit?access_token='
# 最新一次提交审核状态
last_audit_status_url = wx_api_base_url + 'wxa/get_latest_auditstatus?access_token='
# 发布小程序
release_url = wx_api_base_url + 'wxa/release?access_token='
# 取消审核
undo_code_audit_url = wx_api_base_url + 'wxa/undocodeaudit?access_token='


def _base_request(url) -> tuple:
    """
    代小程序微信请求的基础方法
    :param url:
    :return:
    """
    base_info = requests.get(url)
    if base_info.status_code == 200:
        base_info = json.loads(base_info.text)
        logger.debug("wechat base request info : " + str(base_info))
        if int(base_info['errcode']) == 0:
            return True, base_info
        else:
            return False, base_info['errmsg']
    else:
        return False, base_info.raise_for_status()


def _base_post(url: str, payload: dict) -> tuple:
    """
    post 请求
    :param url:
    :param payload:
    :return:
    """
    logger.debug('wechat _base_post payload: ' + str(payload))
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    if response.status_code == 200:
        base_info = json.loads(response.text)
        logger.debug("wechat base request info : " + str(base_info))
        if int(base_info['errcode']) == 0:
            return True, base_info
        else:
            return False, base_info['errmsg']
    else:
        return False, response.raise_for_status()


def app_base_info(access_token: str) -> tuple:
    """
    代小程序获取授权小程序的基本信息
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1
        &id=21528465979XX32V&token=&lang=zh_CN
    :param access_token:
    :return:
    """
    url = base_info_url + access_token
    tp = _base_request(url)
    if tp[0]:
        base_info = tp[1]
        base_info_dict = dict()
        base_info_dict['principal_name'] = base_info['authorizer_info']['principal_name']
        base_info_dict['signature'] = base_info['authorizer_info']['signature']
        base_info_dict['head_image_url'] = base_info['authorizer_info']['head_img']
        return True, base_info_dict
    else:
        return tp


def modify_domain(access_token: str, action: str, requestdomain: list, wsrequestdomain: list, uploaddomain: list,
                  downloaddomain: list) -> tuple:
    """
    设置小程序服务器域名
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1
        &id=open1489138143_WPbOO&token=&lang=zh_CN
    :param access_token:
    :param action:
    :param requestdomain:
    :param wsrequestdomain:
    :param uploaddomain:
    :param downloaddomain:
    :return:
    """
    url = modify_domain_url + access_token
    domain_dict = dict()
    domain_dict['action'] = action
    if requestdomain:
        domain_dict['requestdomain'] = requestdomain
    if requestdomain:
        domain_dict['wsrequestdomain'] = wsrequestdomain
    if requestdomain:
        domain_dict['uploaddomain'] = uploaddomain
    if requestdomain:
        domain_dict['downloaddomain'] = downloaddomain
    tp = _base_post(url, domain_dict)
    if tp[0]:
        return True, 'success'
    else:
        return tp


def set_web_view_domain(access_token: str, action: str, webviewdomain: list) -> tuple:
    """
    设置小程序业务域名（仅供第三方代小程序调用）
    :param access_token:
    :param action:
    :param webviewdomain:
    :return:
    """
    url = web_view_domain_url + access_token
    domain_dict = dict()
    domain_dict['action'] = action
    if webviewdomain:
        domain_dict['webviewdomain'] = webviewdomain
    tp = _base_post(url, domain_dict)
    if tp[0]:
        return True, 'success'
    else:
        return tp


def template_list(component_access_token: str) -> tuple:
    """
    获取代码模版库中的所有小程序代码模版
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1
        &id=open1506504150_nMMh6&token=&lang=zh_CN
    :param component_access_token:代小程序component_access_token
    :return:
    {"template_list":[{"create_time":1532765838,"user_version":"1.0.1","user_desc":"体验版","template_id":0,
        "source_miniprogram_appid":"wx87459342c1b20a3c","source_miniprogram":"玖美","developer":"Quentin"}]}
    """
    url = template_list_url + component_access_token
    tp = _base_request(url)
    if tp[0]:
        result = tp[1]
        templates = result['template_list']
        return True, templates
    else:
        return tp


def commit_code(access_token: str, template_id: str, ext_json: str, user_version: str, user_desc: str) -> tuple:
    """
    为授权的小程序帐号上传小程序代码
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1
        &id=open1489140610_Uavc4&token=&lang=zh_CN
    :param access_token: 授权方access_token
    :param template_id: 代码库中的代码模版ID
    :param ext_json: 第三方(代小程序)自定义的配置
    :param user_version: 代码版本号，开发者可自定义
    :param user_desc: 代码描述，开发者可自定义
    :return:
    """
    commit_dict = dict()
    commit_dict['template_id'] = template_id
    commit_dict['ext_json'] = ext_json
    commit_dict['user_version'] = user_version
    commit_dict['user_desc'] = user_desc
    url = code_commit_url + access_token
    tp = _base_post(url, commit_dict)
    if tp[0]:
        return True, 'success'
    else:
        return tp


def app_category_list(access_token: str) -> tuple:
    """
    获取授权小程序帐号的可选类目
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1
        &id=open1489140610_Uavc4&token=&lang=zh_CN
    :param access_token:
    :return:
    """
    url = category_url + access_token
    tp = _base_request(url)
    if tp[0]:
        base_info = tp[1]
        category_list = dict()
        category_list['category_list'] = base_info['category_list']
        return True, category_list
    else:
        return tp


def app_page_config(access_token: str) -> tuple:
    """
    获取小程序的第三方提交代码的页面配置
    :param access_token:
    :return:
    """
    url = page_url + access_token
    tp = _base_request(url)
    if tp[0]:
        base_info = tp[1]
        page_list = dict()
        page_list['page_list'] = base_info['page_list']
        return True, page_list
    else:
        return tp


def submit_audit(access_token: str, category_list: list) -> tuple:
    """
    提交审核
    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1
        &id=open1489140610_Uavc4&token=&lang=zh_CN
    :param access_token:
    :param category_list:
    :return:
    """
    url = submit_url + access_token
    item_list = []
    item = dict()
    if not category_list:
        status, category_dict = app_category_list(access_token)
        if status:
            category_list = category_dict['category_list']
            # item["tag"] = "美容 整形"
            item["first_class"] = category_list[0]['first_class']
            item["second_class"] = category_list[0]['second_class']
            item["first_id"] = category_list[0]['first_id']
            item["second_id"] = category_list[0]['second_id']
            for category in category_list:
                pass
    status, page_config = app_page_config(access_token)
    if status:
        page_list = page_config['page_list']
        item["address"] = page_list[0]
        item["title"] = "首页"
        for page in page_list:
            pass
    item_list.append(item)
    tp = _base_post(url, {"item_list": item_list})
    if tp[0]:
        return True, {'auditid': tp[1]['auditid']}
    else:
        return tp


def last_audit_status(access_token: str):
    """
    查询最近一次提交审核状态
    :param access_token:
    :return:
    """
    url = last_audit_status_url + access_token
    status, result = _base_request(url)
    if status:
        status_code = result['status']
        if status_code == 0:
            return WXAppReviewStateType.SUCCESS.value, '审核通过'
        elif status_code == 2:
            return WXAppReviewStateType.PROCESSING.value, '审核中'
        else:
            return WXAppReviewStateType.FAILED.value, result['reason']
    else:
        return WXAppReviewStateType.PROCESSING.value, '请求失败'


def release(access_token: str):
    """
    发布已审核通过的小程序
    :param access_token:
    :return:
    """
    url = release_url + access_token
    status, result = _base_post(url=url, payload={})
    if status:
        return True, '发布成功'
    else:
        return False, result


def undocodeaudit(access_token: str) -> bool:
    """
    撤回审核
    :param access_token:
    :return:
    """
    url = undo_code_audit_url + access_token
    tp = _base_request(url)
    if tp[0]:
        return True
    else:
        return False
