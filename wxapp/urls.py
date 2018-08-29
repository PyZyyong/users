from django.conf.urls import url
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from b2c.wxapp.views.wechat_view import AuthCallback, WeChatQrCode, AuditeCallback
from b2c.wxapp.views.wechat_view import WeChatAuthCallbackView, WeChatCurrentDetail
from b2c.wxapp.views.wechat_view import AuditAllMerchant
from b2c.wxapp.views.wechat_view import wxapp_auth_view
from b2c.wxapp.views.wx_oauth_view import WXOAuthViewSet
from b2c.wxapp.views.wx_order_view import WXOrderViewSet

router = DefaultRouter()
router.register(r'wx_auth', WXOAuthViewSet)
router.register(r'wx_order', WXOrderViewSet)

urlpatterns = [
    # url(r'^', include(router.urls)),

    path('mb/wxapps/current_detail/', WeChatCurrentDetail.as_view()),
    path('ab/proxy_wxapp/auth/', WeChatAuthCallbackView.as_view()),
    path('ab/proxy_wxapp/auth_callback/<int:merchant_id>/', AuthCallback.as_view()),
    path('ab/proxy_wxapp/events/<str:app_id>/', AuditeCallback.as_view()),
    path('mb/wxapps/current_wxa_code/', WeChatQrCode.as_view()),
    path('ab/wxapps/audit_all/', AuditAllMerchant.as_view()),
    path('ab/wxapps/auth/<int:merchant_id>/', wxapp_auth_view),
]
