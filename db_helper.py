import time

import pymysql


class DbHelper(object):
    def __init__(self):
        self.mutex = 0  # 锁信号
        self.db = None

    def connenct(self, configs):
        try:
            self.db = pymysql.connect(
                host=configs['host'],
                user=configs['user'],
                password=configs['password'],
                db=configs['db'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print('db connect success')
            return self.db
        except Exception as e:
            print('db connect fail,error:', str(e))
            return None

    def close(self):
        if self.db:
            self.db.close()
            print('db close')

    def save_one_data_to_video(self, data):
        while self.mutex == 1:  # connetion正在被其他线程使用，需要等待
            time.sleep(1)
            print('db connect is using...')
        self.mutex = 1  # 锁定
        try:
            with self.db.cursor() as cursor:
                sql = 'insert into video(author,video_id,description,like_count,comment_count,share_count,music_author,music_title,filename,download_url,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())'
                cursor.execute(sql, (data['author'], data['video_id'], data['description'], data['like_count'],data['comment_count'], data['share_count'], data['music_author'], data['music_title'], data['filename'], data['download_url']))
                self.db.commit()
                self.mutex = 0  # 解锁
                print('{} insert into video'.format(data['video_id']))
        except Exception as e:
            print('save video_id:{} fail,error:{}'.format(data['video_id'],str(e)))

    # def save_one_data_to_keyword(self, data):
    #     while self.mutex == 1:  # connetion正在被其他线程使用，需要等待
    #         time.sleep(1)
    #         print('db connect is using...')
    #     self.mutex = 1  # 锁定
    #     try:
    #         with self.db.cursor() as cursor:
    #             sql = 'insert into keyword(keyword,pinyin,cate1,cate2,cate3,create_time) values(%s,%s,%s,%s,%s,now())'
    #             cursor.execute(sql, (data['keyword'], data['pinyin'], data['cate1'], data['cate2'], data['cate3']))
    #             self.db.commit()
    #             self.mutex = 0  # 解锁
    #             print('{}\t{}\t{}\t{}\t{} insert into keyword'.format(data['keyword'], data['pinyin'], data['cate1'],
    #                                                                   data['cate2'], data['cate3']))
    #     except Exception as e:
    #         print('save_one_data_to_keyword,error:', str(e))
    #
    # def find_all_detail(self):
    #     try:
    #         with self.db.cursor() as cursor:
    #             sql = 'select url,filename from detail limit 10'
    #             cursor.execute(sql)
    #             res = cursor.fetchall()
    #             return res
    #     except Exception as e:
    #         print('find_all_detail fail,error:', str(e))
    #         return None
