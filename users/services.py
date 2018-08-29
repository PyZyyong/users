import uuid
from datetime import datetime
from io import BytesIO
from typing import Iterator

import requests
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction

from b2c.general.exceptions import ServiceValidationError
from b2c.misc.models import Media
from b2c.misc.services import attach_media, upload_temporary_media, send_sms_code, get_sms_code, \
    delete_sms_code, update_obj_media_set, attach_media_by_uuid, verify_sms_code
from b2c.users.models import MerchantUser, Merchant, AdminUser, \
    FrontendUser, User, MerchantGroup, MerchantConfig, MerchantLegalPerson, MerchantCertificate
from b2c.users.models.frontend_user import FrontendUserGender
from b2c.users.models.merchant_card import MerchantCard
from b2c.users.models.user_sms_code_key import SMSCodeKey
from b2c.wxapp.models import WXAppUser, WXMchUser
from b2c.wxapp.services import wx_user_phone_decrypt, wx_user_info_decrypt, wx_user_login_old, wx_user_login


def obtain_merchant_user_login_sms_code(
        user_id: int,
):
    """
    生成登录验证码
    :param user_id:
    :return:
    """
    merchant_user = MerchantUser.objects.get(
        pk=user_id,
    )

    send_sms_code(
        merchant_id=merchant_user.merchant_id,
        receiver=merchant_user,
        code_key=SMSCodeKey.LOGIN.value,
        interval=SMSCodeKey.LOGIN.interval,
        content='您的登录验证码是：{code}，60秒内有效，请勿告诉其他人'
    )


def verify_merchant_user_login_sms_code(
        user_id: int,
        code: str,
        auto_delete: bool = True,
) -> bool:
    """
    验证登录验证码
    :param auto_delete: 验证成功后自动删除
    :param user_id:
    :param code:
    :return:
    """
    merchant_user = MerchantUser.objects.get(
        pk=user_id,
    )
    return verify_sms_code(
        receiver=merchant_user,
        code=code,
        code_key=SMSCodeKey.LOGIN.value,
        valid_time=SMSCodeKey.LOGIN.valid_time,
        auto_delete=auto_delete,
    )


def update_avatar_from_wx(avatar_url, frontend_user_id):
    """
    同步微信头像
    :param avatar_url:
    :param frontend_user_id:
    :return:
    """
    user = FrontendUser.objects.get(id=frontend_user_id)
    wx_filename = 'avatar.jpeg'
    resp = requests.get(avatar_url, stream=True)
    data = resp.content
    file_data = BytesIO(data)
    file_stream = InMemoryUploadedFile(
        file_data,
        None,
        wx_filename,
        'image',
        # len(data),
        None,
        None
    )
    avatar = upload_temporary_media(file_stream)
    attach_media(content_object=user, orig_file=avatar.orig_file)
    user.save()
    return user


def create_merchant_user(
        username: str,
        mobile_number: str,
        display_name: str,
        merchant_id: int,
        is_merchant_admin: bool,
        is_active: bool,
        is_admin_user: bool,
        is_merchant_user: bool,
        is_frontend_user: bool,
        email: str = None,
        notes: str = None,
        password: str = None,
) -> MerchantUser:
    """
    创建MerchantUser
    :param username: 用户名
    :param password: 密码
    :param mobile_number: 手机号
    :param email: 邮箱
    :param is_merchant_admin:
    :param display_name: 昵称 OR 姓名
    :param is_active: 是否激活
    :param is_admin_user: 是否是admin user
    :param is_merchant_user: 是否是merchant user
    :param is_frontend_user: 是否是frontend user
    :param notes: 备注
    :param merchant_id: 所属商户
    :return:
    """
    merchant = Merchant.objects.get(id=merchant_id)
    merchant_user = MerchantUser(
        username=username, mobile_number=mobile_number,
        display_name=display_name, is_admin_user=is_admin_user,
        is_frontend_user=is_frontend_user, merchant=merchant,
        is_merchant_user=is_merchant_user, notes=notes, email=email,
        is_active=is_active, is_merchant_admin=is_merchant_admin)

    if password is not None:
        merchant_user.set_password(password)
    merchant_user.clean()
    merchant_user.save()
    return merchant_user


def user_enable(
        user_id: int
) -> User:
    """
    用户启用
    :param user_id:
    :return:
    """
    user = User.objects.get(id=user_id)
    if user.is_active is False:
        user.is_active = True
        user.save()
    return user


