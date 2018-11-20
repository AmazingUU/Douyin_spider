#!/usr/bin/env python
# encoding: utf-8
import requests
from common import *
"""
拉取首页视频
Host: aweme.snssdk.com
User-Agent: Aweme/2.7.0 (iPhone; iOS 9.0.1; Scale/2.00)
"""

# 获取Token       有效期60分钟
token = getToken()
# 获取新的设备信息  有效期永久
device_info = getDevice()

# 拼装参数
params = {
    "iid":              device_info['iid'],
    "idfa":             device_info['idfa'],
    "vid":              device_info['vid'],
    "device_id":        device_info['device_id'],
    "openudid":         device_info['openudid'],
    "device_type":      device_info['device_type'],
    "os_version":       device_info['os_version'],
    "os_api":           device_info['os_api'],
    "screen_width":     device_info['screen_width'],
    "device_platform":  device_info['device_platform'],
    "version_code": APPINFO['version_code'],
    "channel":      APPINFO['channel'],
    "app_name":     APPINFO['app_name'],
    "build_number": APPINFO['build_number'],
    "app_version":  APPINFO['app_version'],
    "aid":          APPINFO['aid'],
    "ac":           "WIFI",
    "count":        "6",
    "feed_style":   "0",
    "filter_warn":  "0",
    "filter_warn":  "0",
    "max_cursor":   "0",
    "min_cursor":   "0",
    "pull_type":    "1",
    "type":         "0",
    "volume":       "0.00"
}

sign = getSign(token, params)
params['mas'] = sign['mas']
params['as']  = sign['as']
params['ts']  = sign['ts']
print(params)

# 拉取首页视频列表
resp = requests.get("https://aweme.snssdk.com/aweme/v1/feed/", params=params, headers=header).json()
print(resp)
