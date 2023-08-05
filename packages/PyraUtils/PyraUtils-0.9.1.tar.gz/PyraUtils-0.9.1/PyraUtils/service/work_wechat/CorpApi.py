# -*- coding: utf-8 -*-
from .AbstractApi import AbstractApi
from .CorpApiType import *


class CorpApi(AbstractApi) :
    def __init__(self, corpid, corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.access_token = None

    def refreshAccessToken(self) :
        parms = dict(
            corpid=self.corpid,
            corpsecret=self.corpsecret,
        )
        response = self.httpCall(CORP_API_TYPE['GET_ACCESS_TOKEN'], parms)
        self.access_token = response.get('access_token')

    def getAccessToken(self) :
        if self.access_token is None:
            self.refreshAccessToken()
        return self.access_token


    def get_user_detail(self, access_token, userid):
        """
        功能： 读取成员。https://work.weixin.qq.com/api/doc/90000/90135/90196
        """
        params = dict(
            access_token=access_token,
            userid=userid
        )

        response = self.httpCall(CORP_API_TYPE['USER_GET'], params)
        return response

    def get_approval_detail(self, access_token, sp_no):
        """
        功能： 企业可通过审批应用或自建应用Secret调用本接口，根据审批单号查询企业微信“审批应用”的审批申请详情。。
        """

        params = dict(
            access_token=access_token
        )

        body = dict(
            sp_no=sp_no
        )

        response = self.httpCall(CORP_API_TYPE['APPROVAL_DETAIL'], params, req_body=body)
        return response

    def sendMessage(self, access_token, touser, agentid,  msgtype="text", safe=0, **kwargs):
        """消息发送"""
        params = dict(
            access_token=access_token
        )

        if msgtype == "text":
            msg_data = {
                "content": kwargs["msg_content"]
            }
            body = dict(
                touser=touser,
                msgtype=msgtype,
                agentid=agentid,
                safe=safe,
                text=msg_data,
                enable_duplicate_check=0,
                duplicate_check_interval=1800
            )
        elif msgtype == "markdown":
            msg_data = {
                "content": kwargs["msg_content"]
            }
            body = dict(
                touser=touser,
                msgtype=msgtype,
                agentid=agentid,
                safe=safe,
                markdown=msg_data,
                enable_duplicate_check=0,
                duplicate_check_interval=1800
            )
        elif msgtype == "textcard":
            msg_data = {
                "title" :  kwargs["msg_title"],
                "description" : kwargs["msg_content"],
                "url" : kwargs["msg_url"],
                "btntxt":"详情"
            }
            body = dict(
                touser=touser,
                msgtype=msgtype,
                agentid=agentid,
                textcard=msg_data,
                enable_duplicate_check=0,
                duplicate_check_interval=1800
            )
        elif msgtype == "template_card":
            pass
        response = self.httpCall(CORP_API_TYPE['MESSAGE_SEND'], params, req_body=body)
        return response