def user_disable(
        user_id: int
) -> User:
    """
    用户禁用
    :param user_id:
    :param is_active:
    :return:
    """
    user = User.objects.get(id=user_id)
    if user.is_active is True:
        user.is_active = False
        user.save()
    return user


def update_merchant_user(
        user_id: int,
        is_active: bool,
        is_admin_user: bool,
        is_merchant_user: bool,
        is_frontend_user: bool,
        username: str = None,
        mobile_number: str = None,
        email: str = None,
        display_name: str = None,
        notes: str = None,
) -> MerchantUser:
    """
    商户用户修改
    :param user_id:
    :param username:
    :param mobile_number:
    :param email:
    :param display_name:
    :param notes:
    :param is_active:
    :param is_admin_user:
    :param is_merchant_user:
    :param is_frontend_user:
    :return:
    """
    merchant_user = MerchantUser.objects.get(id=user_id)
    if username is not None:
        merchant_user.username = username
    if mobile_number is not None:
        merchant_user.title = mobile_number
    if email is not None:
        merchant_user.email = email
    if display_name is not None:
        merchant_user.display_name = display_name
    if notes is not None:
        merchant_user.notes = notes
    if is_active is not None:
        merchant_user.is_active = is_active
    if is_admin_user is not None:
        merchant_user.is_admin_user = is_admin_user
    if is_merchant_user is not None:
        merchant_user.is_merchant_user = is_merchant_user
    if is_frontend_user is not None:
        merchant_user.is_frontend_user = is_frontend_user

    merchant_user.clean()
    merchant_user.save()

    return merchant_user


def create_admin_user(
        username: str,
        password: str,
        mobile_number: str,
        display_name: str,
        source: str,
        notes: str,
        department_description: str,
        is_admin_user: bool,
        is_merchant_user: bool,
        is_frontend_user: bool,
) -> AdminUser:
    """
    创建AdminUser
    :param username: 用户名
    :param password:
    :param mobile_number: 手机号
    :param display_name: 昵称 OR 姓名
    :param source: 用户来源
    :param department_description: 所属部门
    :param is_admin_user: 是否是admin user
    :param is_merchant_user: 是否是merchant user
    :param is_frontend_user: 是否是frontend user
    :param notes: 备注
    :return:
    """
    admin_user = AdminUser(username=username, mobile_number=mobile_number,
                           display_name=display_name, is_admin_user=is_admin_user,
                           is_frontend_user=is_frontend_user, source=source,
                           is_merchant_user=is_merchant_user, notes=notes,
                           department_description=department_description)
    admin_user.set_password(password)
    admin_user.clean()
    admin_user.save()
    return admin_user


def create_frontend_user(
        merchant_id: int,
        wx_user_id: int,
        username: str,
        is_admin_user: bool,
        is_merchant_user: bool,
        is_frontend_user: bool,
        birthday: datetime = None,
        gender: str = FrontendUserGender.UNKNOWN.value,
        mobile_number: str = None,
        display_name: str = None,
) -> FrontendUser:
    """
    创建FrontendUser
    :param username: 用户名
    :param gender:
    :param birthday:
    :param wx_user_id:
    :param merchant_id:
    :param mobile_number: 手机号
    :param display_name: 昵称 OR 姓名
    :param is_admin_user: 是否是admin user
    :param is_merchant_user: 是否是merchant user
    :param is_frontend_user: 是否是frontend user
    :return:
    """
    merchant = Merchant.objects.get(id=merchant_id)
    wx_user = WXAppUser.objects.get(id=wx_user_id)
    frontend_user = FrontendUser(
        wx_user=wx_user,
        merchant=merchant,
        username=username,
        birthday=birthday,
        mobile_number=mobile_number,
        display_name=display_name,
        is_admin_user=is_admin_user,
        gender=gender,
        is_frontend_user=is_frontend_user,
        is_merchant_user=is_merchant_user)
    frontend_user.clean()
    frontend_user.save()
    return frontend_user


