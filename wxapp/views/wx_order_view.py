import time
from datetime import datetime, timedelta

import pytz
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from b2c.wxapp.models.wx_payment import WXPaymentOrder
from b2c.wxapp.serializers.wx_order_serializer import WXOrderSerializer
from b2c.wxapp.services import wx_order_create, wx_order_trade_state_update, wx_order_refund, \
    wx_refund_trade_state_update, wx_order_close


class WXOrderViewSet(viewsets.ModelViewSet):
    """
    微信订单
    """
    queryset = WXPaymentOrder.objects.all()
    serializer_class = WXOrderSerializer

    @action(methods=['post'], detail=False)
    def order_create_for_test(self, request):
        app_user_id = request.data['app_user_id']
        mch_user_id = request.data['mch_user_id']
        body = request.data['body']
        total_fee = request.data['total_fee']
        notify_url = request.data['notify_url']
        out_trade_no = request.data['out_trade_no']
        client_ip = request.data['client_ip']

        time_start = datetime.fromtimestamp(time.time(), tz=pytz.timezone('Asia/Shanghai'))
        time_expire = time_start + timedelta(hours=2)
        wx_order = wx_order_create(
            app_user_id=app_user_id, mch_user_id=mch_user_id, body=body, total_fee=total_fee,
            notify_url=notify_url, out_trade_no=out_trade_no,
            client_ip=client_ip, time_start=time_start, time_expire=time_expire)
        rep = {'msg': 'success', 'code': 200, 'data': ''}
        return Response(rep)

    @action(methods=['post'], detail=False)
    def order_query_for_test(self, request):
        out_trade_no = request.data['out_trade_no']
        wx_order = wx_order_trade_state_update(out_trade_no=out_trade_no)
        rep = {'msg': 'success', 'code': 200, 'data': ''}
        return Response(rep)

    @action(methods=['post'], detail=False)
    def order_close_for_test(self, request):
        out_trade_no = request.data['out_trade_no']
        wx_order = wx_order_close(out_trade_no=out_trade_no)
        rep = {'msg': 'success', 'code': 200, 'data': ''}
        return Response(rep)

    @action(methods=['post'], detail=False)
    def order_refund_for_test(self, request):
        out_trade_no = request.data['out_trade_no']
        notify_url = request.data['notify_url']
        wx_order = wx_order_refund(out_trade_no=out_trade_no, notify_url=notify_url)
        rep = {'msg': 'success', 'code': 200, 'data': ''}
        return Response(rep)

    @action(methods=['post'], detail=False)
    def order_refund_query_for_test(self, request):
        out_trade_no = request.data['out_trade_no']
        wx_order = wx_refund_trade_state_update(out_trade_no=out_trade_no)
        rep = {'msg': 'success', 'code': 200, 'data': ''}
        return Response(rep)

    @action(methods=['get'], detail=False)
    def order_notify(self, request):
        body_data = request.body
        rep = {'msg': 'success', 'code': 200, 'data': ''}
        return Response(rep)
