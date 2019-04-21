'''
获取抖音首页的视频相关数据
'''
import datetime
import sys
import os
import time
from queue import Queue
from threading import Thread

import requests

from db_helper import DbHelper


def params2str(params):  # 参数转化成url中需要拼接的字符串
    query = ''
    for k, v in params.items():
        query += '%s=%s&' % (k, v)
    query = query.strip('&')
    return query


# 需要自己获取代理，不获取代理也可以，但就是最开始能获取到加密url，
# 后面就会被封IP获取不到了加密url了

# 20190419更新
# 当前使用代理会报错The requested URL could not be retrieved，应该是项目作者
# 设置了屏蔽代理请求，正在寻找解决方案。
# 暂时先不使用代理
def get_proxy():
    proxies = requests.get('xxx')
    return proxies.text


def get_feed_url():  # 获取带有加密参数的url
    headers = {
        # "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)",
        'User-Agent': 'okhttp/3.8.2',
    }
    # proxies = {
    #     'http': 'http://' + get_proxy()
    # }
    feed_params = get_feed_params()
    form_data = {
        'url': 'https://aweme.snssdk.com/aweme/v1/feed/?' + params2str(feed_params)
    }
    print('未带加密参数url:', form_data)
    try:
        # 根据开源项目获取加密参数，要求提供加密之前的url
        # feed_url = \
        #     requests.post('http://jokeai.zongcaihao.com/douyin/v292/sign', proxies=proxies,data=form_data, headers=headers).json()[
        #         'url']
        # 下面是不使用代理获取feed_url，可做最开始的测试用
        feed_url = \
            requests.post('http://jokeai.zongcaihao.com/douyin/v292/sign', data=form_data, headers=headers).json()[
                'url']
        print('带有加密参数的完整url:', feed_url)
    except Exception as e:
        feed_url = None
        print('get_sign_url() error:', str(e))
    return feed_url


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
        base_dir = sys.path[0]
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


def put_into_queue(queue):  # 获取接口返回的视频数据，放进队列
    i = 0  # 抓取的视频个数
    # 测试发现获取的带有加密参数的url，利用该url请求大概50多个视频之后，返回的是video_list
    # 就为空了，应该是加密参数过期了，所以需要一个flag来判断加密参数是否过期
    flag = 0  # 加密参数是否过期
    feed_url = None
    while i < 1000:  # 每天抓取1000个左右视频，因为get_feed()一次返回6个视频数据，最后爬取的视频数不是1万整
        if flag == 0:  # 加密参数初始化或已经过期，需要重新获取url
            feed_url = get_feed_url()
            if feed_url:  # 如果为空说明代理失效
                flag = 1
            else:
                continue
        video_list = get_video_list(feed_url)
        if not video_list:  # 利用video_list是否为空，判断加密url是否过期
            flag = 0
            continue
        for video_data in get_video_info(video_list):
            if video_data['result'] == 'success':
                i += 1
                print('today video num:', i)
                video_data['type'] = 'video'
                queue.put_nowait(video_data)
            elif video_data['result'] == 'error':
                continue
        time.sleep(3)  # 降低请求频率，防止IP被封
    # data = {}
    data = {'result': 'success', 'type': 'putFinished'}  # 抓取完成标志
    queue.put_nowait(data)

def get_from_queue(queue, db):  # 获取队列里的视频数据，保存到数据库和下载视频
    while True:
        try:
            data = queue.get_nowait()
            if data['result'] == 'success':
                if data['type'] == 'video':
                    # 每天1000个视频大约2G左右，下载时注意磁盘空间
                    db.save_one_data_to_video(data)
                    download(data['filename'], data['download_url'])
                    queue.task_done()
                    # if upload2bypy(file_path):
                    #     os.remove(file_path)
                    #     print(file_path + ' removed')
                # elif data['type'] == 'comment':
                #     db.save_one_data_to_comment(data)
                elif data['type'] == 'putFinished':  # 抓取完成后子线程退出循环
                    data['type'] = 'getFinished'
                    queue.put_nowait(data)  # 告诉主线程抓取完成
                    break
        except:
            print("queue is empty wait for a while")
            time.sleep(5)


def get_feed_params():
    params = {
        'app_type': 'normal',
        'manifest_version_code': '290',
        '_rticket': '1550930244608',
        'ac': 'wifi',
        'device_id': '66294943700',
        # 'device_id':device_info['device_id'],
        'iid': '64323608375',
        # 'iid':device_info['iid'],
        'os_version': '9',
        'channel': 'wandoujia_zhiwei',
        'version_code': '290',
        'device_type': 'ONEPLUS%20A6010',
        'language': 'zh',
        # 'uuid':device_info['uuid'],
        'uuid': '869386044722596',
        'resolution': '1080*2261',
        # 'openudid':device_info['openudid'],
        # 'vid':'C2DD3A72-18E8-490e-B58A-86AD20BB8035',
        'openudid': '89ca1c64a055844d',
        'update_version_code': '2902',
        'app_name': 'aweme',
        'version_name': '2.9.0',
        'os_api': '28',
        'device_brand': 'OnePlus',
        'ssmix': 'a',
        'device_platform': 'android',
        'dpi': '420',
        'aid': '1128',
        'count': '6',
        'type': '0',
        'max_cursor': '0',
        'min_cursor': '-1',
        # 'volume':'0.06',
        'pull_type': '2',
    }
    return params


def get_video_list(feed_url):  # 获取视频相关数据
    headers = {
        # "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)",
        "User-Agent": "okhttp/3.8.2",
    }

    r = requests.get(feed_url, headers=headers).json()
    video_list = r['aweme_list']
    return video_list


def get_video_info(video_list):
    try:
        # video_list = r['aweme_list']
        # if video_list:
        for video in video_list:  # 共6个video
            data = {}
            data['result'] = 'success'
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

    except Exception as e:
        print('get_video_info() error,', str(e))
        data = {}
        data['result'] = 'error'
        yield data


if __name__ == '__main__':
    configs = {'host': '***', 'user': '***', 'password': '***', 'db': '***'}
    db = DbHelper()
    db.connenct(configs)

    queue = Queue()
    Thread(target=put_into_queue, args=(queue,), daemon=True).start()
    Thread(target=get_from_queue, args=(queue, db), daemon=True).start()

    while True:  # 该循环是用来判断何时关闭数据库
        try:
            data = queue.get_nowait()
            if data['type'] == 'getFinished':
                db.close()
                break
        except:
            print('spidering...')
            time.sleep(10)
