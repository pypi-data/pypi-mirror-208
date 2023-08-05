#!/usr/bin/env python
# -*- coding:utf-8 -*-

CORP_API_TYPE = {
        'GET_ACCESS_TOKEN'                  : ['https://qyapi.weixin.qq.com/cgi-bin/gettoken', 'GET'],   ## 获取Token
        'USER_CREATE'                       : ['https://qyapi.weixin.qq.com/cgi-bin/user/create?access_token=ACCESS_TOKEN', 'POST'],  ## 创建成员
        'USER_GET'                          : ['https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN', 'GET'],  ## 读取成员
        'USER_UPDATE'                       : ['https://qyapi.weixin.qq.com/cgi-bin/user/update?access_token=ACCESS_TOKEN', 'POST'],  ## 更新成员
        'USER_DELETE'                       : ['https://qyapi.weixin.qq.com/cgi-bin/user/delete?access_token=ACCESS_TOKEN', 'GET'],  ## 删除成员
        'USER_BATCH_DELETE'                 : ['https://qyapi.weixin.qq.com/cgi-bin/user/batchdelete?access_token=ACCESS_TOKEN', 'POST'],
        'USER_SIMPLE_LIST'                  : ['https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token=ACCESS_TOKEN', 'GET'],
        'USER_LIST'                         : ['https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=ACCESS_TOKEN', 'GET'],
        'USERID_TO_OPENID'                  : ['https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_openid?access_token=ACCESS_TOKEN', 'POST'],
        'OPENID_TO_USERID'                  : ['https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_userid?access_token=ACCESS_TOKEN', 'POST'],
        'USER_AUTH_SUCCESS'                 : ['https://qyapi.weixin.qq.com/cgi-bin/user/authsucc?access_token=ACCESS_TOKEN', 'GET'],
        'DEPARTMENT_CREATE'                 : ['https://qyapi.weixin.qq.com/cgi-bin/department/create?access_token=ACCESS_TOKEN', 'POST'],
        'DEPARTMENT_UPDATE'                 : ['https://qyapi.weixin.qq.com/cgi-bin/department/update?access_token=ACCESS_TOKEN', 'POST'],
        'DEPARTMENT_DELETE'                 : ['https://qyapi.weixin.qq.com/cgi-bin/department/delete?access_token=ACCESS_TOKEN', 'GET'],
        'DEPARTMENT_LIST'                   : ['https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=ACCESS_TOKEN', 'GET'],
        'TAG_CREATE'                        : ['https://qyapi.weixin.qq.com/cgi-bin/tag/create?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_UPDATE'                        : ['https://qyapi.weixin.qq.com/cgi-bin/tag/update?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_DELETE'                        : ['https://qyapi.weixin.qq.com/cgi-bin/tag/delete?access_token=ACCESS_TOKEN', 'GET'],
        'TAG_GET_USER'                      : ['https://qyapi.weixin.qq.com/cgi-bin/tag/get?access_token=ACCESS_TOKEN', 'GET'],
        'TAG_ADD_USER'                      : ['https://qyapi.weixin.qq.com/cgi-bin/tag/addtagusers?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_DELETE_USER'                   : ['https://qyapi.weixin.qq.com/cgi-bin/tag/deltagusers?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_GET_LIST'                      : ['https://qyapi.weixin.qq.com/cgi-bin/tag/list?access_token=ACCESS_TOKEN', 'GET'],
        'BATCH_JOB_GET_RESULT'              : ['https://qyapi.weixin.qq.com/cgi-bin/batch/getresult?access_token=ACCESS_TOKEN', 'GET'],
        'BATCH_INVITE'                      : ['https://qyapi.weixin.qq.com/cgi-bin/batch/invite?access_token=ACCESS_TOKEN', 'POST'],
        'AGENT_GET'                         : ['https://qyapi.weixin.qq.com/cgi-bin/agent/get?access_token=ACCESS_TOKEN', 'GET'],
        'AGENT_SET'                         : ['https://qyapi.weixin.qq.com/cgi-bin/agent/set?access_token=ACCESS_TOKEN', 'POST'],
        'AGENT_GET_LIST'                    : ['https://qyapi.weixin.qq.com/cgi-bin/agent/list?access_token=ACCESS_TOKEN', 'GET'],
        'MENU_CREATE'                       : ['https://qyapi.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN', 'POST'], ## TODO
        'MENU_GET'                          : ['https://qyapi.weixin.qq.com/cgi-bin/menu/get?access_token=ACCESS_TOKEN', 'GET'],
        'MENU_DELETE'                       : ['https://qyapi.weixin.qq.com/cgi-bin/menu/delete?access_token=ACCESS_TOKEN', 'GET'],
        'MESSAGE_SEND'                      : ['https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=ACCESS_TOKEN', 'POST'],
        'MESSAGE_REVOKE'                    : ['https://qyapi.weixin.qq.com/cgi-bin/message/revoke?access_token=ACCESS_TOKEN', 'POST'],
        'MEDIA_GET'                         : ['https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token=ACCESS_TOKEN', 'GET'],
        'GET_USER_INFO_BY_CODE'             : ['https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=ACCESS_TOKEN', 'GET'],
        'GET_USER_DETAIL'                   : ['https://qyapi.weixin.qq.com/cgi-bin/user/getuserdetail?access_token=ACCESS_TOKEN', 'POST'],
        'GET_TICKET'                        : ['https://qyapi.weixin.qq.com/cgi-bin/ticket/get?access_token=ACCESS_TOKEN', 'GET'],
        'GET_JSAPI_TICKET'                  : ['https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=ACCESS_TOKEN', 'GET'],
        'GET_CHECKIN_OPTION'                : ['https://qyapi.weixin.qq.com/cgi-bin/checkin/getcheckinoption?access_token=ACCESS_TOKEN', 'POST'],
        'GET_CHECKIN_DATA'                  : ['https://qyapi.weixin.qq.com/cgi-bin/checkin/getcheckindata?access_token=ACCESS_TOKEN', 'POST'],
        'GET_APPROVAL_DATA'                 : ['https://qyapi.weixin.qq.com/cgi-bin/corp/getapprovaldata?access_token=ACCESS_TOKEN', 'POST'],
        'GET_INVOICE_INFO'                  : ['https://qyapi.weixin.qq.com/cgi-bin/card/invoice/reimburse/getinvoiceinfo?access_token=ACCESS_TOKEN', 'POST'],
        'UPDATE_INVOICE_STATUS'             : ['https://qyapi.weixin.qq.com/cgi-bin/card/invoice/reimburse/updateinvoicestatus?access_token=ACCESS_TOKEN', 'POST'],
        'BATCH_UPDATE_INVOICE_STATUS'       : ['https://qyapi.weixin.qq.com/cgi-bin/card/invoice/reimburse/updatestatusbatch?access_token=ACCESS_TOKEN', 'POST'],
        'BATCH_GET_INVOICE_INFO'            : ['https://qyapi.weixin.qq.com/cgi-bin/card/invoice/reimburse/getinvoiceinfobatch?access_token=ACCESS_TOKEN', 'POST'],
        'APP_CHAT_CREATE'                   : ['https://qyapi.weixin.qq.com/cgi-bin/appchat/create?access_token=ACCESS_TOKEN', 'POST'],
        'APP_CHAT_GET'                      : ['https://qyapi.weixin.qq.com/cgi-bin/appchat/get?access_token=ACCESS_TOKEN', 'GET'],
        'APP_CHAT_UPDATE'                   : ['https://qyapi.weixin.qq.com/cgi-bin/appchat/update?access_token=ACCESS_TOKEN', 'POST'],
        'APP_CHAT_SEND'                     : ['https://qyapi.weixin.qq.com/cgi-bin/appchat/send?access_token=ACCESS_TOKEN', 'POST'],
        'MINIPROGRAM_CODE_TO_SESSION_KEY'   : ['https://qyapi.weixin.qq.com/cgi-bin/miniprogram/jscode2session?access_token=ACCESS_TOKEN', 'GET'],
        'APPROVAL_DETAIL'                   : ['https://qyapi.weixin.qq.com/cgi-bin/oa/getapprovaldetail?access_token=ACCESS_TOKEN', 'POST'],
}