def update_frontend_user(
        frontend_user_id: int,
        is_admin_user: bool,
        is_merchant_user: bool,
        is_frontend_user: bool,
        district_id: any,
        gender: int = 2,
        birthday: datetime.date = datetime(year=1995, month=7, day=15).date(),
        username: str = None,
        mobile_number: str = None,
        display_name: str = None,
) -> FrontendUser:
    """
    frontend user update
    :param frontend_user_id:
    :param username:
    :param birthday:
    :param gender:
    :param mobile_number:
    :param display_name:
    :param district_id:
    :param is_admin_user:
    :param is_merchant_user:
    :param is_frontend_user:
    :return:
    """

    frontend_user = FrontendUser.objects.get(id=frontend_user_id)
    print(frontend_user.gender)
    if birthday is not None:
        frontend_user.birthday = birthday
    if gender is not None:
        frontend_user.gender = gender
    if username is not None:
        frontend_user.username = username
    if mobile_number is not None:
        frontend_user.mobile_number = mobile_number
    if display_name is not None:
        frontend_user.display_name = display_name
    if district_id is not None:
        frontend_user.district_id = district_id
    if is_admin_user is not None:
        frontend_user.is_admin_user = is_admin_user
    if is_merchant_user is not None:
        frontend_user.is_merchant_user = is_merchant_user
    if is_frontend_user is not None:
        frontend_user.is_frontend_user = is_frontend_user

    frontend_user.clean()
    frontend_user.save()
    return frontend_user


def update_merchant_card_images(
        merchant_id: int,
        new_set: Iterator
):
    """
    更新商户卡片图片集
    :param merchant_id:
    :param new_set:
    :return:
    """
    card, _ = MerchantCard.objects.get_or_create(merchant_id=merchant_id)
    update_obj_media_set(card, old_set=card.images.all(), new_set=new_set)


@transaction.atomic
def update_merchant_card(
        merchant_id: int,
        description: str,
        contact_mobile_number: str,
        address: str,
        location_lat: float,
        location_lng: float
) -> bool:
    """
    更新商户卡的基本信息
    :param merchant_id:
    :param description:
    :param address:
    :param contact_mobile_number:
    :param location_lat:
    :param location_lng:
    :return:
    """
    card, _ = MerchantCard.objects.get_or_create(merchant_id=merchant_id)
    card.description = description
    card.location_lat = location_lat
    card.location_lng = location_lng
    card.clean()
    card.save()
    merchant = Merchant.objects.get(id=merchant_id)
    if contact_mobile_number is not None:
        merchant.contact_mobile_number = contact_mobile_number
        merchant.save()
    if address is not None:
        merchant.address = address
        merchant.save()
    return card


@transaction.atomic
def create_merchant_group(
        merchant_id: int,
        name: str,
        notes: str,
        user_id: int = None,

) -> MerchantGroup:
    """
    MerchantGroup create without permissions
    :param merchant_id:
    :param user_id:
    :param name:
    :param notes:
    :return:
    """
    merchant = Merchant.objects.get(id=merchant_id)
    merchant_group_db = MerchantGroup.objects.filter(name=name, merchant=merchant).first()
    if merchant_group_db:
        raise ServiceValidationError('角色名不可重复!')
    user = User.objects.filter(id=user_id).first()
    group = Group(
        name=f'{merchant_id}_{uuid.uuid4()}'
    )
    group.clean()
    group.save()
    print(group.name)
    merchant_group = MerchantGroup(
        group=group,
        create_user=user if user else None,
        merchant=merchant,
        notes=notes,
        name=name
    )

    merchant_group.clean()
    merchant_group.save()
    return merchant_group


@transaction.atomic
def update_merchant_group(
        merchant_group_id: int,
        name: str,
        notes: str,

) -> MerchantGroup:
    """
    MerchantGroup update without permissions
    :param merchant_group_id:
    :param name:
    :param notes:
    :return:
    """
    merchant_group = MerchantGroup.objects.get(id=merchant_group_id)
    group = Group.objects.get(merchantgroup=merchant_group)
    if name is not None:
        merchant_group.name = name
    if notes is not None:
        merchant_group.notes = notes
    merchant_group.clean()
    merchant_group.save()

    group.clean()
    group.save()
    return merchant_group


def merchant_group_del(
        merchant_group_id: int,
) -> MerchantGroup:
    """
    Merchant Group 删除
    :param merchant_group_id:
    :return:
    """
    merchant_group = MerchantGroup.objects.get(id=merchant_group_id)
    group = Group.objects.get(merchantgroup=merchant_group)
    user = User.objects.filter(groups=group)
    if user:
        raise ServiceValidationError('组中存在用户, 无法删除!')
    return group.delete()


