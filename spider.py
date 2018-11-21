import datetime
import json
import os
import time
from queue import Queue
from threading import Thread

import requests

from db_helper import DbHelper


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


def get_common_params(device_info,app_info):
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
        'channel': app_info['channel']
    }
    return params

def get_video_params(params):
    params.update({
        'count': '6',
        'feed_style': '0',
        'filter_warn': '0',
        'max_cursor': '0',
        'min_cursor': '0',
        'pull_type': '0',
        'type': '0',
        'volume': '0.06'
    })
    return params

def get_comment_params(params,video_id):
    params.update({
        'aweme_id':video_id,
        'count': '10',
        'cursor': '0',
        'insert_ids': '',
    })
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

def get_video_info(params):
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    r = requests.get('https://aweme-eagle.snssdk.com/aweme/v1/feed/',params=params,headers=headers).json()
    video_list = r['aweme_list']
    for video in video_list:
        data = {}
        data['author'] = video['author']['nickname']
        data['video_id'] = video['aweme_id']
        data['description'] = video['desc']
        data['like_count'] = video['statistics']['digg_count']
        data['comment_count'] = video['statistics']['comment_count']
        data['share_count'] = video['statistics']['share_count']
        data['music_author'] = video['music']['author']
        data['music_title'] = video['music']['title']
        data['download_url'] = video['video']['play_addr']['url_list'][0]
        # print('author_name:{}\tvideo_id:{}\ndesc:{}\nmusic_title:{}\tmusic_author:{}\nlike_count:{}\tcomment_count:{}\tshare_count:{}\ndownload_url:{}\n\n'.format(
        #     author,video_id,description,music_title,music_author,like_count,comment_count,share_count,download_url
        # ))
        data['filename'] = data['description'] if data['description'] else data['author'] + '_' + data['video_id']
        yield data

def get_comment_info(params):
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    r = requests.get('https://aweme.snssdk.com/aweme/v2/comment/list/',params=params,headers=headers).json()
    # print(r)
    comment_list = r['comments']
    for comment in comment_list:
        data = {}
        data['video_id'] = comment['aweme_id']
        data['user'] = comment['user']['nickname']
        data['content'] = comment['text']
        data['like_count'] = comment['digg_count']
        # time = int(comment['create_time'] / 1000)
        # dateArray = datetime.datetime.fromtimestamp(time)
        data['comment_time'] = timestamp2datetime(comment['create_time'])
        try:
            data['beReplied_user'] = comment['reply_comment'][0]['user']['nickname']
            data['beReplied_content'] = comment['reply_comment'][0]['text']  # 最新评论中经常有回复别人评论的情况，所以记录下被回复的内容和用户名
            data['beReplied_like_count'] = comment['reply_comment'][0]['digg_count']
            data['beReplied_comment_time'] = timestamp2datetime(comment['reply_comment'][0]['create_time'])
        except:
            data['beReplied_user'] = None
            data['beReplied_content'] = None
            data['beReplied_like_count'] = None
            data['beReplied_comment_time'] = None
        yield data

def timestamp2datetime(timestamp):  # 时间戳转日期时间格式
    time = int(timestamp)
    dateArray = datetime.datetime.fromtimestamp(time)
    return dateArray.strftime("%Y-%m-%d %H:%M:%S")

def download(filename,url):
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    response = requests.get(url,headers=headers)
    # content_size = int(r.headers['content-length'])
    # print(content_size)
    # stream = r.content
    chunk_size = 1024
    content_size = int(response.headers['content-length'])
    if response.status_code == 200:
        print(filename + '\n文件大小:%0.2f MB' % (content_size / chunk_size / 1024))
        base_dir = os.getcwd()
        download_dir = os.path.join(base_dir,'download')
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        file_path = os.path.join(download_dir,filename)
        size = 0
        if not os.path.exists(file_path):
            with open(file_path + '.mp4','wb') as f:
                for stream in response.iter_content(chunk_size=chunk_size):
                    f.write(stream)
                    size += len(stream)
                    f.flush()
                    print('下载进度:%.2f%%' % float(size / content_size * 100) + '\r',end=''if (size / content_size) != 1 else '\n')

def put_into_queue(params,queue):
    while True:
        video_params = get_video_params(params)
        for video_data in get_video_info(video_params):
            video_data['type'] = 'video'
            queue.put_nowait(video_data)
            comment_params = get_comment_params(params,video_data['video_id'])
            for comment_data in get_comment_info(comment_params):
                comment_data['type'] = 'comment'
                queue.put_nowait(comment_data)
        time.sleep(10)

def get_from_queue(queue,db):
    while True:
        try:
            data = queue.get_nowait()
            if data['type'] == 'video':
                download(data['filename'],data['download_url'])
                db.save_one_data_to_video(data)
            elif data['type'] == 'comment':
                db.save_one_data_to_comment(data)
        except:
            print("queue is empty wait for a while")
            time.sleep(2)

if __name__ == '__main__':
    configs = {'host':'localhost','user':'root','password':'admin','db':'douyin'}
    db = DbHelper()
    db.connenct(configs)

    device_info = get_device('https://api.appsign.vip:2688/douyin/device/new/version/2.7.0')
    token = get_token('https://api.appsign.vip:2688/token/douyin/version/2.7.0')
    app_info = get_app_info()
    params = get_common_params(device_info,app_info)
    query = params2str(params)
    sign = get_sign(token,query)
    params.update(sign)
    # print(sign)

    queue = Queue()
    Thread(target=put_into_queue,args=(params,queue)).start()
    Thread(target=get_from_queue,args=(queue,db)).start()

    # for video in video_list:
    #     data = {}
    #     data['author'] = video['author']['nickname']
    #     data['video_id'] = video['aweme_id']
    #     data['description'] = video['desc']
    #     data['like_count'] = video['statistics']['digg_count']
    #     data['comment_count'] = video['statistics']['comment_count']
    #     data['share_count'] = video['statistics']['share_count']
    #     data['music_author'] = video['music']['author']
    #     data['music_title'] = video['music']['title']
    #     data['download_url'] = video['video']['play_addr']['url_list'][0]
    #     # print('author_name:{}\tvideo_id:{}\ndesc:{}\nmusic_title:{}\tmusic_author:{}\nlike_count:{}\tcomment_count:{}\tshare_count:{}\ndownload_url:{}\n\n'.format(
    #     #     author,video_id,description,music_title,music_author,like_count,comment_count,share_count,download_url
    #     # ))
    #     data['filename'] = data['description'] if data['description'] else data['author'] + '_' + data['video_id']
    #     download(data['filename'],data['download_url'])
    #
    #     db.save_one_data_to_video(data)
