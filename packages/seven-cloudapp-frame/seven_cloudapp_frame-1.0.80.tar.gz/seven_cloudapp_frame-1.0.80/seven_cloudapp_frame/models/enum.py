# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-06-02 14:32:40
@LastEditTime: 2023-05-06 10:46:35
@LastEditors: HuangJianYi
:description: 枚举类
"""

from enum import Enum
from enum import unique

@unique
class TaskCompleteType(Enum):
    """
    :description: 任务完成类型
    """
    day = 1 #每日任务
    week = 2 #每周任务
    month = 4 #每月任务
    long = 3 #持久任务

@unique
class PlatType(Enum):
    """
    :description: 平台类型
    """
    tb = 1 #淘宝
    wx = 2 #微信
    dy = 3 #抖音
    web = 4 #站点
    jd = 5 #京东

@unique
class PageCountMode(Enum):
    """
    :description: 分页模式
    """
    none = 0 #无
    total = 1 #总数
    next = 2 #是否有下一页

@unique
class OperationType(Enum):
    """
    :description: 用户操作日志类型
    """
    add = 1 #新增
    update = 2 #编辑
    delete = 3 #删除
    review = 4 #还原
    copy = 5 #复制
    export = 6 #导出
    import_data = 7 #导入
    release = 8 #上架
    un_release = 9 #下架
    operate = 10 #操作

@unique
class TaskType(Enum):
    """
    docstring：任务类型 业务的自定义任务类型从201起
    """
    # 掌柜有礼、免费领取、新人有礼，格式：{"reward_value":0,"asset_object_id":""}  字段说明：reward_value:奖励值 asset_object_id:资产对象标识
    free_gift = 1
    # 单次签到，格式：{"reward_value":0,"asset_object_id":""}  字段说明：reward_value:奖励值 asset_object_id:资产对象标识
    one_sign = 2
    # 每周签到(指定天数签到)，格式：{"day_list":[{'day': 1, 'reward_value': 1}, {'day': 2, 'reward_value': 1}, {'day': 3, 'reward_value': 1}, {'day': 4, 'reward_value': 1}, {'day': 5, 'reward_value': 1}, {'day': 6, 'reward_value': 1}, {'day': 7, 'reward_value': 1}],"asset_object_id":""}  字段说明：day_array:每天奖励配置列表 asset_object_id:资产对象标识
    weekly_sign = 3
    # 邀请新用户，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    invite_new_user = 4
    # 邀请入会，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""}  字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    invite_join_member = 5
    # 关注店铺，格式：{"reward_value":0,"once_favor_reward":0,"asset_object_id":""} 字段说明：reward_value:奖励值 once_favor_reward:已关注是否奖励1是0否 asset_object_id:资产对象标识
    favor_store = 6
    # 加入店铺会员，格式：{"reward_value":0,"once_member_reward":0,"asset_object_id":""} 字段说明：reward_value:奖励值 once_member_reward:已入会是否奖励1是0否 asset_object_id:资产对象标识
    join_member = 7
    # 收藏商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 asset_object_id:资产对象标识 limit_num:完成限制数 goods_ids:商品ID串 goods_list:商品列表
    collect_goods = 8
    # 浏览商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 asset_object_id:资产对象标识 limit_num:完成限制数 goods_ids:商品ID串 goods_list:商品列表
    browse_goods = 9
    # 浏览店铺(进店逛逛)，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""} 或者 [{"id":1,"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""}] 字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    browse_store = 10
    # 浏览直播间(观看直播间)，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"link_url":"","asset_object_id":""} 或者 [{"id":1,"reward_value":0,"satisfy_num":1,"limit_num":0,"link_url":"","asset_object_id":""}] 字段说明：reward_value:奖励值 link_url:链接地址 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    browse_live_room = 11
    # 浏览会场/专题，格式：[{"id":"","reward_value":0,"link_url":"","satisfy_num":1,"limit_num":1,"asset_object_id":""}] 字段说明：id:子任务类型,必填 reward_value:奖励值 satisfy_num:满足数  link_url:链接地址 asset_object_id:资产对象标识 limit_num:完成限制数
    browse_special_topic = 12
    # 累计签到，格式：{"day_list":[{'day': 1, 'reward_value': 1}, {'day': 2, 'reward_value': 1}],"asset_object_id":"","is_loop":1} 字段说明： day_list:每天奖励配置列表 asset_object_id:资产对象标识 is_loop:是否循环1是0否
    cumulative_sign = 13
    # 分享，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    share = 14
    # 邀请用户助力(不判断是否新用户，可重复邀请)，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 limit_num:完成限制数 asset_object_id:资产对象标识
    invite_user_help = 15
    # 神秘暗号，格式：{"reward_value":0,"secret_code":"","asset_object_id":""} 字段说明：reward_value:奖励值 secret_code:暗号 asset_object_id:资产对象标识
    secret_code = 16
    # 店铺会员积分兑换资产，格式：{"reward_value":1,"satisfy_num":1,"limit_num":1} 字段说明：reward_value:奖励值 satisfy_num:需要的积分 limit_num:完成限制数
    crm_point_exchange_asset = 17
    # 连续签到（天数是连续递增），格式：{"day_list":[{'day': 1, 'reward_value': 1}, {'day': 2, 'reward_value': 1}],"asset_object_id":""} 字段说明： day_list:每天奖励配置列表 asset_object_id:资产对象标识
    successive_sign = 18
    # 购买指定商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],"asset_object_id":""} 字段说明：reward_value:奖励值 satisfy_num:满足数 asset_object_id:资产对象标识 limit_num:完成限制数 goods_ids:商品ID串 goods_list:商品列表
    buy_appoint_goods = 19
