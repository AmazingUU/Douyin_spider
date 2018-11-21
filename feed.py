#!/usr/bin/env python
# encoding: utf-8
import requests
from common import *
"""
下载指定短链接无水印视频到 当前目录/douyin.mp4
Host: aweme.snssdk.com
User-Agent: Aweme/2.7.0 (iPhone; iOS 9.0.1; Scale/2.00)
"""

# 获取Token       有效期60分钟
token = getToken()
# 获取新的设备信息  有效期永久
device_info = getDevice()

def getAwemeIdByShortUrl(url):
    try:
        return requests.get(url, headers=header, allow_redirects=False).headers['location'].split("/video/")[1].split("/")[0]
    except:
        return ""

aweme_id = getAwemeIdByShortUrl("http://v.douyin.com/dQxxCw/")
if aweme_id == "":
    print "短链接错误"
    exit(-1)

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
    "ac":           "WIFI"
}

postParams={
    "aweme_id": aweme_id
}

signParams = params
signParams.update(postParams)
sign = getSign(token, signParams)
params['mas'] = sign['mas']
params['as']  = sign['as']
params['ts']  = sign['ts']
print(params)

# 获取视频详情
resp = requests.get("https://aweme.snssdk.com/aweme/v1/aweme/detail/", params=params, data=postParams, headers=header).json()
print(resp)
play_addr = resp['aweme_detail']['video']['play_addr']['url_list'][0]
print u"下载地址: " + play_addr

saveFile = "douyin.mp4"
resp = requests.get(play_addr)
open(saveFile, "wb").write(resp.content)
