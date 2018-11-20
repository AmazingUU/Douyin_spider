# Douyin_spider
抖音视频下载

create table if not exists video(id int primary key auto_increment,author varchar(30),video_id varchar(25),description text,like_count int(9),comment_count int(7),share_count int(8),music_author varchar(30),music_title varchar(50),filename text,download_url text,create_time datetime);

# https://cuijiahua.com/blog/2018/03/spider-5.html/comment-page-1/#comments

https://github.com/AppSign/douyin

https://aweme-eagle.snssdk.com/aweme/v1/feed/?iid=51050168070&idfa=887748FC-0DA1-4984-B87F-F2FC9AC5D14B&version_code=3.1.0&device_type=iPhone5,2&aid=1128&os_version=10.3.3&screen_width=640&pass-region=1&vid=AECABC99-0F66-4086-86BC-EC4E01B4DEA1&device_id=59415024289&os_api=18&app_name=aweme&build_number=31006&device_platform=iphone&js_sdk_version=1.3.0.1&app_version=3.1.0&ac=mobile&openudid=75a4bc255848cd7901e166e5c168b23e3e9394a8&channel=App%20Store&count=6&feed_style=0&filter_warn=0&max_cursor=0&min_cursor=0&pull_type=0&type=0&volume=0.06&mas=0161b6c4a20babcf6829e30950a9f3a577adb04abc0c6da0eeca91&as=a105e18ff4e32b1a102320&ts=1542462004

http://v6-dy.ixigua.com/video/m/220d45bedc8880b462ab90e2cbf7c050d05115fbb9e00005c41e74f2b34/?AWSAccessKeyId=qh0h9TdcEMoS2oPj7aKX&Expires=1542468786&Signature=kVNct%2F5LcqjqkGQU1BmlPiGnsSU%3D&rc=Mzk0OXMzc2Y0aTMzZ2kzM0ApQHRoaGR1KTk6Njk0MzQzMzU2NTQ0NDVvQGgzdSlAZjN1KXNyMWgxcHpAKTU0ZDIxLV5wcGAxbF8tLV8tL3NzLW8janQ6aT5BLTIuMzEtLjUvLzQuNS06I28jOmEtcSM6YGZeZF90YmJeYDUuOg%3D%3D

SSL的问题：

 

    最近iPhone系统更新到ios 10.3后,用Charles抓包竟然出现了一些问题,https的请求都会失败,提示错误信息为Failure SSLHandshake: Received fatal alert: unknown_ca 和You may need to configure your browser or application to trust the Charles Root Certificate. 然而之前任何问题都没有,并且相关设置都正确:电脑上安装了Charles的根证书,并且设置了始终信任,然后手机上也登录了http://chls.pro/ssl安装了描述文件,一切都按正常程序走的,但是错误始终无法解决.

 

原因：

    虽然charles的根证书已经在安装列表中显示,但它是被关闭的。在iOS 10.3之前,当你将安装一个自定义证书,iOS会默认信任,不需要进一步的设置。而iOS 10.3之后,安装新的自定义证书默认是不受信任的。如果要信任已安装的自定义证书,需要手动打开开关以信任证书。

 

解决：

设置->通用->关于本机->证书信任设置-> 找到charles proxy custom root certificate然后信任该证书即可.

https://blog.csdn.net/mxw2552261/article/details/78645118
