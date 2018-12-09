# Douyin_spider
抖音视频下载

# 项目博客

# 简介
定时爬取抖音首页随机视频，保存相关视频信息和评论信息到数据库，并将视频下载到本地

# 功能

 1. 爬取抖音首页视频的作者、视频ID、描述、点赞数、评论数、分享数、下载地址、背景音乐作者和名称
 2. 爬取视频对应的评论的作者、内容、点赞数、评论时间、被回复的用户名、内容、点赞数和评论时间
 3. 保存视频到本地

# 效果图
![video][1]

![comment][2]

![download][3]

# 特别感谢
感谢 [AppSign][4] 提供免费加签服务


  [1]: https://github.com/AmazingUU/Douyin_spider/blob/master/imgs/video.png
  [2]: https://github.com/AmazingUU/Douyin_spider/blob/master/imgs/comment.png
  [3]: https://github.com/AmazingUU/Douyin_spider/blob/master/imgs/download.png
  [4]: https://github.com/AppSign/douyin


1、Fiddler抓包，手机上设置代理后，无法上网

 按照网上教程,用Fiddler抓取手机包，发现不设置代理，可以正常上网，设置了代理之后
，就上不了网了。https的请求都会失败,提示错误信息为Failure SSLHandshake: Received
 fatal alert: unknown_ca 和You may need to configure your browser or application
  to trust the Charles Root Certificate. 但是相关设置都正确:电脑上安装了Fiddler
  的根证书,并且设置了始终信任,然后手机上也安装了描述文件,一切都按正常程序走的,
  但是错误始终无法解决.
  
原因：

虽然Fiddler的根证书已经在安装列表中显示,但它是被关闭的。在iOS 10.3之前,当你
将安装一个自定义证书,iOS会默认信任,不需要进一步的设置。而iOS 10.3之后,安装新的
自定义证书默认是不受信任的。如果要信任已安装的自定义证书,需要手动打开开关以信
任证书。

解决：

设置->通用->关于本机->证书信任设置-> 找到DO_NOT_TRUST_FiddlerRoot然后信任该证书即可.

https://blog.csdn.net/mxw2552261/article/details/78645118

2、接口post参数加密
抓包分析，找到了首页视频流url：https://aweme-eagle.snssdk.com/aweme/v1/feed/
post参数如下：

其中mas、as、ts为加密参数，需要一步一步分析JS文件才能得出这三个加密参数如何生成的。
不过有万能的GitHub，在此感谢AppSign提供加签服务，
github地址：https://github.com/AppSign/douyin。参照该文档，很快可以得到三个加密
参数，和其他参数一起post给接口就可以拿到返回的视频流数据了。
同样，评论接口加密参数也是一样的，相同的办法就可以拿到评论数据了。
评论url：https://aweme.snssdk.com/aweme/v2/comment/list/
post参数如下：

3、程序终止问题
    原本打算程序放到服务器上一直跑的，想了一下由于没有使用代理池，
长时间跑可能会被封IP，而且一直跑对AppSign提供加签的服务器也有一定的
压力，最后决定每天爬取1万条视频数据。
因为我采用的是爬取和存储是分开
的线程，而且考虑到减少加签服务器的压力，爬取线程速度较慢，存储线程
速度快，并且设置两个线程的daemon=True(会随着主线程的结束而结束)。这
时候就不能通过queue.join()来控制主线程是否阻塞。因为queue的get速度比
put速度要快，这样主程序运行一段时间就会因为queue中待处理的数据为0，
从而使queue.join()放通，导致主程序结束，子线程也会随之结束，爬取视频
达不到1万条。
4、异常处理