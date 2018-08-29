permission_schema = [
    {
        "name": "项目管理",
        "children": [
            {
                "name": "项目分类",
                "permissions": [
                    "mb_product_categories"
                ]
            },
            {
                "name": "项目管理",
                "permissions": [
                    "mb_all_products_list"
                ]
            },
            {
                "name": "推荐项目",
                "permissions": [
                    "mb_products_recommended"
                ]
            },
            {
                "name": "购买须知",
                "permissions": [
                    "mb_set_product_notice"
                ]
            }
        ]
    },
    {
        "name": "订单",
        "children": [
            {
                "name": "订单列表",
                "permissions": [
                    "mb_order_list"
                ]
            }
        ]
    },
    {
        "name": "活动管理",
        "children": [
            {
                "name": "优惠券",
                "permissions": [
                    "mb_coupons_operation"
                ]
            },
            {
                "name": "秒杀",
                "permissions": [
                    "mb_sales_operation"
                ]
            },
            {
                "name": "拼团",
                "permissions": [
                    "mb_groupon_operation"
                ]
            },
            {
                "name": "砍价",
                "permissions": [
                    "mb_assistance_operation"
                ]
            }
        ]
    },
    {
        "name": "数据",
        "children": [
            {
                "name": "销售统计",
                "permissions": [
                    "mb_order_stat"
                ]
            },
            {
                "name": "客户统计",
                "permissions": [
                    "mb_daily_user_stat"
                ]
            },
            {
                "name": "活动统计",
                "permissions": [
                    "mb_activity_data_stat"
                ]
            },
            {
                "name": "财务统计",
                "permissions": [
                    "mb_finance_stat"
                ]
            },
            {
                "name": "服务统计",
                "permissions": [
                    "mb_reservation_stat"
                ]
            }
        ]
    },
    {
        "name": "设置",
        "children": [
            {
                "name": "首页banner",
                "permissions": [
                    "mb_index_page_banner"
                ]
            },
            # {
            #     "name": "店铺认证",
            #     "permissions": [
            #         "mb_merchant_certificate"
            #     ]
            # },
            # {
            #     "name": "短信签名",
            #     "permissions": [
            #         "mb_set_sms_sign"
            #     ]
            # },
            {
                "name": "人员管理",
                "permissions": [
                    "mb_merchant_user_manage"
                ]
            },
            {
                "name": "首页",
                "permissions": [
                    "mb_merchant_index_page"
                ]
            },
            {
                "name": "医院品牌",
                "permissions": [
                    "mb_merchant_card"
                ]
            },
            {
                "name": "小程序授权",
                "permissions": [
                    "mb_binding_wx_applet"
                ]
            },
            {
                "name": "微信支付授权",
                "permissions": [
                    "mb_wx_pay_auth"
                ]
            },
            {
                "name": "角色管理",
                "permissions": [
                    "mb_merchant_user_set_group"
                ]
            }
        ]
    }
]
