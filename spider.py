import json

import requests

def get_device(url):
    r = requests.get(url).json()
    device_info = r['data']
    return device_info

def get_token(url):
    r = requests.get(url).json()
    token = r['token']
    return token

def get_app_info():
    app_info = {
        'version_code':'2.7.0',
        'aid': '1128',
        'app_name': 'aweme',
        'build_number': '27014',
        'app_version': '2.7.0',
        'channel': 'App%20Stroe',
    }
    return app_info


def get_params(device_info,app_info):
    params = {
        'iid':device_info['iid'],
        'idfa':device_info['idfa'],
        'device_type': device_info['device_type'],
        'version_code':app_info['version_code'],
        'aid':app_info['aid'],
        'os_version': device_info['os_version'],
        'screen_width': device_info['screen_width'],
        'pass-region': 1,
        'vid':device_info['vid'],
        'device_id':device_info['device_id'],
        'os_api': device_info['os_api'],
        'app_name': app_info['app_name'],
        'build_number': app_info['build_number'],
        'device_platform': device_info['device_platform'],
        'js_sdk_version': '2.7.0.1',
        'app_version': app_info['app_version'],
        'ac': 'mobile',
        'openudid': device_info['openudid'],
        'channel': app_info['channel'],
        'count': '10',
        'feed_style': 0,
        'filter_warn': 0,
        'max_cursor': 0,
        'min_cursor': 0,
        'pull_type': 0,
        'type': 0,
        'volume': 0.06
    }
    return params

def params2str(params):
    query = ''
    for k, v in params.items():
        query += '%s=%s&' % (k, v)
    query = query.strip('&')
    # print(query)
    return query

def get_sign(token, query):
    r = requests.post('https://api.appsign.vip:2688/sign', json={'token': token, 'query': query}).json()
    if r['success']:
        sign = r['data']
    else:
        sign = r['success']
    return sign

def get_video_list(params):
    r = requests.get('https://aweme-eagle.snssdk.com/aweme/v1/feed/',params=params).json()
    aweme_list = r['aweme_list']
    return aweme_list

if __name__ == '__main__':
    # res = get_html('https://aweme-eagle.snssdk.com/aweme/v1/feed/?iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5,2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=mobile&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store&count=6&feed_style=0&filter_warn=0&max_cursor=0&min_cursor=0&pull_type=0&type=0&volume=0.06&mas=0161b6c4a20babcf6829e30950a9f3a577adb04abc0c6da0eeca91&as=a105e18ff4e32b1a102320&ts=1542462004')
    # res = get_html('https://xlog.snssdk.com/v2/s?os_ver=iOS%2010.3.3&os=1&app_ver=3.1.0&did=59415024289&ver=0.8.8.6-fix1&m=1&channel=App%20Store&aid=1128&region=US')
    # res = get_html('https://aweme.snssdk.com/aweme/v1/playwm/?video_id=v0200fbd0000bfo14ccps0spa6014650&line=0')
    # with open('test.txt','w',encoding='utf-8') as f:
    #     f.write(res)

    device_info = get_device('https://api.appsign.vip:2688/douyin/device/new/version/2.7.0')
    token = get_token('https://api.appsign.vip:2688/token/douyin/version/2.7.0')
    app_info = get_app_info()
    params = get_params(device_info,app_info)
    query = params2str(params)
    sign = get_sign(token,query)
    print(sign)
    params['mas'] = sign['mas']
    params['as'] = sign['as']
    params['ts'] = sign['ts']
    get_video_list(params)
