from django.conf.urls import include, url
from django.urls import path
from rest_framework_nested import routers

from b2c.users.views.merchant_group_view import MerchantGroupView
from b2c.users.views.merchant_view import MerchantSMSCodeObtainView, MerchantSMSCodeVerifyView
from b2c.users.views.merchant_view import (
    MerchantViewSet,
    MerchantCardView,
    MerchantAuthView)
from b2c.users.views.permissions_view import PermissionsView
from b2c.users.views.user_view import (
    UserViewSet,
    # LoginView,
    CheckPhoneView)
from b2c.users.views_fe.frontend_user_view import FrontendUserView, PersonalCenterView, WXAppShareCode
from b2c.users.views_fe.merchant_view_fe import MerchantCardFeView

router = routers.SimpleRouter()  # mb
fe_router = routers.SimpleRouter()  # fe
# ab_router = routers.SimpleRouter()  # ab

#  frontend user
fe_router.register(r'users', FrontendUserView, base_name="users")
# 个人中心
fe_router.register(r'users', PersonalCenterView, base_name="users")
# merchant
fe_router.register(r'merchants', MerchantCardFeView, base_name="merchant_card")

# permissions
router.register(r'permissions', PermissionsView, base_name="permissions")
# user
router.register(r'users', UserViewSet, base_name="users")
router.register(r'users/check_phone', CheckPhoneView, base_name="users")
user_router = routers.NestedSimpleRouter(router, r'users', lookup='users')
# merchant
router.register(r'merchants', MerchantViewSet, base_name="merchants")
router.register(r'merchants/my', MerchantAuthView, base_name="merchants")
merchant_router = routers.NestedSimpleRouter(router, r'merchants', lookup='merchants')
# merchant groups
router.register(r'groups', MerchantGroupView, base_name="groups")

urls = (
    # url(r'^mb/users/login/', LoginView.as_view()),
    url(r'^mb/merchant_cards/my', MerchantCardView.as_view()),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('mb/users/obtain_login_sms_code/', MerchantSMSCodeObtainView.as_view()),
    path('mb/users/verify_login_sms_code/', MerchantSMSCodeVerifyView.as_view()),

    url('fe/wxapps/share/', WXAppShareCode.as_view()),
    url(r'^mb/', include(router.urls)),
    url(r'^mb/', include(merchant_router.urls)),
    url(r'^mb/', include(user_router.urls)),
    url(r'^fe/', include(fe_router.urls)),

)
