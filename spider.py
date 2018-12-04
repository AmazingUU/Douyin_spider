"""
感谢AppSign提供加签服务
github地址：https://github.com/AppSign/douyin
"""
import datetime
import json
import os
import time
from queue import Queue
from threading import Thread

import requests

from db_helper import DbHelper


def get_device(url):  # 获取设备信息
    r = requests.get(url).json()
    device_info = r['data']
    return device_info


def get_token(url):  # 获取token信息
    r = requests.get(url).json()
    token = r['token']
    return token


def get_app_info():  # 初始化app信息
    app_info = {
        'version_code': '2.7.0',
        'aid': '1128',
        'app_name': 'aweme',
        'build_number': '27014',
        'app_version': '2.7.0',
        'channel': 'App%20Stroe',
    }
    return app_info


def get_common_params(device_info, app_info):  # 拼接视频接口和评论接口url中共同需要的参数
    params = {
        'iid': device_info['iid'],
        'idfa': device_info['idfa'],
        'device_type': device_info['device_type'],
        'version_code': app_info['version_code'],
        'aid': app_info['aid'],
        'os_version': device_info['os_version'],
        'screen_width': device_info['screen_width'],
        'pass-region': 1,
        'vid': device_info['vid'],
        'device_id': device_info['device_id'],
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


def get_video_params(params):  # 拼接视频接口url中剩下的参数
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


def get_comment_params(params, video_id):  # 拼接评论接口url中剩下的参数
    params.update({
        'aweme_id': video_id,
        'count': '10',
        'cursor': '0',
        'insert_ids': '',
    })
    return params


def params2str(params):  # 参数转化成url中需要拼接的字符串
    query = ''
    for k, v in params.items():
        query += '%s=%s&' % (k, v)
    query = query.strip('&')
    # print(query)
    return query


def get_sign(token, query):  # 调用接口获取加密签名，该签名拼接在url参数中组成完整的接口请求参数
    r = requests.post('https://api.appsign.vip:2688/sign', json={'token': token, 'query': query}).json()
    if r['success']:
        sign = r['data']
    else:
        sign = r['success']
    return sign


def get_video_info(params):  # 获取视频相关数据
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    # 视频接口url样例：https://aweme-eagle.snssdk.com/aweme/v1/feed/?iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5,2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=mobile&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store&count=6&feed_style=0&filter_warn=0&max_cursor=0&min_cursor=0&pull_type=0&type=0&volume=0.06&mas=0161b6c4a20babcf6829e30950a9f3a577adb04abc0c6da0eeca91&as=a105e18ff4e32b1a102320&ts=1542462004
    # 返回视频相关信息的JSON，视频相关数据在aweme_list里
    r = requests.get('https://aweme-eagle.snssdk.com/aweme/v1/feed/', params=params, headers=headers).json()
    video_list = r['aweme_list']
    for video in video_list:  # 共6个video
        data = {}
        data['author'] = video['author']['nickname']  # 视频作者
        data['video_id'] = video['aweme_id']  # 视频id
        data['description'] = video['desc']  # 描述
        data['like_count'] = video['statistics']['digg_count']  # 点赞数
        data['comment_count'] = video['statistics']['comment_count']  # 评论数
        data['share_count'] = video['statistics']['share_count']  # 分享数
        data['music_author'] = video['music']['author']  # 背景音乐作者
        data['music_title'] = video['music']['title']  # 背景音乐名称
        data['download_url'] = video['video']['play_addr']['url_list'][0]  # 无水印视频播放地址
        print('{}\tget video_id:{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                           data['video_id']))
        # 下载保存的文件名称
        data['filename'] = data['description'] if data['description'] else data['author'] + '_' + data['video_id']
        yield data


def get_comment_info(params):  # 获取评论相关数据
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    # 评论接口样例：https://aweme.snssdk.com/aweme/v2/comment/list/?iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5,2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=WIFI&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store&aweme_id=6624665048084122888&count=20&cursor=0&insert_ids=&mas=01198234838414691343a02f57be4c745b5a7406c5ebf53dbcd6a8&as=a195301fa2978b61f50218&ts=1542783346
    # 返回评论相关信息的JSON，评论相关数据在comments里
    r = requests.get('https://aweme.snssdk.com/aweme/v2/comment/list/', params=params, headers=headers).json()
    comment_list = r['comments']
    for comment in comment_list:  # 共10个comment
        data = {}
        data['video_id'] = comment['aweme_id']  # 被评论视频id
        data['user'] = comment['user']['nickname']  # 发表人
        data['content'] = comment['text']  # 内容
        data['like_count'] = comment['digg_count']  # 点赞数
        # time = int(comment['create_time'] / 1000)
        # dateArray = datetime.datetime.fromtimestamp(time)
        data['comment_time'] = timestamp2datetime(comment['create_time'])  # 评论时间
        try:
            # 最新评论中经常有回复别人评论的情况，所以记录下被回复的用户名、内容、点赞数和评论时间
            data['beReplied_user'] = comment['reply_comment'][0]['user']['nickname']
            data['beReplied_content'] = comment['reply_comment'][0]['text']
            data['beReplied_like_count'] = comment['reply_comment'][0]['digg_count']
            data['beReplied_comment_time'] = timestamp2datetime(comment['reply_comment'][0]['create_time'])
        except:
            data['beReplied_user'] = None
            data['beReplied_content'] = None
            data['beReplied_like_count'] = None
            data['beReplied_comment_time'] = None
        print('{}\tget user:{} comment'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                                               data['user']))
        yield data


def timestamp2datetime(timestamp):  # 时间戳转日期时间格式
    time = int(timestamp)
    dateArray = datetime.datetime.fromtimestamp(time)
    return dateArray.strftime("%Y-%m-%d %H:%M:%S")


def download(filename, url):  # 下载视频
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    # 请求视频播放地址，二进制流保存到本地
    response = requests.get(url, headers=headers)
    chunk_size = 1024  # 切分视频流，一次保存视频流大小为1M，当读取到1M时保存到文件一次
    content_size = int(response.headers['content-length'])  # 视频流总大小
    if response.status_code == 200:
        print(filename + '\n文件大小:%0.2f MB' % (content_size / chunk_size / 1024))
        base_dir = os.getcwd()
        download_dir = os.path.join(base_dir, 'download')
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        file_path = os.path.join(download_dir, filename)
        size = 0
        if not os.path.exists(file_path):
            with open(file_path + '.mp4', 'wb') as f:
                for stream in response.iter_content(chunk_size=chunk_size):  # 切分视频流
                    f.write(stream)
                    size += len(stream)
                    f.flush()  # 一次write后需要flush
                    # '\r'使每一次print会覆盖前一个print信息，end=''使print不换行，如果全部保存完，print再换行
                    # 实现下载进度实时刷新，当保存到100%时，打印下一行
                    print('下载进度:%.2f%%' % float(size / content_size * 100) + '\r',
                          end='' if (size / content_size) != 1 else '\n')


def put_into_queue(params, queue):  # 获取接口返回的视频和评论数据，放进队列
    i = 0
    while i < 10000:  # 每天抓取10000个视频
        video_params = get_video_params(params)
        for video_data in get_video_info(video_params):
            i += 1
            video_data['type'] = 'video'
            queue.put_nowait(video_data)
            comment_params = get_comment_params(params, video_data['video_id'])
            for comment_data in get_comment_info(comment_params):
                comment_data['type'] = 'comment'
                queue.put_nowait(comment_data)
        time.sleep(10)  # 加密签名为github开源服务，作者要求禁止高并发请求访问公用服务器，所以降低请求频率
    data = {'type': 'finished'}  # 抓取完成标志
    queue.put_nowait(data)


def get_from_queue(queue, db):  # 获取队列里的视频和评论数据，保存到数据库和下载视频
    while True:
        try:
            data = queue.get_nowait()
            if data['type'] == 'video':
                # download(data['filename'], data['download_url']) # 1w个视频大约需要20G，因存储空间不足，暂不下载
                db.save_one_data_to_video(data)
            elif data['type'] == 'comment':
                db.save_one_data_to_comment(data)
            elif data['type'] == 'finished':  # 抓取完成后子线程退出循环
                queue.put_nowait(data)  # 告诉主线程抓取完成
                break
        except:
            print("queue is empty wait for a while")
            time.sleep(2)


if __name__ == '__main__':
    configs = {'host': '***', 'user': '***', 'password': '***', 'db': '***'}
    db = DbHelper()
    db.connenct(configs)

    device_info = get_device('https://api.appsign.vip:2688/douyin/device/new/version/2.7.0')
    token = get_token('https://api.appsign.vip:2688/token/douyin/version/2.7.0')
    app_info = get_app_info()
    params = get_common_params(device_info, app_info)
    query = params2str(params)
    sign = get_sign(token, query)
    params.update(sign)  # url参数中拼接签名
    # print(sign)

    queue = Queue()
    Thread(target=put_into_queue, args=(params, queue)).start()
    Thread(target=get_from_queue, args=(queue, db)).start()

    while True:  # 该循环是用来判断何时关闭数据库
        try:
            data = queue.get_nowait()
            if data['type'] == 'finished':
                db.close()
                break
        except:
            print('spidering...')
            time.sleep(10)