def fe_wx_user_login_old(mch_id, user_code):
    mch_user = MerchantConfig.objects.get(merchant_id=mch_id).wx_mch_user
    wx_app_user = wx_user_login_old(mch_user.id, user_code)
    frontend_user = FrontendUser.objects.filter(wx_user=wx_app_user).first()
    if not wx_app_user:
        return None
    if frontend_user:
        return frontend_user
    else:
        frontend_user = create_frontend_user(
            username=wx_app_user.open_id,
            is_admin_user=False,
            is_merchant_user=False,
            is_frontend_user=True,
            wx_user_id=wx_app_user.id,
            merchant_id=mch_id
        )
        return frontend_user


def fe_wx_user_login(mch_id, user_code):
    mch_user = MerchantConfig.objects.get(merchant_id=mch_id).wx_mch_user
    if not mch_user:
        return None
    wx_app_user = wx_user_login(mch_user.id, user_code)
    frontend_user = FrontendUser.objects.filter(wx_user=wx_app_user).first()
    if not wx_app_user:
        return None
    if frontend_user:
        return frontend_user
    else:
        frontend_user = create_frontend_user(
            username=wx_app_user.open_id,
            is_admin_user=False,
            is_merchant_user=False,
            is_frontend_user=True,
            wx_user_id=wx_app_user.id,
            merchant_id=mch_id
        )
        return frontend_user


def frontend_user_info_decrypt(
        token,
        mch_id,
        encrypted_data,
        iv
) -> FrontendUser:
    """
    更新 FrontendUser info  解密微信数据
    :param mch_id:
    :param token:
    :param encrypted_data:
    :param iv:
    :return:
    """
    wx_mch_user = MerchantConfig.objects.get(merchant_id=mch_id).wx_mch_user
    app_user = wx_user_info_decrypt(
        token=token,
        mch_user_id=wx_mch_user.id,
        encrypted_data=encrypted_data,
        iv=iv
    )
    if not app_user:
        return None

    # 判断 是否更新 frontend user
    frontend_user = FrontendUser.objects.get(wx_user=app_user)
    if not frontend_user.is_synced_from_wx:
        user = update_frontend_user(
            frontend_user_id=frontend_user.id,
            username=app_user.open_id,
            mobile_number=app_user.phone_number,
            display_name=app_user.nick_name,
            gender=app_user.gender,
            is_admin_user=False,
            is_merchant_user=False,
            is_frontend_user=True,
            district_id=None,
            birthday=datetime(year=1995, month=7, day=15).date(),
        )
        user.synced_from_wx_at = datetime.now()
        user.is_synced_from_wx = True

        # 同步 头像
        if app_user.avatar_url:
            return update_avatar_from_wx(
                avatar_url=app_user.avatar_url,
                frontend_user_id=user.id
            )
        return user

    return frontend_user


def frontend_user_phone_decrypt(
        token,
        mch_id,
        encrypted_data,
        iv
) -> FrontendUser:
    """
    更新 创建 FrontendUser phone
    :param mch_id:
    :param token:
    :param encrypted_data:
    :param iv:
    :return:
    """
    wx_mch_user = MerchantConfig.objects.get(merchant_id=mch_id).wx_mch_user
    app_user = wx_user_phone_decrypt(
        token=token,
        mch_user_id=wx_mch_user.id,
        encrypted_data=encrypted_data,
        iv=iv
    )
    if not app_user:
        return None

    frontend_user = FrontendUser.objects.get(wx_user=app_user)
    frontend_user.mobile_number = app_user.phone_number
    frontend_user.save()
    return frontend_user


@transaction.atomic
def merchant_certificate_base_create(
        merchant_id: int,
        name: str,
        merchant_legal_person: str,
        district_province: str,
        district_city: str,
        district_area: str,
        tel_phone: str,
        address: str,
        owner: str,
        contact_email: str,
        contact: str,
        contact_mobile_number: str,
        contact_position: str,
        authenticated_state: int,

) -> Merchant:
    """
    商户信息-基本信息 更新
    :param merchant_id:
    :param name:
    :param merchant_legal_person:
    :param district_province:
    :param district_city:
    :param district_area:
    :param authenticated_state:
    :param address:
    :param owner:
    :param contact_email:
    :param contact:
    :param contact_mobile_number:
    :param tel_phone:
    :param contact_position:
    :return:
    """
    merchant = Merchant.objects.get(id=merchant_id)

    if name is not None:
        merchant.name = name
    if district_province is not None:
        merchant.district_province = district_province
    if district_city is not None:
        merchant.district_city = district_city
    if district_area is not None:
        merchant.district_area = district_area
    if address is not None:
        merchant.address = address
    if owner is not None:
        merchant.owner = owner
    if contact is not None:
        merchant.contact = contact
    if contact_mobile_number is not None:
        merchant.contact_mobile_number = contact_mobile_number
    if tel_phone is not None:
        merchant.tel_phone = tel_phone
    if contact_email is not None:
        merchant.contact_email = contact_email
    if contact_position is not None:
        merchant.contact_position = contact_position
    if authenticated_state is not None:
        merchant.authenticated_state = authenticated_state
    merchant.clean()
    merchant.save()
    # 创建 法人信息
    legal_person, is_create = MerchantLegalPerson.objects.get_or_create(merchant=merchant)
    print(legal_person, is_create)
    if merchant_legal_person is not None:
        legal_person.realname = merchant_legal_person
        legal_person.clean()
        legal_person.save()
    return merchant


