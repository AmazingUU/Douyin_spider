import json
import os

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
        'count': '6',
        'feed_style': '0',
        'filter_warn': '0',
        'max_cursor': '0',
        'min_cursor': '0',
        'pull_type': '0',
        'type': '0',
        'volume': '0.06'
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
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    r = requests.get('https://aweme-eagle.snssdk.com/aweme/v1/feed/',params=params,headers=headers).json()
    print(r)
    aweme_list = r['aweme_list']
    return aweme_list

def download(filename,url):
    r = requests.get(url)
    stream = r.content
    save2file(filename,stream)

def save2file(filename,stream):
    base_dir = os.getcwd()
    download_dir = os.path.join(base_dir,'download')
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
    file_path = os.path.join(download_dir,filename)
    if not os.path.exists(file_path):
        with open(file_path + '.mp4','wb') as f:
            f.write(stream)

if __name__ == '__main__':
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
    video_list = get_video_list(params)
    for video in video_list:
        author = video['author']['nickname']
        video_id = video['aweme_id']
        description = video['desc']
        like_count = video['statistics']['digg_count']
        comment_count = video['statistics']['comment_count']
        share_count = video['statistics']['share_count']
        music_author = video['music']['author']
        music_title = video['music']['title']
        download_url = video['video']['play_addr']['url_list'][0]
        print('author_name:{}\tvideo_id:{}\ndesc:{}\nmusic_title:{}\tmusic_author:{}\nlike_count:{}\tcomment_count:{}\tshare_count:{}\ndownload_url:{}\n\n'.format(
            author,video_id,description,music_title,music_author,like_count,comment_count,share_count,download_url
        ))

        filename = description if description else author + video_id
        download(filename,download_url)