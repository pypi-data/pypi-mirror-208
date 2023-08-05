# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 17:00:55
@LastEditTime: 2023-02-16 17:49:22
@LastEditors: HuangJianYi
@Description: 基础模块
"""

from seven_cloudapp_frame.libs.common import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.db_models.marketing.marketing_program_model import *
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
#从Python SDK导入SMS配置管理模块以及安全认证模块
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
import baidubce.services.sms.sms_client as sms
import baidubce.exception as ex


class LeftNavigationHandler(ClientBaseHandler):
    """
    :description: 左侧导航栏
    """
    def get_async(self):
        """
        :description: 左侧导航栏
        :return:
        :last_editors: HuangJianYi
        """
        app_base_model = AppBaseModel(context=self)
        access_token = self.get_access_token()
        app_key, app_secret = self.get_app_key_secret()
        invoke_result_data = app_base_model.get_left_navigation(self.get_user_nick(), access_token, app_key, app_secret, self.get_app_id())
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class FriendLinkListHandler(ClientBaseHandler):
    """
    :description: 获取友情链接产品互推列表
    """
    def get_async(self):
        """
        :description: 获取友情链接产品互推列表
        :param {*}
        :return list
        :last_editors: HuangJianYi
        """
        friend_link_model = FriendLinkModel(context=self)
        friend_link_list = friend_link_model.get_cache_list(where="is_release=1")
        return self.response_json_success(friend_link_list)


class SendSmsHandler(ClientBaseHandler):
    """
    :description: 发送短信
    """
    @filter_check_params("telephone")
    def get_async(self):
        """
        :description: 发送短信
        :param thelephone：电话号码
        :param sms_type：短信渠道1-阿里 2-百度
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_open_id()
        telephone = self.get_param("telephone")
        sms_type = self.get_param_int("sms_type",2)
        result_code = str(random.randint(100000, 999999))
        if sms_type == 1:
            sms_ali_config = share_config.get_value("sms_ali_config", {"host": "", "ak": "", "secret": "", "region_id": "", "sign_name": "", "template_code": ""})
            client = AcsClient(sms_ali_config["ak"], sms_ali_config["secret"], sms_ali_config["region_id"])
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain(sms_ali_config["host"])
            request.set_method('POST')
            request.set_protocol_type('https')  # https | http
            request.set_version('2017-05-25')
            request.set_action_name('SendSms')

            request.add_query_param('RegionId', sms_ali_config["region_id"])
            request.add_query_param('PhoneNumbers', telephone)
            request.add_query_param('SignName', sms_ali_config["sign_name"])
            request.add_query_param('TemplateCode', sms_ali_config["template_code"])
            request.add_query_param('TemplateParam', "{\"code\":" + result_code + "}")
            response = client.do_action(request)
            result = dict(json.loads(response))
            result["result_code"] = result_code
            #记录验证码
            SevenHelper.redis_init().set(f"user_bind_phone_code:{open_id}", result_code, ex=300)
            return self.response_json_success()
        else:
            #设置SmsClient的Host，Access Key ID和Secret Access Key
            sms_bce_config = share_config.get_value("sms_bce_config", {"host": "", "ak": "", "sk": "", "signature_id": "", "template_id": ""})
            sms_config = BceClientConfiguration(credentials=BceCredentials(sms_bce_config["ak"], sms_bce_config["sk"]), endpoint=sms_bce_config["host"])
            #新建SmsClient
            sms_client = sms.SmsClient(sms_config)
            try:
                response = sms_client.send_message(signature_id=sms_bce_config["signature_id"], template_id=sms_bce_config["template_id"], mobile=telephone, content_var_dict={'code': result_code, 'time': '30'})
                #记录验证码
                SevenHelper.redis_init().set(f"user_bind_phone_code:{open_id}", result_code, ex=300)
                return self.response_json_success()
            except ex.BceHttpClientError as e:
                if isinstance(e.last_error, ex.BceServerError):
                    self.logger_error.error(f"发送短信失败。Response:{e.last_error.status_code},code:{e.last_error.code},request_id:{e.last_error.request_id}")
                else:
                    self.logger_error.error(f"发送短信失败。Unknown exception:{e}")
                return self.response_json_error("error","发送失败")


class MarketingProgramListHandler(ClientBaseHandler):
    """
    :description: 获取营销方案列表获取营销方案列表
    """
    def get_async(self):
        """
        :description: 获取营销方案列表
        :return: 列表
        :last_editors: HuangJianYi
        """
        marketing_program_list = MarketingProgramModel(context=self).get_cache_dict_list()
        return self.response_json_success(marketing_program_list)


class GetProductPriceHandler(ClientBaseHandler):
    """
    :description: 获取产品价格信息
    """
    def get_async(self):
        """
        :description: 获取产品价格信息
        :return 
        :last_editors: HuangJianYi
        """
        product_price_model = ProductPriceModel(context=self)
        now_date = SevenHelper.get_now_datetime()
        product_price = product_price_model.get_dict(where="%s>=begin_time and %s<=end_time and is_release=1", order_by="create_time desc", limit="1", params=[now_date, now_date])
        if not product_price:
            return self.response_json_error("error", "找不到产品价格信息")
        try:
            product_price["content"] = SevenHelper.json_loads(product_price["content"])
        except:
            return self.response_json_error("error", "产品价格信息格式有误")

        return self.reponse_json_success(product_price)