def merchant_legal_person_create(
        realname: str,
        idcard_number: str,
        idcard_valid_from: datetime,
        idcard_valid_to: datetime,
        idcard_front_image: Media,
        idcard_back_image: Media,
        merchant_id: int,
) -> MerchantLegalPerson:
    """
    Merchant 法人创建
    :param realname:
    :param idcard_number:
    :param idcard_valid_from:
    :param idcard_valid_to:
    :param idcard_front_image:
    :param idcard_back_image:
    :param merchant_id:
    :return:
    """
    merchant = Merchant.objects.get(id=merchant_id)
    merchant_legal_obj = MerchantLegalPerson(
        merchant=merchant,
        realname=realname,
        idcard_number=idcard_number,
        idcard_valid_from=idcard_valid_from,
        idcard_valid_to=idcard_valid_to,
        idcard_front_image=idcard_front_image,
        idcard_back_image=idcard_back_image
    )
    return merchant_legal_obj


def update_avatar(user_id: int, uuid):
    """
    更新用户头像
    :param user_id:
    :param uuid:
    :return:
    """
    frontend_user = FrontendUser.objects.get(id=user_id)
    attach_media_by_uuid(content_object=frontend_user, media_uuid=uuid)


def update_idcard(merchant_legal_person_id: int, orig_file):
    """
    更新 法人身份证
    :param merchant_legal_person_id:
    :param orig_file:
    :return:
    """
    merchant_legal_person = MerchantLegalPerson.objects.filter(
        id=merchant_legal_person_id).first()
    attach_media_by_uuid(content_object=merchant_legal_person, media_uuid=orig_file)


def update_merchant_certificate_images(
        merchant_id: int,
        new_set: Iterator
):
    """
    更新 资质证书 图片集
    :param merchant_id:
    :param new_set:
    :return:
    """
    merchant = Merchant.objects.get(id=merchant_id)
    card, _ = MerchantCertificate.objects.get_or_create(merchant=merchant)
    update_obj_media_set(card, old_set=card.images.all(), new_set=new_set)


def get_user_joined_days(date_joined):
    now = datetime.now()
    joined_days = (now - date_joined).days
    return joined_days


def get_login_ip(request, user_id):
    """
    获取登录用户的IP
    :param request:
    :return:
    """
    user = User.objects.get(id=user_id)
    login_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if login_ip:
        last_logged_in_ip = login_ip.split(',')[0]
    else:
        last_logged_in_ip = request.META.get('REMOTE_ADDR')

    user.last_logged_in_ip = last_logged_in_ip
    user.save()
    return user


def update_merchant_config(
        merchant: Merchant,
        wx_mch_user: WXMchUser
) -> MerchantConfig:
    """
    关联商户与微信小程序商户
    :param merchant:
    :param wx_mch_user:
    :return:
    """
    config = MerchantConfig.objects.filter(merchant=merchant).first()
    if config:
        if not config.wx_mch_user:
            config.wx_mch_user = wx_mch_user
            config.save()
    else:
        config = MerchantConfig()
        config.merchant = merchant
        config.wx_mch_user = wx_mch_user
        config.save()
    return config


def get_merchant_name_code(app_id: str) -> str:
    """
    通过小程序app_id获取商户name_code
    :param app_id:
    :return:
    """
    wx_mc_user = WXMchUser.objects.get(app_id=app_id)
    merchant = MerchantConfig.objects.get(wx_mch_user=wx_mc_user).merchant
    return merchant.name_code


def cancel_authorize(app_id: str):
    """
    小程序取消授权
    :param app_id:
    :return:
    """
    wx_mc_user = WXMchUser.objects.get(app_id=app_id)
    config = MerchantConfig.objects.get(wx_mch_user=wx_mc_user)
    config.wx_mch_user = None
    config.save()