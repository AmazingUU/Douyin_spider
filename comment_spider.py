'''
从数据库读取video_id，获取相应抖音视频的评论数据
'''
import datetime
import time

import requests

from db_helper import DbHelper


def timestamp2datetime(timestamp):  # 时间戳转日期时间格式
    time = int(timestamp)
    dateArray = datetime.datetime.fromtimestamp(time)
    return dateArray.strftime("%Y-%m-%d %H:%M:%S")


def get_comment(comment_api):  # 获取评论相关数据
    headers = {
        "User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"
    }
    # 返回评论相关信息的JSON，评论相关数据在comments里
    try:
        r = requests.get(comment_api, headers=headers).json()['data']
        # r = requests.get(comment_api,headers=headers).json()
        comment_list = r['comments']
        for comment in comment_list:  # 共10个comment
            data = {}
            data['result'] = 'success'
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
    except Exception as e:
        print('get_comment_info() error,', str(e))
        data = {}
        data['result'] = 'error'
        yield data


if __name__ == '__main__':
    configs = {'host': '***', 'user': '***', 'password': '***', 'db': '***'}
    db = DbHelper()
    db.connenct(configs)

    video_id_list = db.find_today_video()
    for video_id in video_id_list:
        comment_api = 'https://jokeai.zongcaihao.com/douyin/v292/comment/list?aweme_id={}&cursor=0'.format(
            video_id['video_id'])
        print(comment_api)
        for comment_data in get_comment(comment_api):
            if comment_data['result'] == 'success':
                db.save_one_data_to_comment(comment_data)
            elif comment_data['result'] == 'error':
                continue
