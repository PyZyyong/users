import json

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from b2c.users.models import User, AdminUser
from b2c.users.ymj_open_center_services.ymj_api import ymj_login, ymj_department_info

User = get_user_model()


class YMJOpenCenterBackend(ModelBackend):
    """
    自定义admin登录验证
    """
    def authenticate(self, username=None, password=None, **kwargs):

        if username and password:
            login_dict = ymj_login(username, password)
            if int(login_dict['status']) == 1:
                login_data = json.loads(login_dict['data'])
                user = User.objects.filter(username=username).first()
                department_info = ymj_department_info(login_data['email'])
                department_dict = json.loads(department_info['data'])
                department = department_dict['name']
                if user:
                    if not (user.adminuser.department_description == department):
                        user.adminuser.department_description = department
                        user.save()
                    return user
                else:
                    user = AdminUser.objects.create(
                        is_active=True,
                        is_admin_user=True,
                        username=login_data['email'],
                        email=login_data['email'],
                        display_name=login_data['name'],
                        mobile_number=login_data['mobile_number'],
                        source=1,
                        department_description=department,
                        is_staff=True,
                    )
                    user.is_superuser = True
                    user.save()
                    return user
            else:
                return None
        else:
            return None


class CustomMerchantUserBackend(ModelBackend):
    """
    自定义merchant登录验证:
                        用户名、手机号或邮箱+密码 登录
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) | Q(mobile=username) | Q(email=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
