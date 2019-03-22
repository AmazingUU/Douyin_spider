import datetime

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
    # 评论接口样例：https://aweme.snssdk.com/aweme/v2/comment/list/?iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5,2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=WIFI&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store&aweme_id=6624665048084122888&count=20&cursor=0&insert_ids=&mas=01198234838414691343a02f57be4c745b5a7406c5ebf53dbcd6a8&as=a195301fa2978b61f50218&ts=1542783346
    # 返回评论相关信息的JSON，评论相关数据在comments里
    try:
        # r = requests.get(comment_api,headers=headers).json()['data']
        r = requests.get(comment_api,headers=headers).json()
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
    configs = {'host': 'localhost', 'user': 'root', 'password': 'admin', 'db': 'douyin'}
    db = DbHelper()
    db.connenct(configs)